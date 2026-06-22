from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from services.insights import generate_insights
import csv
import os
import io
import requests
import yfinance as yf
from collections import defaultdict
app = Flask(__name__)

# ------------------------
# DB
# ------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # THIS LINE FIXES LOCKING
    conn.execute("PRAGMA journal_mode=WAL;")

    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        date TEXT,
        description TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        monthly_limit REAL
    )
    """)

    conn.commit()
    conn.close()

# ------------------------
# Routes
# ------------------------

@app.route("/")

def index():
    conn = get_db()
    transactions = conn.execute(
        "SELECT * FROM transactions"
    ).fetchall()
    conn.close()

    return render_template("index.html", transactions=transactions)

# ------------------------
# CSV Upload
# ------------------------

@app.route("/upload", methods=["POST"])

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
        print("ROW:", row)  # 🔥 ADD THIS
        try:
            amount = row.get("amount") or row.get("Amount")
            category = row.get("category") or row.get("Category")
            date = row.get("date") or row.get("Date")
            description = row.get("description") or row.get("Description", "")

            if not amount or not category or not date:
                skipped += 1
                continue

            amount = float(amount.replace("$", "").replace(",", ""))

            conn.execute(
                "INSERT INTO transactions (amount, category, date, description) VALUES (?, ?, ?, ?)",
                (
                    amount,
                    category.strip(),
                    date,
                    description.strip()
                )
            )

            added += 1

        except Exception as e:
            print("UPLOAD ERROR:", e, row)
            skipped += 1
            continue

    conn.commit()
    conn.close()

    print(f"Uploaded {added}, skipped {skipped}")

    return redirect("/")

# ------------------------
# CATEGORY DROPDOWN 
# ------------------------

@app.route("/categories")

def categories():
    conn = get_db()

    rows = conn.execute(
        "SELECT DISTINCT category FROM transactions"
    ).fetchall()

    conn.close()

    return jsonify([row["category"] for row in rows])

# ------------------------
# APIs
# ------------------------

@app.route("/chart-data")

def chart_data():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE category = ?",
            (category,)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions"

        ).fetchall()

    conn.close()

    data = {}
    for t in transactions:
        data[t["category"]] = data.get(t["category"], 0) + float(t["amount"] or 0)

    return jsonify(data)


@app.route("/monthly-data")

def monthly_data():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE category = ?",
            (category,)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions"
        ).fetchall()

    conn.close()

    months = {}
    for t in transactions:
        key = t["date"][:7]
        months[key] = months.get(key, 0) + float(t["amount"] or 0)

    return jsonify(dict(sorted(months.items())))


@app.route("/insights")
def insights():
    category = request.args.get("category")

    conn = get_db()

    if category:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE category = ?",
            (category,)
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT * FROM transactions"
        ).fetchall()

    all_transactions = conn.execute(
        "SELECT * FROM transactions"
    ).fetchall()

    budgets = conn.execute(
    "SELECT * FROM budgets"
    ).fetchall()

    conn.close()

    return jsonify(
        generate_insights(
            transactions,
            all_transactions,
            budgets
        )
    )

@app.route("/budget-status")
def budget_status():
    
    conn = get_db()

    budgets = conn.execute(
        "SELECT * FROM budgets"
    ).fetchall()
    transactions = conn.execute(
        "SELECT * FROM transactions"
    ).fetchall()
    conn.close()
    current_month = max(
        t["date"][:7]
        for t in transactions
    )

    category_totals = defaultdict(float)

    for t in transactions:
        if t["date"].startswith(current_month):
            if float(float(t["amount"] or 0)) > 0:
                category_totals[
                    t["category"].strip().lower()
                ] += float(float(t["amount"] or 0))

    results = []

    for budget in budgets:
        category = budget["category"]
        limit = float(
            budget["monthly_limit"]
        )
        spent = category_totals.get(
            category.strip().lower(),
            0
        )
        percent = 0
        if limit > 0:
            percent = round(
                (spent / limit) * 100,
                1
            )
        results.append({
            "id": budget["id"],
            "category": category,
            "spent": spent,
            "limit": limit,
            "percent": percent
        })

    return jsonify(results)

@app.route("/delete-budget", methods=["POST"])
def delete_budget():

    budget_id = request.form["id"]

    conn = get_db()

    conn.execute(
        "DELETE FROM budgets WHERE id = ?",
        (budget_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})

    
@app.route("/ai-summary")
def ai_summary():
    conn = get_db()

    transactions = conn.execute(
        "SELECT * FROM transactions"
    ).fetchall()

    conn.close()

    if not transactions:
        return jsonify({
            "summary": "No transaction data available yet."
        })

    insights = generate_insights(transactions)

    # ------------------------
    # Build Financial Summary
    # ------------------------

    category_totals = {}

    for t in transactions:
        category_totals[t["category"]] = (
            category_totals.get(t["category"], 0)
            + float(t["amount"] or 0)
        )

    summary_text = "\n".join(insights)

    category_text = "\n".join([
        f"{k}: ${v:.2f}"
        for k, v in category_totals.items()
    ])

    prompt = f"""
