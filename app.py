import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = Path(__file__).with_name("finance.db")

CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Salary", "Other"]


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category TEXT NOT NULL DEFAULT 'Other'
            )
        """)

        # Add the category column to a database created on Day 4.
        columns = connection.execute(
            "PRAGMA table_info(transactions)"
        ).fetchall()

        if not any(column["name"] == "category" for column in columns):
            connection.execute(
                "ALTER TABLE transactions "
                "ADD COLUMN category TEXT NOT NULL DEFAULT 'Other'"
            )


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount_text = request.form.get("amount", "").strip()
        transaction_type = request.form.get("type", "")
        category = request.form.get("category", "")

        try:
            amount = float(amount_text)
        except ValueError:
            amount = 0

        if (
            description
            and amount > 0
            and transaction_type in ("income", "expense")
            and category in CATEGORIES
        ):
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO transactions
                        (description, amount, type, category)
                    VALUES (?, ?, ?, ?)
                    """,
                    (description, amount, transaction_type, category),
                )

        return redirect(url_for("home"))

    with get_connection() as connection:
        transactions = connection.execute(
            """
            SELECT id, description, amount, type, category
            FROM transactions
            ORDER BY id DESC
            """
        ).fetchall()

        totals = connection.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0)
                    AS income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0)
                    AS expenses
            FROM transactions
            """
        ).fetchone()

    balance = totals["income"] - totals["expenses"]

    return render_template(
        "index.html",
        transactions=transactions,
        income=totals["income"],
        expenses=totals["expenses"],
        balance=balance,
        categories=CATEGORIES,
    )


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)