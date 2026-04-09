# 625_GROUP_PROJECT
This is the repository for our groups semester-long project
# Agile Addicts — Flashcard Study App

A full-featured flashcard web application built with **Python (Flask)**, **SQLite**, and a clean **MVC architecture**.

## Features

- 🔐 **Register & Login** — secure password hashing, session management
- 📚 **Deck Management** — create, edit, delete decks with custom accent colors
- 🃏 **Flashcard CRUD** — add, edit, delete cards with live flip preview while editing
- 🔄 **Flip Animation** — smooth 3D card flip in both edit preview and study mode
- 📖 **Study Mode** — fullscreen study session with progress bar, keyboard shortcuts
- 🎨 **Dark theme UI** — polished design with Instrument Serif + DM Sans typography

## Project Structure (MVC)

```
flashcard_app/
├── app.py                        # Entry point — Flask app, blueprint registration
├── requirements.txt
├── flashcards.db                 # SQLite database (auto-created on first run)
├── models/
│   ├── database.py               # DB connection, schema initialization
│   ├── user_model.py             # User CRUD + password hashing
│   ├── deck_model.py             # Deck CRUD
│   └── flashcard_model.py        # Flashcard CRUD
├── controllers/
│   ├── auth_controller.py        # Register, login, logout routes
│   ├── deck_controller.py        # Dashboard, deck CRUD, study routes
│   └── flashcard_controller.py   # Card CRUD routes
├── views/templates/
│   ├── base.html                 # Navbar, flash messages layout
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html            # Deck grid overview
│   ├── deck_form.html            # Create / Edit deck
│   ├── deck_view.html            # Deck detail with card list
│   ├── card_form.html            # Create / Edit flashcard (with live preview)
│   └── study.html                # Study mode with flip animation
└── static/
    └── css/
        └── style.css             # Full dark-theme stylesheet
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app (database auto-initializes)
python app.py
```

Then open **http://localhost:5000** in your browser.

## Study Mode Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Flip card |
| `→` / `↓` | Next card |
| `←` / `↑` | Previous card |
