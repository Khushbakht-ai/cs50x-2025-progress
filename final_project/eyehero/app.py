import os
import json
import calendar
from datetime import date, datetime, timedelta
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------- Flask Setup ----------------
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Random secret key for sessions

# Flask session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ---------------- Database Setup ----------------
# Using CS50 SQL library with SQLite database
db = SQL("sqlite:///db/eyehero.db")

# ---------------- Routes ----------------

# Landing page / front page


@app.route("/")
def index():
    """
    If user is logged in, redirect to home.
    Otherwise, render the landing/front page.
    """
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("frontpage.html")

# Serve service worker for push notifications


@app.route("/sw.js")
def service_worker():
    """
    Returns the service worker JavaScript file for enabling
    push notifications in the browser.
    """
    return send_from_directory("static/js", "sw.js")

# Subscribe user to push notifications


@app.route("/subscribe", methods=["POST"])
def subscribe():
    """
    Handles subscription of a logged-in user to push notifications.
    Saves subscription details in the database to avoid duplicates.
    """
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 403

    user_id = session["user_id"]
    data = request.json
    subscription = json.dumps(data)

    try:
        # Insert subscription if it doesn't already exist
        db.execute(
            "INSERT OR IGNORE INTO push_subscriptions (user_id, subscription) VALUES (?, ?)",
            user_id, subscription
        )
        return jsonify({"success": True}), 201
    except Exception as e:
        print("Error saving subscription:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# List all push subscriptions (for testing purposes)


@app.route("/subscriptions")
def get_subscriptions():
    """
    Returns all push subscriptions stored in the database.
    Useful for debugging or testing notifications.
    """
    try:
        subs = db.execute("SELECT * FROM push_subscriptions")
        return jsonify(subs)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- Login ----------------


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    GET: Render login form.
    POST: Verify credentials and start session.
    """
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query user from database
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1:
            flash("Invalid username", "warning")
            return redirect(url_for("login"))

        # Check password hash
        if not check_password_hash(user[0]["hash"], password):
            flash("Invalid password", "warning")
            return redirect(url_for("login"))

        # Store user ID in session
        session["user_id"] = user[0]["id"]
        flash("Login successful!", "success")
        return redirect(url_for("home"))

    # Render login page
    return render_template("login.html")

# ---------------- Signup ----------------


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Handles new user registration.
    GET: Render signup form.
    POST: Validate input, hash password and security answer,
          save user to database.
    """
    # Predefined security questions
    questions = [
        "What is your pet's name?",
        "What is your mother's maiden name?",
        "What is your favorite color?"
    ]

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        security_question = request.form.get("security_question")
        security_answer = request.form.get("security_answer")

        # Ensure passwords match
        if password != confirm_password:
            flash("Passwords do not match", "warning")
            return redirect(url_for("signup"))

        # Hash password and security answer for secure storage
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        hashed_answer = generate_password_hash(
            security_answer.strip().lower(), method="pbkdf2:sha256")

        try:
            # Insert new user into database
            db.execute(
                "INSERT INTO users (username, hash, security_question, security_que_answer, join_date) VALUES (?, ?, ?, ?, ?)",
                username, hashed_password, security_question, hashed_answer, date.today().isoformat()
            )
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("Username already exists", "danger")
            return redirect(url_for("signup"))

    return render_template("signup.html", questions=questions)

# ---------------- Forget / Reset Password ----------------


@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    """
    Handles password recovery using a security question.
    Step 1: Enter username
    Step 2: Answer security question
    Step 3: Set new password
    """
    username = None
    question = None

    # Step 1: User submits username
    if request.method == "POST" and "username" in request.form and "answer" not in request.form:
        username = request.form.get("username")
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1:
            flash("Username not found", "danger")
            return render_template("forget_password.html", step=1)
        question = user[0]["security_question"]
        return render_template("forget_password.html", step=2, username=username, question=question)

    # Step 2 & 3: User answers question and sets new password
    if request.method == "POST" and "answer" in request.form:
        username = request.form.get("username")
        answer = request.form.get("answer").strip().lower()
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)[0]
        question = user["security_question"]

        # Verify security answer
        if not check_password_hash(user["security_que_answer"], answer):
            flash("Incorrect answer to security question", "danger")
            return render_template("forget_password.html", step=2, username=username, question=question)

        # Validate and update password
        if new_password and confirm_password:
            if new_password != confirm_password:
                flash("Passwords do not match", "warning")
                return render_template("forget_password.html", step=3, username=username, question=question)

            hashed_password = generate_password_hash(new_password, method="pbkdf2:sha256")
            db.execute("UPDATE users SET hash = ? WHERE username = ?", hashed_password, username)
            flash("Password reset successful!", "success")
            return redirect(url_for("login"))

        return render_template("forget_password.html", step=3, username=username, question=question)

    return render_template("forget_password.html", step=1)