You are a financial assistant.

Analyze this user's spending activity and provide a short helpful summary.

Financial Insights:
{summary_text}

Category Totals:
{category_text}

Rules:
- Keep response concise
- Use bullet points
- Focus on trends and observations
- Do not invent fake data
- Be practical and helpful
"""
    print("Sending prompt to Ollama...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        data = response.json()
        print("Received AI response")

        return jsonify({
            "summary": data["response"]
        })

    except Exception as e:
        return jsonify({
            "summary": f"AI error: {str(e)}"
        })

# ------------------------
# TRANSACTIONS
# ------------------------

@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    conn.execute(
        "INSERT INTO transactions (amount, category, date, description) VALUES (?, ?, ?, ?)",
        (
            request.form["amount"],
            request.form["category"],
            request.form["date"],
            request.form["description"]
        )
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

import time

@app.route("/reset", methods=["POST"])

def reset():
   

    for attempt in range(3):
        try:
            conn = get_db()

            conn.execute(
                "DELETE FROM transactions",
            )

            conn.commit()
            conn.close()

            print("Reset successful")
            return redirect("/")

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"DB locked, retrying... ({attempt})")
                time.sleep(1)
            else:
                raise e

    return "Database busy, try again"

# ------------------------
# WATCHLIST
# ------------------------

@app.route("/add-stock", methods=["POST"])

def add_stock():
    ticker = request.form["ticker"].upper()

    conn = get_db()
    conn.execute(
        "INSERT INTO stocks (ticker) VALUES (?)",
        (ticker,)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/get-stocks")
def get_stocks():

    conn = get_db()

    stocks = conn.execute(
        "SELECT * FROM stocks"
    ).fetchall()

    conn.close()

    results = []

    for stock in stocks:

        ticker = stock["ticker"]

        try:

            data = yf.Ticker(ticker)

            info = data.fast_info

            price = info.get("lastPrice", 0)

            previous = info.get("previousClose", price)

            change = 0

            if previous:
                change = (
                    (price - previous)
                    / previous
                ) * 100

            results.append({

                "id": stock["id"],

                "ticker": ticker,

                "price": round(price, 2),

                "change": round(change, 2)

            })

        except Exception as e:

            print("Stock error:", ticker, e)

            results.append({

                "id": stock["id"],

                "ticker": ticker,

                "price": "N/A",

                "change": 0

            })

    return jsonify(results)

@app.route("/delete-stock", methods=["POST"])
def delete_stock():
    stock_id = request.form["id"]

    conn = get_db()
    conn.execute(
        "DELETE FROM stocks WHERE id = ?",
        (stock_id,)
    )
    conn.commit()
    conn.close()

    return redirect("/")

    

# ------------------------
# Transaction Table
# ------------------------
@app.route("/transactions")
def transactions():
    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM transactions
        ORDER BY date DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])

@app.route("/delete-transaction", methods=["POST"])
def delete_transaction():
    transaction_id = request.form["id"]

    conn = get_db()

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/update-transaction", methods=["POST"])
def update_transaction():
    transaction_id = request.form["id"]

    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form["description"]
    date = request.form["date"]

    conn = get_db()

    conn.execute("""
        UPDATE transactions
        SET amount = ?,
            category = ?,
            description = ?,
            date = ?
        WHERE id = ?
    """, (
        amount,
        category,
        description,
        date,
        transaction_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/add-budget", methods=["POST"])
def add_budget():

    category = request.form.get(
        "category",
        ""
    ).strip()

    limit = request.form.get(
        "limit",
        ""
    ).strip()

    if not category or not limit:
        return jsonify({
            "error": "Missing category or limit"
        }), 400

    try:
        limit = float(limit)
    except ValueError:
        return jsonify({
            "error": "Invalid limit"
        }), 400

    conn = get_db()

    conn.execute(
        """
        INSERT INTO budgets
        (category, monthly_limit)
        VALUES (?, ?)
        """,
        (
            category,
            limit
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })

@app.route("/get-budgets")
def get_budgets():

    conn = get_db()

    budgets = conn.execute(
        "SELECT * FROM budgets"
    ).fetchall()

    conn.close()

    return jsonify([dict(b) for b in budgets])

# ------------------------
# RUN APP (DO NOT REMOVE)
# ------------------------

import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)