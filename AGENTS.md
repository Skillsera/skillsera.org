# Skillsera Development Guide

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy 2 + PostgreSQL |
| Templates | Jinja2 (server-rendered HTML) |
| Frontend | htmx 2 (partial updates) + Alpine.js 3 (client reactivity) |
| Browser tests | Playwright (`@playwright/test`) |
| API tests | pytest + FastAPI `TestClient` |
| Local dev | Docker Compose |

---

## Quick Start

```bash
docker compose up          # starts app on :8000 + postgres
open http://localhost:8000
```

For development with auto-reload, the `app` container already runs uvicorn with `--reload`. Edit files in `app/` or `static/` and the server restarts automatically.

---

## Running Tests

### API tests (fast, no browser)
```bash
pip install -r requirements.txt
pytest tests/api/ -v
```

### Browser tests (Playwright)
```bash
# First install browsers once:
npm install
npx playwright install chromium

# Run with app already running (docker compose up or local uvicorn):
npm run test:e2e

# Interactive UI mode:
npm run test:e2e:ui

# Run headed (see the browser):
npm run test:e2e:headed
```

---

## Development Workflow: TDD

We use test-driven development. The loop is:

1. **Write a failing test first.** Before touching any application code, write a Playwright test (for UI features) or a pytest test (for API behavior) that describes what the feature should do.
2. **Watch it fail.** Run the test. It should fail with a meaningful error.
3. **Implement the feature.** Write the minimum code to make the test pass.
4. **Watch it pass.** Run the test again. Green.
5. **Commit both.** The test and the implementation go in the same commit.

### Adding a UI feature

```bash
# 1. Write the test
# tests/e2e/my_feature.spec.js
test('user can do X', async ({ page }) => { ... });

# 2. Run it — watch it fail
npm run test:e2e

# 3. Implement in app/routers/ + app/templates/
# 4. Run again — green
npm run test:e2e
```

### Adding an API endpoint

```bash
# 1. Write the test
# tests/api/test_my_thing.py
def test_my_endpoint_returns_200(client): ...

# 2. Run it — watch it fail
pytest tests/api/test_my_thing.py -v

# 3. Implement the route in app/routers/
# 4. Run again — green
pytest tests/api/ -v
```

---

## Regression Policy

> **Any bug fix must include a test that would have caught the bug.**

- UI regression → add a test to `tests/e2e/`
- API regression → add a test to `tests/api/`
- The test goes in the same PR as the fix.
- If you can reproduce a bug without a test, write the test first, confirm it fails, then fix.

---

## htmx Conventions

- **Dual-response routes**: check `request.headers.get("HX-Request") == "true"` to decide whether to return an HTML fragment or JSON.
- **Partials live in** `app/templates/partials/`. Full pages live in `app/templates/`.
- **Loading states**: use `hx-indicator` on the triggering element and add a spinner element with class `htmx-indicator`.
- **Navigation**: use `hx-push-url` to keep the browser URL in sync when htmx loads new content.
- **Forms**: use `hx-post` / `hx-put` with `hx-target` and `hx-swap` to update the page without a full reload.

Example — search with htmx:
```html
<input name="q"
       hx-get="/questions/search"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#results"
       hx-indicator="#spinner">
<span id="spinner" class="htmx-indicator">Searching...</span>
<div id="results"></div>
```

---

## Alpine.js Conventions

- **Use Alpine for purely client-side state** — things that don't need a server round-trip (e.g., toggling a form open/closed, switching the active video in a player).
- **Keep `x-data` scopes small** and colocated with the markup they control. Avoid global Alpine stores unless state is truly shared across the page.
- **Don't replicate server state in Alpine** — htmx handles fetching and updating DOM from the server. Alpine should only hold ephemeral UI state.
- Use `x-cloak` on elements that should be hidden until Alpine initialises (add `[x-cloak] { display: none }` to your CSS).

Example — video player:
```html
<div x-data="videoPlayer()">
  <button @click="play(url, start, stop)">▶ Play</button>
  <div x-show="embedUrl" x-cloak>
    <iframe :src="embedUrl"></iframe>
  </div>
</div>
```

---

## Project Structure

```
app/
  main.py          ← FastAPI app, middleware, router mounts
  config.py        ← Settings (pydantic-settings, reads from env)
  database.py      ← SQLAlchemy engine + get_db dependency
  models/
    graph.py       ← SQLAlchemy ORM models (Question, Answer, Tag, User, ...)
  routers/
    pages.py       ← Full HTML page routes (/, /learn, /about)
    questions.py   ← /questions/* (JSON + htmx partials)
    answers.py     ← /answers/*
    tags.py        ← /tags/*
    auth.py        ← /auth/* (login, logout, register, session, activate)
  templates/
    base.html      ← Shared layout with htmx/Alpine CDN scripts
    index.html     ← Search landing page
    learn.html     ← Question + video answers
    about.html     ← About page
    partials/      ← htmx fragments (not full pages)

static/
  css/style.css    ← All styles
  js/player.js     ← Alpine videoPlayer() component
  imgs/            ← Images

tests/
  conftest.py      ← pytest fixtures, TestClient, SQLite test DB
  api/             ← pytest API tests
  e2e/             ← Playwright browser tests
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://skillsera:skillsera@localhost/skillsera` | Postgres connection string |
| `SECRET_KEY` | dev value | Session signing key — change in production |
| `AUTH_SERVER_URL` | `https://auth.skillsera.org` | External auth server |
| `CORS_ORIGINS` | `["http://localhost:8000"]` | Allowed CORS origins |
| `DEBUG` | `false` | Enables `/api/docs` Swagger UI |

Copy `.env.example` to `.env` to override locally.

---

## Adding a New Feature — Checklist

- [ ] Write failing Playwright test in `tests/e2e/`
- [ ] Add route in appropriate router (`app/routers/`)
- [ ] Add full-page template or partial in `app/templates/`
- [ ] Wire htmx attributes in the template
- [ ] Add Alpine `x-data` if client state is needed
- [ ] Run `npm run test:e2e` — all green
- [ ] Run `pytest tests/api/` — all green
- [ ] Commit test + implementation together
