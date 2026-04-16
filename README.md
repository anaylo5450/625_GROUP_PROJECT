# Agile Addicts — Flashcard Study App

A full-featured flashcard web application built with **Python (Flask)**, **SQLite**, and a clean **MVC architecture**.

**Course:** COSC 625 — Advanced Software Engineering
**Team:** Chidi Azubike · Richard Baldwin · Frits Buningh · Andrew Naylor

---

## Features

- **Register & Login** — secure password hashing (werkzeug pbkdf2), session management
- **Deck Management** — create, edit, delete decks with custom accent colors, tags, and public/private visibility
- **Flashcard CRUD** — add, edit, delete cards with live flip preview while editing
- **Flip Animation** — smooth 3D card flip in both edit preview and study mode
- **Study Mode** — fullscreen study session with progress bar and correct/incorrect tracking
- **Session Stats** — study session results stored automatically; stats overview and per-deck history
- **Dark theme UI** — polished design with Instrument Serif + DM Sans typography

---

## Project Structure

The active application lives under `src/625_GROUP_PROJECT/`. The orphaned files at the repo root (`flashcards/`, `db.py`, `main.py`, `__init__.py`) are an earlier prototype — do not run or modify them.

```
src/625_GROUP_PROJECT/
├── app.py                        # Entry point — run this
├── requirements.txt
├── flashcards.db                 # SQLite database (auto-created on first run)
├── models/
│   ├── database.py               # DB connection, schema init, migrations
│   ├── user_model.py             # User CRUD + password hashing
│   ├── deck_model.py             # Deck CRUD
│   ├── flashcard_model.py        # Flashcard CRUD
│   └── stats_model.py            # Study session storage and queries
├── controllers/
│   ├── auth_controller.py        # /register, /login, /logout
│   ├── deck_controller.py        # /dashboard, deck CRUD routes
│   ├── flashcard_controller.py   # Card CRUD routes
│   └── stats_controller.py       # /stats, /deck/<id>/stats, session API
├── views/templates/
│   ├── base.html                 # Navbar, flash messages layout
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html            # Deck grid overview
│   ├── deck_form.html            # Create / edit deck
│   ├── deck_view.html            # Deck detail with card list
│   ├── card_form.html            # Create / edit flashcard (with live flip preview)
│   ├── study.html                # Study session with flip animation
│   ├── stats_overview.html       # User-wide stats (Sprint 2)
│   └── stats_deck.html           # Per-deck session history (Sprint 2)
└── static/
    └── css/
        └── style.css             # Full dark-theme stylesheet
```

---

## Setup & Run

```bash
# 1. Create and activate a virtual environment (from repo root)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r src/625_GROUP_PROJECT/requirements.txt

# 3. Run the app — must be run from the src/625_GROUP_PROJECT/ directory
cd src/625_GROUP_PROJECT
../../.venv/bin/python app.py
```

Then open **http://localhost:5000** in your browser.

The database (`flashcards.db`) is created automatically on first run. If the schema ever gets corrupted, delete `src/625_GROUP_PROJECT/flashcards.db` and restart — it will be recreated from scratch.

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Registered accounts (username, email, hashed password) |
| `decks` | Decks with title, description, tags, visibility, color |
| `flashcards` | Cards linked to a deck (front text, back text) |
| `study_sessions` | Session results: cards seen, correct, wrong, duration |

Schema migrations run automatically on every startup via `migrate_decks()` and `migrate_stats()` in `database.py` — safe to re-run against an existing database.

---

## Study Mode Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Flip card |
| `→` / `↓` | Next card |
| `←` / `↑` | Previous card |

---

## Sprint Status

| Sprint | Stories | Points | Status |
|--------|---------|--------|--------|
| Sprint 1 | US-1 (auth), US-2 (login), US-3 (create deck), US-4 (update deck), US-5.1–5.3 (flashcard CRUD) | 19 planned + US-4 bonus | Complete |
| Sprint 2 | US-5.4–5.6 (image upload), US-6.6 (card frequency), US-7 (stats display), US-9 (password reset), US-11 (deck sharing) | 27+ | In progress |
| Sprint 3 | US-7 remaining, polish, stretch goals | 11+ | Not started |

Scrum board: [GitHub Projects #2](https://github.com/users/anaylo5450/projects/2)

---

## Team

| Name | GitHub | Role |
|------|--------|------|
| Richard Baldwin | [@eyeclept](https://github.com/eyeclept) | Organization Lead — board, docs, auth, security |
| Chidi Azubike | [@caazubike](https://github.com/caazubike) | Programming Lead — MVC architecture, controllers, stylesheet |
| Frits Buningh | [@Sailor1976](https://github.com/Sailor1976) | DB Lead — original prototype, schema, flashcard CRUD |
| Andrew Naylor | [@anaylo5450](https://github.com/anaylo5450) | Writing Lead — user stories, preconditions, deck DB fields |
