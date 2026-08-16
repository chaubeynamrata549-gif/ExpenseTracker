from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "expenses.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():

    conn = get_db()

    expenses = conn.execute("""
        SELECT * FROM expenses
        ORDER BY date DESC, id DESC
    """).fetchall()

    total = sum(float(e["amount"]) for e in expenses)
    count = len(expenses)

    if count > 0:
        average = total / count
    else:
        average = 0

    category_totals = {}

    for expense in expenses:
        category = expense["category"]
        amount = float(expense["amount"])

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        count=count,
        average=average,
        category_totals=category_totals
    )


@app.route("/add", methods=["POST"])
def add_expense():

    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]

    conn = get_db()

    conn.execute("""
        INSERT INTO expenses (name, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (name, amount, category, date))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete_expense(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):

    conn = get_db()

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    ).fetchone()

    if expense is None:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":

        name = request.form["name"]
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        conn.execute("""
            UPDATE expenses
            SET name = ?, amount = ?, category = ?, date = ?
            WHERE id = ?
        """, (name, amount, category, date, id))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()

    return render_template(
        "edit.html",
        expense=expense
    )


@app.route("/clear")
def clear_expenses():

    conn = get_db()

    conn.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)