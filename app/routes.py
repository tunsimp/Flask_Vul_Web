# app/routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from . import db
from .models import User
from .utils import is_valid_input
from sqlalchemy import text  # Import text for raw SQL queries

routes = Blueprint('routes', __name__)

@routes.route("/")
def home():
    if "user" in session:
        user = session['user']
        return render_template("index.html", username=user)
    else:
        return redirect(url_for('routes.login'))

@routes.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['password']
        
        
        # Vulnerable SQL Query
        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        try:
            result = db.session.execute(query).fetchone()
        except Exception as e:
            # In real applications, log the exception
            return render_template("login.html", message="An error occurred. Please try again.")
        
        if result:
            session['user'] = username
            session.permanent = True  # Apply session lifetime
            return redirect(url_for('routes.home'))
        else:
            return render_template("login.html", message="Invalid username or password.")
    else:
        return render_template("login.html")

@routes.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        MAX_USERNAME_LENGTH = 50
        MAX_PASSWORD_LENGTH = 50
        username = request.form['name'][:MAX_USERNAME_LENGTH]
        password = request.form['password'][:MAX_PASSWORD_LENGTH]
        repassword = request.form['repassword'][:MAX_PASSWORD_LENGTH]
        
        if not username or not password:
            return render_template("register.html", message="Please fill out all fields.")

        # Validate username format
        if not is_valid_input(username):
            return render_template("register.html", message="Username must be alphanumeric.")

        # Check if passwords match
        if password != repassword:
            return render_template("register.html", message="Passwords do not match.")

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", message="Username already exists.")
        
        # Create a new user (password stored in plain text for demonstration)
        new_user = User(username=username, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("routes.login"))
        except Exception as e:
            # In real applications, log the exception
            return render_template("register.html", message="Registration failed. Please try again.")
    else:
        return render_template("register.html")

@routes.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('routes.login'))
