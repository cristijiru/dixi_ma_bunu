# Scraper Project Documentation

## Overview

This project scrapes and processes the Aromanian dictionary from dixionline.net.

## Data Structure

```
data/
├── aromanian_dictionary.jsonl    # FINAL OUTPUT - use this!
├── raw/                          # Original scraped data
│   ├── dictionary.jsonl
│   ├── dictionary.json
│   ├── dictionary.csv
│   └── scrape.log
├── merged/                       # Merged output (detailed)
│   ├── dictionary_merged.jsonl
│   └── dictionary_merged.json
└── processing/                   # Merge workflow files
    ├── merge_candidates.json
    ├── merge_decisions.json
    └── checkpoint.json
```

## Quick Start

The final dictionary is at `data/aromanian_dictionary.jsonl` (40,871 words).

## Merger System

### Scripts

| Script | Purpose |
|--------|---------|
| `merger.py` | Find and auto-merge spelling variants |
| `review_merges.py` | CLI to review merge candidates |
| `apply_merges.py` | Apply decisions, export final dataset |

### Auto-Approved Spelling Equivalences

These are automatically merged without review:

| Pattern | Example |
|---------|---------|
| ã ↔ â ↔ ă | `acasã` = `acasâ` |
| dh ↔ d | `acridhã` = `acridã` |
| gh ↔ g | `aghnanghea` = `agnanghea` |
| th ↔ t | `aculuthii` = `aculutii` |
| ch ↔ k | `acheryiu` = `akeryiu` |
| y ↔ g | `ayitã` = `aghitã` |

### Needs Manual Review

These patterns sometimes represent different words:

| Pattern | Risk | Example |
|---------|------|---------|
| nj ↔ n | HIGH | `nilushu` (ring) ≠ `njilushu` (lamb) |
| lj ↔ l | HIGH | `cãljush` (leader) ≠ `cãlush` (gag) |
| dz ↔ z | MEDIUM | `dzâpitu` (crăpet) ≠ `zâpitu` (guvernator) |
| a ↔ ã (start) | MEDIUM | `ai` (vai!) ≠ `ãi` (is) |

### Current Status

- **48,829** raw entries
- **40,871** merged word groups
- **~4,900** auto-merged spelling variants
- **1,055** candidates pending review

### Usage

```bash
# Step 1: Run auto-merge and generate review candidates
python3 merger.py

# Step 2: Review candidates interactively (optional)
python3 review_merges.py

# Step 3: Apply decisions and export final dataset
python3 apply_merges.py
```

## Data Format

### Final Dictionary Entry

```json
{
  "id": "word_000001",
  "canonical": "acasã",
  "variants": ["acasã", "acasâ"],
  "entries": [
    {
      "headword": "acasã",
      "source": "Dictionary A",
      "translation_ro": "acasă",
      "translation_en": "home"
    },
    {
      "headword": "acasâ",
      "source": "Dictionary B",
      "definition": "..."
    }
  ]
}
```

Each entry preserves its original source and all fields.

### Entry Fields

| Field | Description |
|-------|-------------|
| `headword` | The Aromanian word |
| `source` | Dictionary source |
| `translation_ro` | Romanian translation |
| `translation_en` | English translation |
| `translation_fr` | French translation |
| `definition` | Aromanian definition |
| `part_of_speech` | sf, sm, sn, vb, adg, adv |
| `examples` | Usage examples |
| `expressions` | Idiomatic expressions |
| `etymology` | Word origin |
