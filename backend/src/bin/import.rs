use dixi_backend::db;
use dixi_backend::models::{GroupedEntry, ImportEntry};
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));
    dotenvy::dotenv().ok();

    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: import <path-to-jsonl-file> [--clear]");
        eprintln!("  --clear  Clear existing entries before import");
        std::process::exit(1);
    }

    let file_path = &args[1];
    let clear_first = args.iter().any(|a| a == "--clear");

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    log::info!("Connecting to database...");
    let pool = db::create_pool(&database_url).await?;

    log::info!("Initializing schema...");
    db::init_schema(&pool).await?;

    if clear_first {
        log::info!("Clearing existing entries...");
        let deleted = db::queries::clear_entries(&pool).await?;
        log::info!("Deleted {} existing entries", deleted);
    }

    log::info!("Importing from {}...", file_path);
    let path = Path::new(file_path);
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut count = 0;
    let mut errors = 0;

    for (line_num, line_result) in reader.lines().enumerate() {
        let line = match line_result {
            Ok(l) => l,
            Err(e) => {
                log::warn!("Error reading line {}: {}", line_num + 1, e);
                errors += 1;
                continue;
            }
        };

        if line.trim().is_empty() {
            continue;
        }

        // Try grouped format first, then flat format
        let entries: Vec<ImportEntry> = if let Ok(grouped) = serde_json::from_str::<GroupedEntry>(&line) {
            grouped.entries
        } else if let Ok(entry) = serde_json::from_str::<ImportEntry>(&line) {
            vec![entry]
        } else {
            log::warn!("Error parsing line {}: unrecognized format", line_num + 1);
            errors += 1;
            continue;
        };

        for entry in entries {
            match db::queries::insert_entry(&pool, &entry).await {
                Ok(_) => {
                    count += 1;
                    if count % 1000 == 0 {
                        log::info!("Imported {} entries...", count);
                    }
                }
                Err(e) => {
                    log::warn!("Error inserting entry '{}': {}", entry.headword, e);
                    errors += 1;
                }
            }
        }
    }

    log::info!(
        "Import complete: {} entries imported, {} errors",
        count,
        errors
    );

    Ok(())
}
