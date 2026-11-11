import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DB_PATH = os.path.join(os.path.dirname(__file__), "ciphershield.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','manager','user'))
    )""")
    # Demo administrator; change this password after first login.
    existing = db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if not existing:
        db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                   ("admin", generate_password_hash("Admin@123"), "admin"))
    db.commit()
    db.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if session.get("role") not in allowed_roles:
                return render_template("denied.html"), 403
            return view(*args, **kwargs)
        return decorator_wrapper(wrapped)
    return decorator

def decorator_wrapper(view):
    return view

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8:
            flash("Username must have 3+ characters and password must have 8+ characters.")
            return redirect(url_for("register"))
        try:
            get_db().execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'user')",
                (username, generate_password_hash(password))
            )
            get_db().commit()
            flash("Account created. You can now log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already taken.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
@roles_required("admin")
def admin_panel():
    users = get_db().execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    return render_template("admin.html", users=users)

@app.route("/admin/create-manager", methods=["POST"])
@roles_required("admin")
def create_manager():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if len(username) < 3 or len(password) < 8:
        flash("Manager username must have 3+ characters and password 8+ characters.")
    else:
        try:
            get_db().execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'manager')",
                (username, generate_password_hash(password))
            )
            get_db().commit()
            flash("Manager account created.")
        except sqlite3.IntegrityError:
            flash("That username already exists.")
    return redirect(url_for("admin_panel"))

@app.route("/manage")
@roles_required("admin", "manager")
def manage():
    users = get_db().execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    return render_template("manage.html", users=users)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
