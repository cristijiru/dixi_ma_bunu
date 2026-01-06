use dixi_backend::models::*;
use uuid::Uuid;

fn sample_entry() -> DictionaryEntry {
    DictionaryEntry {
        id: Uuid::new_v4(),
        headword: "casã".to_string(),
        pronunciation: Some("ká-sə".to_string()),
        part_of_speech: Some("sf".to_string()),
        inflections: Some("casã, case".to_string()),
        definition: Some("Construcție pentru locuit".to_string()),
        translation_ro: Some("casă".to_string()),
        translation_en: Some("house".to_string()),
        translation_fr: Some("maison".to_string()),
        etymology: Some("Latin: casa".to_string()),
        examples: vec!["Casã mari".to_string()],
        expressions: vec!["acasã".to_string()],
        related_terms: vec!["cãsuțã".to_string()],
        context: None,
        source: Some("DDA".to_string()),
        source_url: None,
    }
}

#[test]
fn test_dictionary_entry_serialization() {
    let entry = sample_entry();
    let json = serde_json::to_string(&entry).unwrap();

    assert!(json.contains("casã"));
    assert!(json.contains("house"));
    assert!(json.contains("maison"));
}

#[test]
fn test_dictionary_entry_deserialization() {
    let json = r#"{
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "headword": "apã",
        "pronunciation": "á-pə",
        "part_of_speech": "sf",
        "inflections": null,
        "definition": "Lichid transparent",
        "translation_ro": "apă",
        "translation_en": "water",
        "translation_fr": "eau",
        "etymology": null,
        "examples": ["Apã aratsã"],
        "expressions": [],
        "related_terms": [],
        "context": null,
        "source": null,
        "source_url": null
    }"#;

    let entry: DictionaryEntry = serde_json::from_str(json).unwrap();

    assert_eq!(entry.headword, "apã");
    assert_eq!(entry.translation_en, Some("water".to_string()));
    assert_eq!(entry.examples.len(), 1);
}

#[test]
fn test_import_entry_with_defaults() {
    let json = r#"{
        "headword": "test"
    }"#;

    let entry: ImportEntry = serde_json::from_str(json).unwrap();

    assert_eq!(entry.headword, "test");
    assert!(entry.examples.is_empty());
    assert!(entry.expressions.is_empty());
    assert!(entry.related_terms.is_empty());
}

#[test]
fn test_import_entry_full() {
    let json = r#"{
        "headword": "casã",
        "pronunciation": "ká-sə",
        "part_of_speech": "sf",
        "translation_ro": "casă",
        "translation_en": "house",
        "translation_fr": "maison",
        "examples": ["example1", "example2"],
        "expressions": ["expr1"],
        "related_terms": ["term1", "term2"]
    }"#;

    let entry: ImportEntry = serde_json::from_str(json).unwrap();

    assert_eq!(entry.headword, "casã");
    assert_eq!(entry.examples.len(), 2);
    assert_eq!(entry.expressions.len(), 1);
    assert_eq!(entry.related_terms.len(), 2);
}

#[test]
fn test_match_type_serialization() {
    assert_eq!(serde_json::to_string(&MatchType::Exact).unwrap(), "\"exact\"");
    assert_eq!(serde_json::to_string(&MatchType::Prefix).unwrap(), "\"prefix\"");
    assert_eq!(serde_json::to_string(&MatchType::Contains).unwrap(), "\"contains\"");
    assert_eq!(serde_json::to_string(&MatchType::Fuzzy).unwrap(), "\"fuzzy\"");
}

#[test]
fn test_search_result_serialization() {
    let result = SearchResult {
        entry: sample_entry(),
        score: 0.95,
        match_type: MatchType::Exact,
    };

    let json = serde_json::to_string(&result).unwrap();

    assert!(json.contains("\"score\":0.95"));
    assert!(json.contains("\"match_type\":\"exact\""));
    assert!(json.contains("casã"));
}

#[test]
fn test_api_response_new() {
    let response = ApiResponse::new("test data");

    assert_eq!(response.data, "test data");
    assert!(response.total.is_none());
}

#[test]
fn test_api_response_with_total() {
    let response = ApiResponse::with_total(vec![1, 2, 3], 100);

    assert_eq!(response.data.len(), 3);
    assert_eq!(response.total, Some(100));
}

#[test]
fn test_api_response_serialization_without_total() {
    let response = ApiResponse::new("data");
    let json = serde_json::to_string(&response).unwrap();

    assert!(json.contains("\"data\":\"data\""));
    assert!(!json.contains("total"));
}

#[test]
fn test_api_response_serialization_with_total() {
    let response = ApiResponse::with_total("data", 42);
    let json = serde_json::to_string(&response).unwrap();

    assert!(json.contains("\"data\":\"data\""));
    assert!(json.contains("\"total\":42"));
}

#[test]
fn test_search_query_deserialization() {
    let json = r#"{"q": "casa", "lang": "en", "pos": "sf", "limit": 10}"#;
    let query: SearchQuery = serde_json::from_str(json).unwrap();

    assert_eq!(query.q, "casa");
    assert_eq!(query.lang, Some("en".to_string()));
    assert_eq!(query.pos, Some("sf".to_string()));
    assert_eq!(query.limit, Some(10));
}

#[test]
fn test_search_query_minimal() {
    let json = r#"{"q": "test"}"#;
    let query: SearchQuery = serde_json::from_str(json).unwrap();

    assert_eq!(query.q, "test");
    assert!(query.lang.is_none());
    assert!(query.pos.is_none());
    assert!(query.limit.is_none());
}

#[test]
fn test_letter_count_serialization() {
    let count = LetterCount {
        letter: "A".to_string(),
        count: 5000,
    };
    let json = serde_json::to_string(&count).unwrap();

    assert!(json.contains("\"letter\":\"A\""));
    assert!(json.contains("\"count\":5000"));
}

#[test]
fn test_dictionary_stats_serialization() {
    let stats = DictionaryStats {
        total_entries: 50000,
        entries_by_letter: vec![
            LetterCount { letter: "A".to_string(), count: 5000 },
            LetterCount { letter: "B".to_string(), count: 3000 },
        ],
        entries_by_pos: vec![
            PosCount { part_of_speech: "sf".to_string(), count: 20000 },
        ],
    };
    let json = serde_json::to_string(&stats).unwrap();

    assert!(json.contains("\"total_entries\":50000"));
    assert!(json.contains("entries_by_letter"));
    assert!(json.contains("entries_by_pos"));
}

#[test]
fn test_suggestion_serialization() {
    let suggestion = Suggestion {
        headword: "casã".to_string(),
        part_of_speech: Some("sf".to_string()),
    };
    let json = serde_json::to_string(&suggestion).unwrap();

    assert!(json.contains("\"headword\":\"casã\""));
    assert!(json.contains("\"part_of_speech\":\"sf\""));
}
