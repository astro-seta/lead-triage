import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for
from db import get_conn, init_db
from ai import triage

load_dotenv()
app = Flask(__name__)
init_db()
SECRET = os.getenv("WEBHOOK_SECRET", "")


def process_lead(name, email, message):
    """Send the message to the AI, then save the result in the database."""
    try:
        data, tokens_in, tokens_out = triage(name, email, message)
        row = (name, email, message, data["category"], data["urgency"],
               data["summary"], data["suggested_reply"],
               tokens_in, tokens_out, "ok", None)
    except Exception as e:
        row = (name, email, message, None, None, None, None,
               0, 0, "error", str(e))

    with get_conn() as c:
        c.execute("""INSERT INTO leads
            (name, email, message, category, urgency, summary, suggested_reply,
             input_tokens, output_tokens, status, error)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", row)
    return row[9]


@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent = False
    if request.method == "POST":
        process_lead(request.form.get("name"),
                     request.form.get("email"),
                     request.form.get("message"))
        sent = True
    return render_template("contact.html", sent=sent)


@app.post("/webhook/lead")
def webhook():
    if request.headers.get("X-Webhook-Secret") != SECRET:
        return jsonify(error="unauthorized"), 401

    p = request.get_json(silent=True) or {}
    name, email, message = p.get("name"), p.get("email"), p.get("message")
    if not message:
        return jsonify(error="message is required"), 400

    status = process_lead(name, email, message)
    return jsonify(status=status), (200 if status == "ok" else 502)


@app.get("/")
def dashboard():
    with get_conn() as c:
        leads = c.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
        stats = c.execute(
            "SELECT category, COUNT(*) AS n FROM leads "
            "WHERE category IS NOT NULL GROUP BY category").fetchall()
        usage = c.execute(
            "SELECT COALESCE(SUM(input_tokens),0) AS i, "
            "COALESCE(SUM(output_tokens),0) AS o, "
            "COALESCE(SUM(status='error'),0) AS errs FROM leads").fetchone()
    return render_template("dashboard.html", leads=leads, stats=stats, usage=usage)


if __name__ == "__main__":
    app.run(debug=True)