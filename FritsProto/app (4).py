from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)
import mysql.connector
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------------------------------------------------------
# App + Session
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM_STRING"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("flask_app.log", "a", "utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
db_config = {
    "host": "localhost",
    "user": "rfdiurne_Sailor76",
    "password": "Delta_99!",
    "database": "rfdiurne_Sprint1",
    "charset": "utf8mb4",
    "use_unicode": True,
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _require_login():
    return "user_id" in session

def _norm(s):
    return (s or "").strip().lower()

def _get_question_count_for_user(user_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM flashcard_questions
            WHERE user_id = %s
            """,
            (user_id,)
        )
        row = cur.fetchone()
        return int(row["cnt"]) if row else 0

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# -----------------------------------------------------------------------------
# Home
# -----------------------------------------------------------------------------
@app.route("/")
@app.route("/index")
@app.route("/index.html")
def index():
    return render_template("index.html")

# -----------------------------------------------------------------------------
# Flashcards Home
# -----------------------------------------------------------------------------
@app.route("/flashcards")
def flashcards_home():
    return render_template("flashcards/flashcards_home.html")

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------
@app.route("/flashcards/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = (request.form.get("firstname") or "").strip()
        lastname = (request.form.get("lastname") or "").strip()
        username = (request.form.get("username") or "").strip()
        school = (request.form.get("school") or "").strip()
        password = request.form.get("password") or ""

        if not firstname or not lastname or not username or not password:
            return redirect(url_for("register"))

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute(
                "SELECT user_id FROM users WHERE username = %s",
                (username,)
            )
            if cur.fetchone():
                logger.info("Register blocked: username already exists: %s", username)
                return redirect(url_for("register"))

            pw_hash = generate_password_hash(password)

            cur.execute(
                """
                INSERT INTO users (firstname, lastname, username, school, password_hash)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (firstname, lastname, username, school if school else None, pw_hash)
            )
            conn.commit()

            return redirect(url_for("login"))

        except Exception as e:
            logger.exception("Registration error: %s", e)
            return redirect(url_for("register"))

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("flashcards/register.html")


@app.route("/flashcards/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            return redirect(url_for("login"))

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute(
                """
                SELECT user_id, firstname, lastname, username, password_hash
                FROM users
                WHERE username = %s
                """,
                (username,)
            )
            user = cur.fetchone()

            if not user:
                logger.info("Login failed: user not found: %s", username)
                return redirect(url_for("login"))

            if not user.get("password_hash"):
                logger.info("Login failed: no password hash for %s", username)
                return redirect(url_for("login"))

            if not check_password_hash(user["password_hash"], password):
                logger.info("Login failed: bad password for %s", username)
                return redirect(url_for("login"))

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["firstname"] = user["firstname"]

            return redirect(url_for("flashcards_menu"))

        except Exception as e:
            logger.exception("Login error: %s", e)
            return redirect(url_for("login"))

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("flashcards/login.html")


@app.route("/flashcards/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("firstname", None)
    session.pop("hist_pending_q", None)
    session.pop("hist_pending_quiz_name", None)
    session.pop("sample_answers", None)
    return redirect(url_for("flashcards_home"))

# -----------------------------------------------------------------------------
# Flashcards Menu
# -----------------------------------------------------------------------------
@app.route("/flashcards/menu")
def flashcards_menu():
    if not _require_login():
        return redirect(url_for("login"))
    return render_template("flashcards/flashcards_menu.html")

# -----------------------------------------------------------------------------
# SAMPLE HISTORY QUIZ (no DB writes)
# -----------------------------------------------------------------------------
SAMPLE_HISTORY = [
    {
        "question": "Who was the first President of the United States?",
        "choices": ["John Adams", "Thomas Jefferson", "George Washington", "James Madison"],
        "correct": 2
    },
    {
        "question": "What country did Texas belong to before becoming a US state?",
        "choices": ["Spain", "France", "Mexico", "Colombia"],
        "correct": 2
    },
    {
        "question": "Which nobleman helped George Washington fight the British?",
        "choices": ["Napoleon", "de Lafayette", "Wellington", "Bismarck"],
        "correct": 1
    },
    {
        "question": "What year did World War II end?",
        "choices": ["1943", "1945", "1947", "1950"],
        "correct": 1
    },
    {
        "question": "Who wrote the Declaration of Independence?",
        "choices": ["Jefferson", "Adams", "Franklin", "Hamilton"],
        "correct": 0
    },
    {
        "question": "What empire built the Colosseum?",
        "choices": ["Greek", "Roman", "Ottoman", "Persian"],
        "correct": 1
    },
    {
        "question": "What language did the US almost adopt according to legend?",
        "choices": ["German", "Dutch", "French", "Spanish"],
        "correct": 0
    },
    {
        "question": "Which state joined the Union as the 51st?",
        "choices": ["Puerto Rico", "Hawaii", "Guam", "Alaska"],
        "correct": 1
    },
    {
        "question": "Who was President during the Civil War?",
        "choices": ["Lincoln", "Grant", "Jackson", "Wilson"],
        "correct": 0
    },
    {
        "question": "Which document begins with 'We the People'?",
        "choices": ["Bill of Rights", "Constitution", "Declaration of Independence", "Articles of Confederation"],
        "correct": 1
    }
]

@app.route("/flashcards/sample/start")
def sample_history_start():
    session["sample_answers"] = []
    session.modified = True
    return render_template("flashcards/sample_history_start.html")


@app.route("/flashcards/sample/quiz/<int:n>", methods=["GET", "POST"])
def sample_history_quiz(n):
    total = len(SAMPLE_HISTORY)

    if n < 1:
        return redirect(url_for("sample_history_quiz", n=1))

    if n > total:
        return redirect(url_for("sample_history_results"))

    card = SAMPLE_HISTORY[n - 1]

    if request.method == "POST":
        pick_raw = request.form.get("pick")
        if pick_raw is None:
            return redirect(url_for("sample_history_quiz", n=n))

        try:
            pick = int(pick_raw)
        except ValueError:
            return redirect(url_for("sample_history_quiz", n=n))

        if pick not in (0, 1, 2, 3):
            return redirect(url_for("sample_history_quiz", n=n))

        answers = session.get("sample_answers", [])
        if not isinstance(answers, list):
            answers = []

        answers.append(pick)
        session["sample_answers"] = answers
        session.modified = True

        return redirect(url_for("sample_history_quiz", n=n + 1))

    return render_template(
        "flashcards/history_quiz.html",
        n=n,
        total=total,
        card=card
    )


@app.route("/flashcards/sample/results")
def sample_history_results():
    answers = session.get("sample_answers", [])
    if not isinstance(answers, list):
        answers = []

    rows = []
    correct_count = 0
    total = len(SAMPLE_HISTORY)

    for i, card in enumerate(SAMPLE_HISTORY):
        correct_idx = card["correct"]
        choices = card["choices"]
        question = card["question"]

        picked_idx = answers[i] if i < len(answers) else None

        picked_text = "(no answer)"
        if picked_idx is not None and 0 <= picked_idx < len(choices):
            picked_text = choices[picked_idx]

        correct_text = choices[correct_idx]
        is_correct = picked_idx == correct_idx

        if is_correct:
            correct_count += 1

        rows.append({
            "question": question,
            "picked_text": picked_text,
            "correct_text": correct_text,
            "is_correct": is_correct
        })

    score_percent = int(round((correct_count / total) * 100)) if total else 0

    return render_template(
        "flashcards/sample_history_results.html",
        rows=rows,
        score_percent=score_percent
    )

# -----------------------------------------------------------------------------
# CREATE QUIZ QUESTION
# -----------------------------------------------------------------------------
HIST_PENDING_Q = "hist_pending_q"
HIST_PENDING_QUIZ_NAME = "hist_pending_quiz_name"

@app.route("/flashcards/history/create/question", methods=["GET", "POST"])
def history_create_question():
    if not _require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        quiz_name = (request.form.get("quiz_name") or "").strip()
        question = (request.form.get("question") or "").strip()

        if not quiz_name or not question:
            return redirect(url_for("history_create_question"))

        session[HIST_PENDING_QUIZ_NAME] = quiz_name
        session[HIST_PENDING_Q] = question

        return redirect(url_for("history_create_choices"))

    card_count = _get_question_count_for_user(session["user_id"])

    return render_template(
        "flashcards/history_create_question.html",
        card_count=card_count
    )


@app.route("/flashcards/history/create/choices", methods=["GET", "POST"])
def history_create_choices():
    if not _require_login():
        return redirect(url_for("login"))

    question = session.get(HIST_PENDING_Q)
    quiz_name = session.get(HIST_PENDING_QUIZ_NAME)

    if not question or not quiz_name:
        return redirect(url_for("history_create_question"))

    if request.method == "POST":
        a1 = (request.form.get("a1") or "").strip()
        a2 = (request.form.get("a2") or "").strip()
        a3 = (request.form.get("a3") or "").strip()
        a4 = (request.form.get("a4") or "").strip()
        correct_raw = request.form.get("correct")

        if not all([a1, a2, a3, a4]) or correct_raw is None:
            return redirect(url_for("history_create_choices"))

        try:
            correct_idx = int(correct_raw)
        except ValueError:
            return redirect(url_for("history_create_choices"))

        if correct_idx not in (0, 1, 2, 3):
            return redirect(url_for("history_create_choices"))

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            correct_choice_db = correct_idx + 1

            cur.execute(
                """
                INSERT INTO flashcard_questions
                (user_id, quiz_name, question, choice1, choice2, choice3, choice4, correct_choice)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    quiz_name,
                    question,
                    a1,
                    a2,
                    a3,
                    a4,
                    correct_choice_db
                )
            )
            conn.commit()

            session.pop(HIST_PENDING_Q, None)
            session.pop(HIST_PENDING_QUIZ_NAME, None)

            return redirect(url_for("history_after_save"))

        except Exception as e:
            logger.exception("Flashcard insert error: %s", e)
            return redirect(url_for("history_create_choices"))

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template(
        "flashcards/history_create_choices.html",
        question=question,
        quiz_name=quiz_name
    )


@app.route("/flashcards/history/after_save")
def history_after_save():
    if not _require_login():
        return redirect(url_for("login"))

    card_count = _get_question_count_for_user(session["user_id"])

    return render_template(
        "flashcards/history_after_save.html",
        card_count=card_count
    )

# -----------------------------------------------------------------------------
# WSGI ENTRYPOINT
# -----------------------------------------------------------------------------
application = app

if __name__ == "__main__":
    app.run(debug=True)