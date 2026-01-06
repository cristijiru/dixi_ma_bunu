# Dixi Ma Bunu

A modern web application for browsing and searching the Aromanian/Vlach language dictionary.

## Features

- Full-text search with diacritic-insensitive matching
- Fuzzy search with typo tolerance
- Browse dictionary by letter
- Word of the Day
- Translations in Romanian, English, and French
- Dark mode support
- Mobile-friendly responsive design

## Tech Stack

### Backend
- **Language:** Rust
- **Framework:** Actix-web
- **Database:** PostgreSQL 15+ with `unaccent` and `pg_trgm` extensions
- **ORM:** SQLx

### Frontend
- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS
- **Build:** Vite
- **State:** TanStack Query (React Query)
- **Testing:** Vitest + Testing Library

### Infrastructure
- Docker & Docker Compose
- Hot reload in development

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) Rust 1.75+ for local development
- (Optional) Node.js 20+ for local frontend development

### Quick Start with Docker

```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop services
docker compose -f docker-compose.dev.yml down
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8080
- PostgreSQL: localhost:5432

### Data Import

The data is automatically imported on first container startup if:
1. The `entries` table is empty
2. `/data/dictionary.jsonl` exists

To manually reimport:
```bash
docker compose -f docker-compose.dev.yml exec backend \
  cargo run --bin import -- /data/dictionary.jsonl --clear
```

### Local Development (without Docker)

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your database URL
cargo run
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Run Tests:**
```bash
# Frontend tests
cd frontend
npm test

# Backend tests (requires database)
cd backend
cargo test
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/search?q=&lang=&pos=&limit=` | Search entries |
| `GET /api/words/{id}` | Get entry by ID |
| `GET /api/words/random` | Random word (Word of Day) |
| `GET /api/letters` | List all letters with counts |
| `GET /api/letters/{letter}` | Browse by letter |
| `GET /api/suggestions?q=` | Autocomplete suggestions |
| `GET /api/stats` | Dictionary statistics |
| `GET /api/health` | Health check |

### Search Parameters

- `q` - Search query (required)
- `lang` - Filter by language: `rup`, `ro`, `en`, `fr`, `all`
- `pos` - Filter by part of speech: `sf`, `sm`, `sn`, `vb`, `adg`, `adv`
- `limit` - Max results (default: 20, max: 100)

## Project Structure

```
dixi_ma_bunu/
├── backend/
│   ├── src/
│   │   ├── main.rs          # Server entry point
│   │   ├── lib.rs           # Library exports
│   │   ├── models/          # Data structures
│   │   ├── db/              # Database layer
│   │   ├── routes/          # API endpoints
│   │   ├── search/          # Search logic
│   │   └── bin/import.rs    # Data import CLI
│   ├── Dockerfile
│   └── Dockerfile.dev
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Route pages
│   │   └── test/            # Test utilities
│   ├── Dockerfile
│   └── Dockerfile.dev
├── scraper/                  # Python scraper
├── data/                     # Scraped dictionary data
├── docker-compose.yml        # Production config
├── docker-compose.dev.yml    # Development config
└── spec.md                   # Full specification
```

## Data Source

Dictionary data is scraped from [dixionline.net](https://www.dixionline.net) with their permission. The scraper is located in the `scraper/` directory.

## License

MIT
