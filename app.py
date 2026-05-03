 from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "joel_secret_key_2026"

DB_PATH = os.path.join(os.path.dirname(__file__), "messages.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message, timestamp) VALUES (?, ?, ?, ?)",
                      (name, email, message, timestamp))
        conn.commit()
        conn.close()
        return render_template("success.html", name=name)
    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                          (username, password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except:
            return render_template("register.html", error="Username already exists!")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["username"] = username
            flash(f"Welcome back {username}!", "success")
            return redirect(url_for("view_messages"))
        else:
            return render_template("login.html", error="Wrong username or password!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("home"))

@app.route("/messages")
def view_messages():
    if "username" not in session:
        flash("Please login to view messages!", "error")
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    count = len(messages)
    conn.close()
    return render_template("messages.html", messages=messages,
                          username=session["username"], count=count)

@app.route("/delete/<int:id>")
def delete_message(id):
    if "username" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Message deleted!", "success")
    return redirect(url_for("view_messages"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(debug=False, port=7000)
