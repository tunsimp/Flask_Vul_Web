# app/routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from . import db
from .models import User
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


@routes.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('routes.login'))
