use sqlx::postgres::{PgPool, PgPoolOptions};
use std::time::Duration;

pub mod queries;

/// Create database connection pool
pub async fn create_pool(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(10)
        .acquire_timeout(Duration::from_secs(3))
        .connect(database_url)
        .await
}

/// Initialize database schema
pub async fn init_schema(pool: &PgPool) -> Result<(), sqlx::Error> {
    // Create extensions
    sqlx::query("CREATE EXTENSION IF NOT EXISTS unaccent")
        .execute(pool)
        .await?;

    sqlx::query("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        .execute(pool)
        .await?;

    // Create main entries table
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            headword TEXT NOT NULL,
            headword_normalized TEXT NOT NULL,
            pronunciation TEXT,
            part_of_speech TEXT,
            inflections TEXT,
            definition TEXT,
            translation_ro TEXT,
            translation_en TEXT,
            translation_fr TEXT,
            etymology TEXT,
            examples TEXT[] DEFAULT '{}',
            expressions TEXT[] DEFAULT '{}',
            related_terms TEXT[] DEFAULT '{}',
            context TEXT,
            source TEXT,
            source_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        "#,
    )
    .execute(pool)
    .await?;

    // Create indexes for search performance
    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_headword ON entries (headword)",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_headword_normalized ON entries (headword_normalized)",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_headword_trgm ON entries USING gin (headword_normalized gin_trgm_ops)",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_pos ON entries (part_of_speech)",
    )
    .execute(pool)
    .await?;

    // Indexes for translation searches
    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_translation_ro_trgm ON entries USING gin (COALESCE(translation_ro, '') gin_trgm_ops)",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_translation_en_trgm ON entries USING gin (COALESCE(translation_en, '') gin_trgm_ops)",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_entries_translation_fr_trgm ON entries USING gin (COALESCE(translation_fr, '') gin_trgm_ops)",
    )
    .execute(pool)
    .await?;

    log::info!("Database schema initialized");
    Ok(())
}
