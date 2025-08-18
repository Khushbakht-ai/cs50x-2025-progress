import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from sqlite3 import IntegrityError

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    rows = db.execute("""
        SELECT symbol, SUM(shares) AS total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING SUM(shares) > 0
    """, session["user_id"])

    portfolio = []
    for row in rows:
        stock = lookup(row["symbol"])
        portfolio.append({
            "symbol": row["symbol"],
            "shares": row["total_shares"],
            "price": stock["price"],
            "total": row["total_shares"] * stock["price"]
        })

    user_cash_row = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = user_cash_row[0]["cash"]
    grand_total = cash + sum(item["total"] for item in portfolio)

    return render_template("index.html", purchases=portfolio, cash=cash, total=grand_total)


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    rows = db.execute(
        "SELECT symbol, shares, price,transacted FROM transactions WHERE user_id = ? ORDER BY transacted DESC",
        user_id
    )

    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol")
        shares = request.form.get("shares")
        if not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")
        shares = int(shares)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol")

        row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = row[0]["cash"]

        total = shares * stock["price"]
        if total > cash:
            return apology("cannot afford")

        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total, session["user_id"])
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], stock["symbol"], shares, stock["price"]
        )

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide symbol")

        stock = lookup(symbol)

        if stock is None:
            return apology("invalid symbol")

        return render_template("quoted.html", stock=stock)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if password != confirmation:
            return apology("passwords don't match")

        hash = generate_password_hash(password)

        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
            )
        except ValueError:
            return apology("username already exists")

        session["user_id"] = new_user

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("choose correct symbol")
        shares = request.form.get("shares")
        if not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")
        shares = int(shares)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol")

        row = db.execute(
            "SELECT SUM(shares) as total FROM transactions WHERE user_id = ? AND symbol = ?",
            session["user_id"], symbol
        )
        owned = row[0]["total"]

        if owned is None or owned < shares:
            return apology("you don't own that many shares")

        total = shares * stock["price"]

        # Update cash and record transaction
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total, session["user_id"])
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], symbol, -shares, stock["price"]
        )

        # Redirect to home page
        return redirect("/")

    else:
        rows = db.execute("""
            SELECT symbol, SUM(shares) as total_shares
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0
        """, session["user_id"])
        return render_template("sell.html", rows=rows)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not current_password:
            return apology("must provide current password")
        if not new_password:
            return apology("must provide new password")
        if new_password != confirmation:
            return apology("passwords don't match")

        row = db.execute("SELECT hash FROM users WHERE id = ?",
                         session["user_id"])
        if not check_password_hash(row[0]["hash"], current_password):
            return apology("invalid current password")

        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   new_hash, session["user_id"])

        flash("Password changed successfully!")
        return redirect("/")

    else:
        return render_template("password.html")
