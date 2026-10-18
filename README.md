# Skillsera

A community-powered encyclopedia which teaches educational concepts by connecting bite-sized YouTube video explanations.

## Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: htmx + Alpine.js + Jinja2 (server-rendered, no build step)
- **Tests**: Playwright (browser) + pytest (API)
- **Local dev**: Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up
open http://localhost:8000
```

## Development

See [AGENTS.md](AGENTS.md) for the full development guide including TDD workflow, htmx/Alpine conventions, and testing instructions.

## Running Tests

```bash
# API tests
pytest tests/api/ -v

# Browser tests (requires app running)
npm install && npx playwright install chromium
npm run test:e2e
```

## API Docs

Start the app with `DEBUG=true` and visit http://localhost:8000/api/docs.
