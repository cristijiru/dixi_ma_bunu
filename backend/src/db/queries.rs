use crate::models::{DictionaryEntry, ImportEntry, LetterCount, PosCount, Suggestion};
use sqlx::PgPool;
use uuid::Uuid;

/// Insert a single entry from import
pub async fn insert_entry(pool: &PgPool, entry: &ImportEntry) -> Result<Uuid, sqlx::Error> {
    let id = sqlx::query_scalar(
        r#"
        INSERT INTO entries (
            headword, headword_normalized, pronunciation, part_of_speech,
            inflections, definition, translation_ro, translation_en,
            translation_fr, etymology, examples, expressions,
            related_terms, context, source, source_url
        ) VALUES (
            $1, unaccent(LOWER($1)), $2, $3, $4, $5, $6, $7, $8, $9,
            $10, $11, $12, $13, $14, $15
        )
        RETURNING id
        "#,
    )
    .bind(&entry.headword)
    .bind(&entry.pronunciation)
    .bind(&entry.part_of_speech)
    .bind(&entry.inflections)
    .bind(&entry.definition)
    .bind(&entry.translation_ro)
    .bind(&entry.translation_en)
    .bind(&entry.translation_fr)
    .bind(&entry.etymology)
    .bind(&entry.examples)
    .bind(&entry.expressions)
    .bind(&entry.related_terms)
    .bind(&entry.context)
    .bind(&entry.source)
    .bind(&entry.source_url)
    .fetch_one(pool)
    .await?;

    Ok(id)
}

/// Get entry by ID
pub async fn get_entry_by_id(
    pool: &PgPool,
    id: Uuid,
) -> Result<Option<DictionaryEntry>, sqlx::Error> {
    sqlx::query_as(
        r#"
        SELECT id, headword, pronunciation, part_of_speech, inflections,
               definition, translation_ro, translation_en, translation_fr,
               etymology, examples, expressions, related_terms, context,
               source, source_url
        FROM entries
        WHERE id = $1
        "#,
    )
    .bind(id)
    .fetch_optional(pool)
    .await
}

/// Get a random entry for Word of the Day
pub async fn get_random_entry(pool: &PgPool) -> Result<Option<DictionaryEntry>, sqlx::Error> {
    sqlx::query_as(
        r#"
        SELECT id, headword, pronunciation, part_of_speech, inflections,
               definition, translation_ro, translation_en, translation_fr,
               etymology, examples, expressions, related_terms, context,
               source, source_url
        FROM entries
        ORDER BY RANDOM()
        LIMIT 1
        "#,
    )
    .fetch_optional(pool)
    .await
}

/// Get all available starting letters
/// Skips parenthetical prefixes like (a) to get the real first letter
pub async fn get_letters(pool: &PgPool) -> Result<Vec<LetterCount>, sqlx::Error> {
    sqlx::query_as(
        r#"
        SELECT UPPER(LEFT(REGEXP_REPLACE(headword, '^\([^)]+\)', ''), 1)) as letter,
               COUNT(*)::bigint as count
        FROM entries
        GROUP BY UPPER(LEFT(REGEXP_REPLACE(headword, '^\([^)]+\)', ''), 1))
        ORDER BY letter
        "#,
    )
    .fetch_all(pool)
    .await
}

/// Get entries by starting letter
/// Skips parenthetical prefixes like (a) to match the real first letter
pub async fn get_entries_by_letter(
    pool: &PgPool,
    letter: &str,
    limit: i64,
    offset: i64,
) -> Result<Vec<DictionaryEntry>, sqlx::Error> {
    sqlx::query_as(
        r#"
        SELECT id, headword, pronunciation, part_of_speech, inflections,
               definition, translation_ro, translation_en, translation_fr,
               etymology, examples, expressions, related_terms, context,
               source, source_url
        FROM entries
        WHERE UPPER(LEFT(REGEXP_REPLACE(headword, '^\([^)]+\)', ''), 1)) = UPPER($1)
        ORDER BY REGEXP_REPLACE(headword, '^\([^)]+\)', ''), headword
        LIMIT $2 OFFSET $3
        "#,
    )
    .bind(letter)
    .bind(limit)
    .bind(offset)
    .fetch_all(pool)
    .await
}

/// Count entries by letter
/// Skips parenthetical prefixes like (a) to match the real first letter
pub async fn count_entries_by_letter(pool: &PgPool, letter: &str) -> Result<i64, sqlx::Error> {
    sqlx::query_scalar(
        r#"
        SELECT COUNT(*)::bigint
        FROM entries
        WHERE UPPER(LEFT(REGEXP_REPLACE(headword, '^\([^)]+\)', ''), 1)) = UPPER($1)
        "#,
    )
    .bind(letter)
    .fetch_one(pool)
    .await
}

/// Get autocomplete suggestions
pub async fn get_suggestions(
    pool: &PgPool,
    query: &str,
    limit: i64,
) -> Result<Vec<Suggestion>, sqlx::Error> {
    let normalized_query = query.to_lowercase();

    sqlx::query_as(
        r#"
        SELECT DISTINCT headword, part_of_speech
        FROM entries
        WHERE headword_normalized LIKE $1 || '%'
        ORDER BY headword
        LIMIT $2
        "#,
    )
    .bind(&normalized_query)
    .bind(limit)
    .fetch_all(pool)
    .await
}

/// Get total entry count
pub async fn get_total_count(pool: &PgPool) -> Result<i64, sqlx::Error> {
    sqlx::query_scalar("SELECT COUNT(*)::bigint FROM entries")
        .fetch_one(pool)
        .await
}

/// Get entries grouped by part of speech
pub async fn get_pos_counts(pool: &PgPool) -> Result<Vec<PosCount>, sqlx::Error> {
    sqlx::query_as(
        r#"
        SELECT COALESCE(part_of_speech, 'unknown') as part_of_speech,
               COUNT(*)::bigint as count
        FROM entries
        GROUP BY part_of_speech
        ORDER BY count DESC
        "#,
    )
    .fetch_all(pool)
    .await
}

/// Clear all entries (for reimport)
pub async fn clear_entries(pool: &PgPool) -> Result<u64, sqlx::Error> {
    let result = sqlx::query("DELETE FROM entries").execute(pool).await?;
    Ok(result.rows_affected())
}
