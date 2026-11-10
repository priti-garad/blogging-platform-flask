
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "blogging_platform_secret_key"

DATABASE = "blog.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            flash("Registration successful! Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username already exists!")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("home"))

        flash("Invalid username or password!")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/create", methods=["GET", "POST"])
def create_post():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db()
        conn.execute(
            "INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
            (title, content, session["username"])
        )
        conn.commit()
        conn.close()

        flash("Blog post created successfully!")
        return redirect(url_for("home"))

    return render_template("create_post.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
