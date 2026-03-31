from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
from services.insights import generate_insights
import csv
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from functools import wraps
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_fallback_key")

# ------------------------
# Auth
# ------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# ------------------------
# DB
# ------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ticker TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        date TEXT,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()

# ------------------------
# Routes
# ------------------------

@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ------------------------
# CSV Upload
# ------------------------

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")

    if not file:
        return "No file uploaded"

    conn = get_db()

    stream = io.StringIO(file.read().decode("utf-8"))
    reader = csv.DictReader(stream)

    added = 0
    skipped = 0

    for row in reader:
        try:
            amount = row.get("amount")
            category = row.get("category")
            date = row.get("date")
            description = row.get("description", "")

            if not amount or not category or not date:
                skipped += 1
                continue

            amount = float(amount)

            conn.execute(
                "INSERT INTO transactions (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (
                    session["user_id"],
                    amount,
                    category.strip(),
                    date,
                    description.strip()
                )
            )

            added += 1

        except:
            skipped += 1
            continue

    conn.commit()
    conn.close()

    print(f"Uploaded {added}, skipped {skipped}")

    return redirect("/")

# ------------------------
# CATEGORY DROPDOWN (FIX #1)
# ------------------------

@app.route("/categories")
@login_required
def categories():
    conn = get_db()

    rows = conn.execute(
        "SELECT DISTINCT category FROM transactions WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return jsonify([row["category"] for row in rows])

# ------------------------
# APIs
# ------------------------

@app.route("/chart-data")
@login_required
def chart_data():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND category = ?",
            (session["user_id"], category)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()

    conn.close()

    data = {}
    for t in transactions:
        data[t["category"]] = data.get(t["category"], 0) + t["amount"]

    return jsonify(data)


@app.route("/monthly-data")
@login_required
def monthly_data():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND category = ?",
            (session["user_id"], category)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()

    conn.close()

    months = {}
    for t in transactions:
        key = t["date"][:7]
        months[key] = months.get(key, 0) + t["amount"]

    return jsonify(dict(sorted(months.items())))


@app.route("/insights")
@login_required
def insights():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND category = ?",
            (session["user_id"], category)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()

    all_transactions = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return jsonify(generate_insights(transactions, all_transactions))

# ------------------------
# TRANSACTIONS
# ------------------------

@app.route("/add", methods=["POST"])
@login_required
def add():
    conn = get_db()
    conn.execute(
        "INSERT INTO transactions (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (
            session["user_id"],
            request.form["amount"],
            request.form["category"],
            request.form["date"],
            request.form["description"]
        )
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/reset", methods=["POST"])
@login_required
def reset():
    conn = get_db()
    conn.execute(
        "DELETE FROM transactions WHERE user_id = ?",
        (session["user_id"],)
    )
    conn.commit()
    conn.close()

    return redirect("/")

# ------------------------
# WATCHLIST
# ------------------------

@app.route("/add-stock", methods=["POST"])
@login_required
def add_stock():
    ticker = request.form["ticker"].upper()

    conn = get_db()
    conn.execute(
        "INSERT INTO stocks (user_id, ticker) VALUES (?, ?)",
        (session["user_id"], ticker)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/get-stocks")
@login_required
def get_stocks():
    conn = get_db()

    stocks = conn.execute(
        "SELECT * FROM stocks WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return jsonify([dict(s) for s in stocks])

@app.route("/delete-stock", methods=["POST"])
@login_required
def delete_stock():
    stock_id = request.form["id"]

    conn = get_db()
    conn.execute(
        "DELETE FROM stocks WHERE id = ? AND user_id = ?",
        (stock_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/")

# ------------------------
# AUTH
# ------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (
                    request.form["username"],
                    generate_password_hash(request.form["password"])
                )
            )
            conn.commit()
        except:
            return "User already exists"

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (request.form["username"],)
        ).fetchone()

        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            return redirect("/")
        return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")

# ------------------------
# RUN APP (DO NOT REMOVE)
# ------------------------

import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)