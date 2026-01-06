# Dixi Ma Bunu - Aromanian Dictionary Project Specification

## Overview

A modern web application for browsing and searching the Aromanian/Vlach language dictionary, with data scraped from [dixionline.net](https://www.dixionline.net). The project includes improved search capabilities and a clean, modern interface.

---

## Data Source

### Source Website Structure
- **Base URL:** `https://www.dixionline.net`
- **Browse by letter:** `index.php?l=[letter]`
- **Individual entries:** `index.php?inputWord=[word]`
- **Autocomplete API:** `sugestielive_json.php?q=[query]`

### Entry Data Structure
Each dictionary entry contains:
| Field | Description |
|-------|-------------|
| `headword` | The main word in Aromanian |
| `pronunciation` | Phonetic transcription (in parentheses) |
| `part_of_speech` | Grammatical category (sm, sf, sn, vb, adg, adv) |
| `inflections` | Plural forms, conjugations, gender variants |
| `definition` | Definition in Aromanian |
| `translation_ro` | Romanian translation |
| `translation_en` | English translation |
| `translation_fr` | French translation |
| `etymology` | Word origin (optional) |
| `examples` | Example sentences with usage |
| `expressions` | Idiomatic expressions containing the word |
| `related_terms` | Derived words, variants, cross-references |
| `source` | Source dictionary attribution |
| `db_id` | Original database reference |

### Scale
- Estimated 50,000+ entries total
- ~5,000+ entries for letter "A" alone

---

## Technical Stack

### Scraper
- **Language:** Python 3.11+
- **Libraries:**
  - `httpx` or `aiohttp` for async HTTP requests
  - `beautifulsoup4` for HTML parsing
  - `lxml` for fast parsing
- **Rate limiting:** 1-2 second delay between requests (polite scraping)
- **Output formats:** JSON, CSV, JSONL

### Backend
- **Language:** Rust
- **Framework:** Actix-web
- **Database:** PostgreSQL 15+ with `unaccent` extension
- **ORM:** SQLx or Diesel
- **Search:** PostgreSQL full-text search with trigram similarity

### Frontend
- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS
- **Build tool:** Vite
- **State management:** React Query (TanStack Query) for server state

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Configurations:**
  - `docker-compose.yml` - Production setup
  - `docker-compose.dev.yml` - Development with hot reload

---

## Search Features

### Core Requirements
1. **Diacritic-insensitive search**
   - Query "casa" matches "casã"
   - Uses PostgreSQL `unaccent` extension

2. **Multilingual search**
   - Search by Aromanian headword
   - Search by Romanian translation
   - Search by English translation
   - Search by French translation

3. **Fuzzy matching**
   - Tolerant of typos using trigram similarity (`pg_trgm`)
   - Example: "cassa" still finds "casã"

4. **Implicit wildcard/prefix matching**
   - Query "cas" automatically finds "casã", "casãlu", "cascaval", etc.
   - No need to type explicit wildcard symbols

### Search Algorithm Priority
1. Exact match (highest priority)
2. Prefix match
3. Contains match
4. Fuzzy/similar match (lowest priority)

---

## User Features

### Search Interface
- Large, prominent search bar
- Real-time suggestions as user types
- Filter by language (Aromanian/Romanian/English/French)
- Filter by part of speech

### Word Display
- Clean, readable entry layout
- Pronunciation clearly displayed
- Translations grouped by language
- Expandable sections for examples and related terms

### Additional Features
1. **Word of the Day**
   - Random word featured on homepage
   - Changes daily

2. **Recent Searches**
   - Stored in browser localStorage/cookies
   - Shows last 10-20 searches
   - No user accounts required

### UI/UX Style
- Minimalist/clean design
- Focus on content and readability
- Fast, responsive interface
- Mobile-friendly

---

## Data Export Formats

For ML training and other uses, the scraped data will be available in:

### 1. JSON (`dictionary.json`)
```json
{
  "metadata": {
    "source": "dixionline.net",
    "scraped_at": "2024-01-06T...",
    "total_entries": 50000
  },
  "entries": [
    {
      "headword": "casã",
      "pronunciation": "ká-sə",
      "part_of_speech": "sf",
      "translations": {
        "ro": "casă",
        "en": "house",
        "fr": "maison"
      },
      ...
    }
  ]
}
```

### 2. JSON Lines (`dictionary.jsonl`)
```jsonl
{"headword": "casã", "pronunciation": "ká-sə", "part_of_speech": "sf", ...}
{"headword": "apã", "pronunciation": "á-pə", "part_of_speech": "sf", ...}
```

### 3. CSV (`dictionary.csv`)
Flattened structure suitable for spreadsheets:
```csv
headword,pronunciation,part_of_speech,translation_ro,translation_en,translation_fr,definition,...
casã,ká-sə,sf,casă,house,maison,...
```

---

## Docker Configuration

### Production (`docker-compose.yml`)
```yaml
services:
  db:
    image: postgres:15-alpine
    # Persistent volume, optimized settings

  backend:
    build: ./backend
    # Multi-stage build, release binary

  frontend:
    build: ./frontend
    # Nginx serving static build
```

### Development (`docker-compose.dev.yml`)
```yaml
services:
  db:
    image: postgres:15-alpine

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    # cargo-watch for hot reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
    # Vite dev server with HMR
```

---

## Project Structure

```
dixi_ma_bunu/
├── spec.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── scraper/
│   ├── requirements.txt
│   ├── scraper.py
│   ├── parser.py
│   └── exporter.py
├── data/
│   ├── dictionary.json
│   ├── dictionary.jsonl
│   └── dictionary.csv
├── backend/
│   ├── Cargo.toml
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── src/
│       ├── main.rs
│       ├── routes/
│       ├── models/
│       ├── db/
│       └── search/
└── frontend/
    ├── package.json
    ├── Dockerfile
    ├── Dockerfile.dev
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── components/
        ├── hooks/
        └── pages/
```

---

## Implementation Phases

### Phase 1: Scraper
- Build scraper to extract all entries from dixionline.net
- Parse HTML to extract structured data
- Export to JSON, JSONL, CSV formats
- Handle errors and resume capability

### Phase 2: Database & Backend
- Set up PostgreSQL schema with proper indexes
- Implement Actix-web REST API
- Build search functionality with all features
- Import scraped data

### Phase 3: Frontend
- Create React app with Tailwind
- Build search interface with real-time suggestions
- Implement word display pages
- Add Word of the Day and recent searches

### Phase 4: Docker & Deployment
- Create production Docker configuration
- Create development Docker configuration with hot reload
- Test full stack locally
- Document deployment process

---

## API Endpoints

```
GET  /api/search?q={query}&lang={lang}&pos={pos}&limit={n}
GET  /api/words/{id}
GET  /api/words/random          # For Word of the Day
GET  /api/letters               # Get all available letters
GET  /api/letters/{letter}      # Browse by letter
GET  /api/suggestions?q={query} # Autocomplete
GET  /api/stats                 # Dictionary statistics
```

---

## Notes

- The scraper should be run once initially and can be re-run to update data
- Consider caching frequent searches in Redis (future enhancement)
- The unaccent + trigram approach in PostgreSQL handles most search requirements without needing Elasticsearch
- Word of the Day can be seeded or truly random with daily cache
