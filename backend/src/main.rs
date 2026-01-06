use actix_cors::Cors;
use actix_web::{web, App, HttpServer};
use std::env;

mod db;
mod models;
mod routes;
mod search;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    // Load environment variables
    dotenvy::dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let host = env::var("HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port: u16 = env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    log::info!("Connecting to database...");
    let pool = db::create_pool(&database_url)
        .await
        .expect("Failed to create database pool");

    log::info!("Initializing database schema...");
    db::init_schema(&pool)
        .await
        .expect("Failed to initialize database schema");

    log::info!("Starting server at http://{}:{}", host, port);

    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .wrap(cors)
            .app_data(web::Data::new(pool.clone()))
            .configure(routes::configure)
    })
    .bind((host.as_str(), port))?
    .run()
    .await
}
