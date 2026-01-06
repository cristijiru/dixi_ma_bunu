use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

/// Dictionary entry as stored in the database
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct DictionaryEntry {
    pub id: Uuid,
    pub headword: String,
    pub pronunciation: Option<String>,
    pub part_of_speech: Option<String>,
    pub inflections: Option<String>,
    pub definition: Option<String>,
    pub translation_ro: Option<String>,
    pub translation_en: Option<String>,
    pub translation_fr: Option<String>,
    pub etymology: Option<String>,
    pub examples: Vec<String>,
    pub expressions: Vec<String>,
    pub related_terms: Vec<String>,
    pub context: Option<String>,
    pub source: Option<String>,
    pub source_url: Option<String>,
}

/// Entry for JSON import from scraper
#[derive(Debug, Clone, Deserialize)]
pub struct ImportEntry {
    pub headword: String,
    pub pronunciation: Option<String>,
    pub part_of_speech: Option<String>,
    pub inflections: Option<String>,
    pub definition: Option<String>,
    pub translation_ro: Option<String>,
    pub translation_en: Option<String>,
    pub translation_fr: Option<String>,
    pub etymology: Option<String>,
    #[serde(default)]
    pub examples: Vec<String>,
    #[serde(default)]
    pub expressions: Vec<String>,
    #[serde(default)]
    pub related_terms: Vec<String>,
    pub context: Option<String>,
    pub source: Option<String>,
    pub source_url: Option<String>,
}

/// Search result with relevance score
#[derive(Debug, Clone, Serialize)]
pub struct SearchResult {
    pub entry: DictionaryEntry,
    pub score: f32,
    pub match_type: MatchType,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum MatchType {
    Exact,
    Prefix,
    Contains,
    Fuzzy,
}

/// Query parameters for search endpoint
#[derive(Debug, Deserialize)]
pub struct SearchQuery {
    pub q: String,
    pub lang: Option<String>,
    pub pos: Option<String>,
    pub limit: Option<i64>,
}

/// Query parameters for suggestions endpoint
#[derive(Debug, Deserialize)]
pub struct SuggestionQuery {
    pub q: String,
    pub limit: Option<i64>,
}

/// Query parameters for letter browsing
#[derive(Debug, Deserialize)]
pub struct LetterQuery {
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

/// Suggestion item for autocomplete
#[derive(Debug, Serialize, FromRow)]
pub struct Suggestion {
    pub headword: String,
    pub part_of_speech: Option<String>,
}

/// Dictionary statistics
#[derive(Debug, Serialize)]
pub struct DictionaryStats {
    pub total_entries: i64,
    pub entries_by_letter: Vec<LetterCount>,
    pub entries_by_pos: Vec<PosCount>,
}

#[derive(Debug, Serialize, FromRow)]
pub struct LetterCount {
    pub letter: String,
    pub count: i64,
}

#[derive(Debug, Serialize, FromRow)]
pub struct PosCount {
    pub part_of_speech: String,
    pub count: i64,
}

/// API response wrapper
#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub data: T,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub total: Option<i64>,
}

impl<T> ApiResponse<T> {
    pub fn new(data: T) -> Self {
        Self { data, total: None }
    }

    pub fn with_total(data: T, total: i64) -> Self {
        Self {
            data,
            total: Some(total),
        }
    }
}
