# Dixi Ma Bunu - Project Context

## Project Overview

Aromanian/Vlach dictionary web app with data scraped from dixionline.net.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│ PostgreSQL  │
│  React/TS   │     │  Rust/Actix │     │  + unaccent │
│  Vite       │     │             │     │  + pg_trgm  │
└─────────────┘     └─────────────┘     └─────────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │   Scraper   │
                    │   Python    │
                    └─────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind, TanStack Query |
| Backend | Rust, Actix-web, SQLx |
| Database | PostgreSQL 15+ with `unaccent` + `pg_trgm` extensions |
| Scraper | Python 3.11+, httpx, BeautifulSoup |
| Infra | Docker, Docker Compose |

## Key Implementation Details

### Search
- Diacritic-insensitive via PostgreSQL `unaccent`
- Fuzzy matching via `pg_trgm` trigram similarity
- Priority: exact > prefix > contains > fuzzy

### Data Quirks

**Parenthetical prefixes:** Some headwords start with `(a)` like `(a)fendi` meaning the `a` is optional. The backend strips these prefixes when determining the starting letter for browsing (uses `REGEXP_REPLACE(headword, '^\([^)]+\)', '')`).

### Aromanian Orthography Quirks
The language has multiple spelling conventions. The scraper merger handles these:

**Auto-merged (same word):**
- ã ↔ â ↔ ă (diacritics)
- dh ↔ d, gh ↔ g, th ↔ t, ch ↔ k (digraphs)
- y ↔ g (palatal variants)

**Need manual review (may be different words):**
- nj ↔ n: `nilushu` (ring) vs `njilushu` (lamb)
- lj ↔ l: `cãljush` (leader) vs `cãlush` (gag)
- dz ↔ z: `dzâpitu` (cracked) vs `zâpitu` (governor)

## Directory Structure

```
dixi_ma_bunu/
├── backend/           # Rust API server
│   └── src/
│       ├── routes/    # API endpoints
│       ├── models/    # Data structures
│       ├── db/        # Database layer
│       ├── search/    # Search logic
│       └── bin/import.rs  # Data import CLI
├── frontend/          # React app
│   └── src/
│       ├── api/       # API client
│       ├── components/
│       ├── hooks/
│       └── pages/
├── scraper/           # Python data pipeline
│   ├── scraper.py     # Web scraper
│   ├── parser.py      # HTML parsing
│   ├── exporter.py    # Format conversion
│   ├── merger.py      # Spelling variant merger
│   ├── review_merges.py  # Manual review CLI
│   └── apply_merges.py   # Final export
└── data/
    ├── aromanian_dictionary.jsonl  # FINAL OUTPUT
    ├── raw/           # Original scraped data
    ├── merged/        # Merged output (detailed)
    └── processing/    # Merge workflow files
```

## Quick Commands

```bash
# Start dev environment
docker compose -f docker-compose.dev.yml up -d

# Run scraper merger
cd scraper && python3 merger.py

# Review merge candidates
cd scraper && python3 review_merges.py

# Apply merges and export final dictionary
cd scraper && python3 apply_merges.py

# Import data to database
docker compose -f docker-compose.dev.yml exec backend \
  cargo run --bin import -- /data/dictionary.jsonl --clear
```

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8080
- Data source: https://www.dixionline.net

## Current State

- **48,829** raw scraped entries
- **40,871** merged word groups
- **~4,900** auto-merged spelling variants
- **1,055** merge candidates pending review

### Pending Review Categories
| Type | Count | Risk |
|------|-------|------|
| other | 634 | varies |
| multiple (3+) | 260 | - |
| a/ã start | 111 | MEDIUM |
| dz/z | 41 | MEDIUM |
| lj/l | 6 | HIGH |
| nj/n | 3 | HIGH |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/search?q=&lang=&pos=&limit=` | Search entries |
| `GET /api/words/{id}` | Get entry by ID |
| `GET /api/words/random` | Word of the Day |
| `GET /api/letters` | List letters with counts |
| `GET /api/letters/{letter}` | Browse by letter |
| `GET /api/suggestions?q=` | Autocomplete |
| `GET /api/stats` | Dictionary statistics |
