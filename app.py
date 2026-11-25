from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

transactions = []


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
            transactions.append({
                "description": description,
                "amount": amount,
                "type": transaction_type,
            })

        return redirect(url_for("home"))

    return render_template("index.html", transactions=transactions)


if __name__ == "__main__":
    app.run(debug=True)