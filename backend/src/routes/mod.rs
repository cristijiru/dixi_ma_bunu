use actix_web::{get, web, HttpResponse, Responder};
use sqlx::PgPool;
use uuid::Uuid;

use crate::db::queries;
use crate::models::{ApiResponse, DictionaryStats, LetterQuery, SearchQuery, SuggestionQuery};
use crate::search;

/// Search dictionary entries
#[get("/api/search")]
pub async fn search_entries(
    pool: web::Data<PgPool>,
    query: web::Query<SearchQuery>,
) -> impl Responder {
    let limit = query.limit.unwrap_or(20).min(100);

    match search::search(
        pool.get_ref(),
        &query.q,
        query.lang.as_deref(),
        query.pos.as_deref(),
        limit,
    )
    .await
    {
        Ok(results) => HttpResponse::Ok().json(ApiResponse::new(results)),
        Err(e) => {
            log::error!("Search error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Search failed"
            }))
        }
    }
}

/// Get entry by ID
#[get("/api/words/{id}")]
pub async fn get_word(pool: web::Data<PgPool>, path: web::Path<Uuid>) -> impl Responder {
    let id = path.into_inner();

    match queries::get_entry_by_id(pool.get_ref(), id).await {
        Ok(Some(entry)) => HttpResponse::Ok().json(ApiResponse::new(entry)),
        Ok(None) => HttpResponse::NotFound().json(serde_json::json!({
            "error": "Entry not found"
        })),
        Err(e) => {
            log::error!("Database error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database error"
            }))
        }
    }
}

/// Get random word for Word of the Day
#[get("/api/words/random")]
pub async fn random_word(pool: web::Data<PgPool>) -> impl Responder {
    match queries::get_random_entry(pool.get_ref()).await {
        Ok(Some(entry)) => HttpResponse::Ok().json(ApiResponse::new(entry)),
        Ok(None) => HttpResponse::NotFound().json(serde_json::json!({
            "error": "No entries found"
        })),
        Err(e) => {
            log::error!("Database error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database error"
            }))
        }
    }
}

/// Get all available letters
#[get("/api/letters")]
pub async fn get_letters(pool: web::Data<PgPool>) -> impl Responder {
    match queries::get_letters(pool.get_ref()).await {
        Ok(letters) => HttpResponse::Ok().json(ApiResponse::new(letters)),
        Err(e) => {
            log::error!("Database error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database error"
            }))
        }
    }
}

/// Browse entries by letter
#[get("/api/letters/{letter}")]
pub async fn get_by_letter(
    pool: web::Data<PgPool>,
    path: web::Path<String>,
    query: web::Query<LetterQuery>,
) -> impl Responder {
    let letter = path.into_inner();
    let limit = query.limit.unwrap_or(50).min(200);
    let offset = query.offset.unwrap_or(0);

    let entries_result =
        queries::get_entries_by_letter(pool.get_ref(), &letter, limit, offset).await;
    let count_result = queries::count_entries_by_letter(pool.get_ref(), &letter).await;

    match (entries_result, count_result) {
        (Ok(entries), Ok(total)) => {
            HttpResponse::Ok().json(ApiResponse::with_total(entries, total))
        }
        (Err(e), _) | (_, Err(e)) => {
            log::error!("Database error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database error"
            }))
        }
    }
}

/// Autocomplete suggestions
#[get("/api/suggestions")]
pub async fn suggestions(
    pool: web::Data<PgPool>,
    query: web::Query<SuggestionQuery>,
) -> impl Responder {
    let limit = query.limit.unwrap_or(10).min(50);

    match queries::get_suggestions(pool.get_ref(), &query.q, limit).await {
        Ok(suggestions) => HttpResponse::Ok().json(ApiResponse::new(suggestions)),
        Err(e) => {
            log::error!("Suggestions error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Suggestions failed"
            }))
        }
    }
}

/// Dictionary statistics
#[get("/api/stats")]
pub async fn stats(pool: web::Data<PgPool>) -> impl Responder {
    let total = queries::get_total_count(pool.get_ref()).await;
    let letters = queries::get_letters(pool.get_ref()).await;
    let pos = queries::get_pos_counts(pool.get_ref()).await;

    match (total, letters, pos) {
        (Ok(total_entries), Ok(entries_by_letter), Ok(entries_by_pos)) => {
            HttpResponse::Ok().json(ApiResponse::new(DictionaryStats {
                total_entries,
                entries_by_letter,
                entries_by_pos,
            }))
        }
        _ => HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "Failed to get statistics"
        })),
    }
}

/// Health check endpoint
#[get("/api/health")]
pub async fn health() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "ok"
    }))
}

/// Configure all routes
pub fn configure(cfg: &mut web::ServiceConfig) {
    cfg.service(search_entries)
        .service(random_word)
        .service(get_word)
        .service(get_letters)
        .service(get_by_letter)
        .service(suggestions)
        .service(stats)
        .service(health);
}
