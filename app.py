import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = Path(__file__).with_name("finance.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense'))
            )
        """)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount_text = request.form.get("amount", "").strip()
        transaction_type = request.form.get("type", "")

        try:
            amount = float(amount_text)
        except ValueError:
            amount = 0

        if description and amount > 0 and transaction_type in ("income", "expense"):
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO transactions (description, amount, type)
                    VALUES (?, ?, ?)
                    """,
                    (description, amount, transaction_type),
                )

        return redirect(url_for("home"))

    with get_connection() as connection:
        transactions = connection.execute(
            "SELECT description, amount, type FROM transactions ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", transactions=transactions)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)