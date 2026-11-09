import os


import sqlite3 
from helpers import apology, login_required
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

connection = sqlite3.connect('project.db')
db = connection.cursor()
db.execute(
"CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL )")
connection.commit()
connection.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    #id = session["user_id"]
    #query = db.execute("SELECT * FROM (SELECT stock, sum(value) as value, sum(quantity) as quantity, CAST(sum(value) AS FLOAT)/sum(quantity) as price FROM buy WHERE user = ? GROUP BY stock) WHERE quantity !=0", id)
    #cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id

    if session.get("user_id") is not None:
        return redirect("/")
    
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        connection = sqlite3.connect('project.db')
        db = connection.cursor()
        db.row_factory = sqlite3.Row
        db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = db.fetchone()
        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(
            rows["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        connection.close()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        connection = sqlite3.connect('project.db')
        db = connection.cursor()
        db.row_factory = sqlite3.Row

        db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )

        rows = db.fetchone()

        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure username exists and password is correct
        elif rows is not None:
            return apology("username has been taken", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("please reconfirm password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password is not consistent", 400)

        name = request.form.get("username")
        password = request.form.get("password")
        hash = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (name, hash))

        connection.commit()

        connection.close()

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "GET":
        return render_template("changepass.html")
    elif request.method == "POST":

        connection = sqlite3.connect('project.db')
        db = connection.cursor()
        db.row_factory = sqlite3.Row

        db.execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        )

        rows = db.fetchone()

        if not request.form.get("current"):
            return apology("must provide current password", 400)

        elif not check_password_hash(
            rows["hash"], request.form.get("current")
        ):
            return apology("current password incorrect", 400)

        # Ensure password was submitted
        elif not request.form.get("new"):
            return apology("must provide new password", 400)

        elif not request.form.get("confirm"):
            return apology("please reconfirm password", 400)

        elif request.form.get("confirm") != request.form.get("new"):
            return apology("password is not consistent", 400)

        password = request.form.get("new")
        hash = generate_password_hash(password)
        db.execute("UPDATE users SET hash =? where id = ?", (hash, session["user_id"]))
        connection.commit()

        connection.close()

        return redirect("/")