# ---------------- Home ----------------


@app.route("/home")
def home():
    """
    User dashboard.
    Only accessible if logged in.
    """
    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))
    return render_template("home.html")

# ---------------- 20-20-20 Rule ----------------


@app.route("/rule")
def rule():
    """Page with 20-20-20 eye strain timer."""
    return render_template("rule.html")

# ---------------- Exercise Page ----------------


@app.route("/exercise")
def exercise():
    """Generic exercise page (entry point)."""
    return render_template("exercise.html")

# ---------------- Progress Page ----------------


@app.route("/progress", methods=["GET", "POST"])
def progress():
    """
    Tracks user progress for morning/night exercises.
    POST: Update today's progress
    GET: Show calendar view of current month with streak
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # ---- POST: Update progress ----
    if request.method == "POST":
        try:
            today = date.today().isoformat()
            data = request.get_json()
            exercise_type = data.get("type")  # "morning" or "night"

            # Check if entry exists
            row = db.execute(
                "SELECT * FROM progress WHERE user_id = ? AND date = ?", user_id, today
            )
            if row:
                db.execute(
                    f"UPDATE progress SET {exercise_type}_done = 1 WHERE user_id = ? AND date = ?", user_id, today
                )
            else:
                morning_done = 1 if exercise_type == "morning" else 0
                night_done = 1 if exercise_type == "night" else 0
                db.execute(
                    "INSERT INTO progress (user_id, date, morning_done, night_done) VALUES (?, ?, ?, ?)",
                    user_id, today, morning_done, night_done
                )
            return jsonify({"success": True})
        except Exception as e:
            print("POST /progress ERROR:", e)
            return jsonify({"success": False})

    # ---- GET: Show progress calendar ----
    today = date.today()
    start_month = today.replace(day=1).isoformat()
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_month = today.replace(day=last_day).isoformat()

    rows = db.execute(
        "SELECT * FROM progress WHERE user_id = ? AND date BETWEEN ? AND ?",
        user_id, start_month, end_month
    )

    # Build dictionary for frontend
    user_progress = {row["date"]: {"morning": bool(
        row["morning_done"]), "night": bool(row["night_done"])} for row in rows}

    # Calculate streak (consecutive days with both morning & night done)
    streak = 0
    completed_dates = sorted(
        [datetime.strptime(d, "%Y-%m-%d").date() for d in user_progress if user_progress[d]
         ["morning"] and user_progress[d]["night"]],
        reverse=True
    )

    if completed_dates:
        current_day = completed_dates[0]
        for d in completed_dates:
            if d == current_day:
                streak += 1
                current_day -= timedelta(days=1)
            else:
                break

    return render_template(
        "progress.html",
        user_progress=user_progress,
        streak=streak,
        year=today.year,
        month=today.month,
        last_day=last_day
    )

# ---------------- Morning & Night Exercises ----------------


@app.route("/morning_exercise")
def morning_exercise():
    """Morning exercise routine page."""
    return render_template("morning_exercise.html")


@app.route("/night_exercise")
def night_exercise():
    """Night exercise routine page."""
    return render_template("night_exercise.html")

# ---------------- Logout ----------------


@app.route("/logout")
def logout():
    """Logout the user and clear the session."""
    session.clear()
    return redirect(url_for("index"))


# ---------------- Main ----------------
if __name__ == "__main__":
    # Run Flask app in debug mode
    app.run(debug=True)
