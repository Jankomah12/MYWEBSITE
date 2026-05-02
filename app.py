from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "messages.db")

# Create database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                      (name, email, message))
        conn.commit()
        conn.close()

        return render_template("success.html", name=name)
    return render_template("contact.html")

@app.route("/messages")
def view_messages():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages")
        messages = cursor.fetchall()
        conn.close()
        return render_template("messages.html", messages=messages)
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize database
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
