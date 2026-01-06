use crate::models::{DictionaryEntry, MatchType, SearchResult};
use sqlx::PgPool;

/// Perform a comprehensive search across all fields
/// Priority: exact -> prefix -> contains -> fuzzy
pub async fn search(
    pool: &PgPool,
    query: &str,
    lang: Option<&str>,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<SearchResult>, sqlx::Error> {
    let normalized_query = query.to_lowercase();
    let limit_per_type = limit / 4 + 1; // Distribute limit across match types

    let mut results: Vec<SearchResult> = Vec::new();

    // 1. Exact matches (highest priority)
    let exact = search_exact(pool, &normalized_query, lang, pos, limit_per_type).await?;
    for entry in exact {
        results.push(SearchResult {
            entry,
            score: 1.0,
            match_type: MatchType::Exact,
        });
    }

    // 2. Prefix matches
    if results.len() < limit as usize {
        let prefix =
            search_prefix(pool, &normalized_query, lang, pos, limit_per_type).await?;
        for entry in prefix {
            if !results.iter().any(|r| r.entry.id == entry.id) {
                results.push(SearchResult {
                    entry,
                    score: 0.8,
                    match_type: MatchType::Prefix,
                });
            }
        }
    }

    // 3. Contains matches
    if results.len() < limit as usize {
        let contains =
            search_contains(pool, &normalized_query, lang, pos, limit_per_type).await?;
        for entry in contains {
            if !results.iter().any(|r| r.entry.id == entry.id) {
                results.push(SearchResult {
                    entry,
                    score: 0.6,
                    match_type: MatchType::Contains,
                });
            }
        }
    }

    // 4. Fuzzy matches (lowest priority)
    if results.len() < limit as usize {
        let fuzzy = search_fuzzy(pool, &normalized_query, lang, pos, limit_per_type).await?;
        for entry in fuzzy {
            if !results.iter().any(|r| r.entry.id == entry.id) {
                results.push(SearchResult {
                    entry,
                    score: 0.4,
                    match_type: MatchType::Fuzzy,
                });
            }
        }
    }

    // Sort by score descending and limit
    results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
    results.truncate(limit as usize);

    Ok(results)
}

/// Exact match search (diacritic-insensitive)
async fn search_exact(
    pool: &PgPool,
    query: &str,
    lang: Option<&str>,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    let base_query = build_search_query(
        "headword_normalized = unaccent(LOWER($1))",
        lang,
        pos,
    );

    sqlx::query_as(&base_query)
        .bind(query)
        .bind(limit)
        .fetch_all(pool)
        .await
}

/// Prefix match search
async fn search_prefix(
    pool: &PgPool,
    query: &str,
    lang: Option<&str>,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    let base_query = build_search_query(
        "headword_normalized LIKE unaccent(LOWER($1)) || '%'",
        lang,
        pos,
    );

    sqlx::query_as(&base_query)
        .bind(query)
        .bind(limit)
        .fetch_all(pool)
        .await
}

/// Contains match search
async fn search_contains(
    pool: &PgPool,
    query: &str,
    lang: Option<&str>,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    let base_query = build_search_query(
        "headword_normalized LIKE '%' || unaccent(LOWER($1)) || '%'",
        lang,
        pos,
    );

    sqlx::query_as(&base_query)
        .bind(query)
        .bind(limit)
        .fetch_all(pool)
        .await
}

/// Fuzzy match using trigram similarity
async fn search_fuzzy(
    pool: &PgPool,
    query: &str,
    lang: Option<&str>,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    let base_query = build_search_query(
        "similarity(headword_normalized, unaccent(LOWER($1))) > 0.3",
        lang,
        pos,
    );

    sqlx::query_as(&base_query)
        .bind(query)
        .bind(limit)
        .fetch_all(pool)
        .await
}

/// Search in translation fields based on language
pub async fn search_translations(
    pool: &PgPool,
    query: &str,
    lang: &str,
    pos: Option<&str>,
    limit: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    let field = match lang {
        "ro" => "translation_ro",
        "en" => "translation_en",
        "fr" => "translation_fr",
        _ => return Ok(vec![]),
    };

    let condition = format!(
        "unaccent(LOWER(COALESCE({}, ''))) LIKE '%' || unaccent(LOWER($1)) || '%'",
        field
    );

    let base_query = build_search_query(&condition, None, pos);

    sqlx::query_as(&base_query)
        .bind(query)
        .bind(limit)
        .fetch_all(pool)
        .await
}

/// Build dynamic SQL query with optional filters
fn build_search_query(condition: &str, lang: Option<&str>, pos: Option<&str>) -> String {
    let mut query = format!(
        r#"
        SELECT id, headword, pronunciation, part_of_speech, inflections,
               definition, translation_ro, translation_en, translation_fr,
               etymology, examples, expressions, related_terms, context,
               source, source_url
        FROM entries
        WHERE {}
        "#,
        condition
    );

    // Add language-specific search if specified
    if let Some(lang) = lang {
        let lang_condition = match lang {
            "rup" => "", // Aromanian is the headword, already searched
            "ro" => " OR unaccent(LOWER(COALESCE(translation_ro, ''))) LIKE '%' || unaccent(LOWER($1)) || '%'",
            "en" => " OR unaccent(LOWER(COALESCE(translation_en, ''))) LIKE '%' || unaccent(LOWER($1)) || '%'",
            "fr" => " OR unaccent(LOWER(COALESCE(translation_fr, ''))) LIKE '%' || unaccent(LOWER($1)) || '%'",
            "all" => " OR unaccent(LOWER(COALESCE(translation_ro, ''))) LIKE '%' || unaccent(LOWER($1)) || '%' OR unaccent(LOWER(COALESCE(translation_en, ''))) LIKE '%' || unaccent(LOWER($1)) || '%' OR unaccent(LOWER(COALESCE(translation_fr, ''))) LIKE '%' || unaccent(LOWER($1)) || '%'",
            _ => "",
        };
        if !lang_condition.is_empty() {
            // Wrap the original condition and add language condition
            query = query.replace(
                &format!("WHERE {}", condition),
                &format!("WHERE ({}{})", condition, lang_condition),
            );
        }
    }

    // Add part of speech filter
    if pos.is_some() {
        query.push_str(" AND part_of_speech = '");
        query.push_str(pos.unwrap());
        query.push('\'');
    }

    query.push_str(" ORDER BY headword LIMIT $2");

    query
}
