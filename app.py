import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
    id = session["user_id"]
    query = db.execute("SELECT * FROM (SELECT stock, sum(value) as value, sum(quantity) as quantity, CAST(sum(value) AS FLOAT)/sum(quantity) as price FROM buy WHERE user = ? GROUP BY stock) WHERE quantity !=0", id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    return render_template("index.html", item=query, cash=cash)
