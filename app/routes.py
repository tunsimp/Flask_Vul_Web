# app/routes.py
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
from . import db
from .models import User
from sqlalchemy import text  # Import text for raw SQL queries
from .utils import is_valid_input
from datetime import datetime
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
        if not is_valid_input(username) or not is_valid_input(password):
            return render_template("login.html",message="Nuh uh! Some characters are not allowed.")
        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        try:
            result = db.session.execute(query).fetchone()
        except Exception as e:
            return render_template("login.html", message="An error occurred. Please try again!")
        
        if result:
            session['user'] = username
            session.permanent = True  
            return redirect(url_for('routes.home'))
        else:
            return render_template("login.html", message="Nuh uh! Invalid username or password.")
    else:
        return render_template("login.html")

@routes.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        if not is_valid_input(username) or not is_valid_input(password):
            return render_template("register.html",message="Nuh uh! Some characters are not allowed.")
        if password!=password2:
            return render_template("register.html",message="Passwords are not the same")
        checkquery=text(f"SELECT * FROM user WHERE username = '{username}'")
        try:
            cresult=db.session.execute(checkquery).fetchone()
        except Exception as e:
            return render_template("login.html", message="An error occurred. Please try again!")
        if cresult:
            return render_template("register.html",message="Nuh uh! Username existed.")
        query = text(f"INSERT INTO user(username,password) VALUES('{username}','{password}')")
        try:
            result = db.session.execute(query)
            db.session.commit()
        except Exception as e:
            return render_template("register.html", message="An error occurred. Please try again!")
        return render_template("login.html")
    else:
        return render_template("register.html")

# Vulnerable file upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    # Weak validation - only checks if extension exists, not actual file content
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if file was submitted
        if 'file' not in request.files:
            return render_template('upload.html', message='No file selected')
        file = request.files['file']        
        if file.filename == '':
            return render_template('upload.html', message='No file selected')
        
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)   
            try:
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file.save(file_path)
                
                return render_template('upload.html', 
                                     message=f'File {filename} uploaded successfully!',
                                     file_url=f'/uploads?filename={filename}')
            except Exception as e:
                return render_template('upload.html', message='Upload failed')
        else:
            return render_template('upload.html', 
                                 message='File type not allowed. Only png, jpg, jpeg, gif files are permitted.')
    return render_template('upload.html')

# Route to serve uploaded files (makes them web-accessible)
@routes.route('/uploads')
def uploaded_file():
    # Extract filename from query parameter
    filename = request.args.get('filename')
    if not filename:
        return "No filename provided", 400
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    print("filename=" + filename + " and path=" + file_path)
    try:
        return send_file(file_path, download_name=filename)
    except:
        return "File not found", 404

@routes.route('/archive')
def archive():
    """
    Archive page with file search functionality AND SSTI vulnerability
    """
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    
    # Get files from upload directory
    files = []
    filtered_files = []
    
    try:
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    stat_info = os.stat(file_path)
                    file_info = {
                        'name': filename,
                        'size': stat_info.st_size,
                        'modified': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    files.append(file_info)
    except Exception as e:
        print(f"Error reading upload directory: {e}")
    
    files.sort(key=lambda x: x['name'])
    
    # Handle search functionality
    search_query = request.args.get('search', '')
    search_result = ""
    
    if search_query:        
        # LEGITIMATE FILE SEARCH: Filter files by search term
        filtered_files = [f for f in files if search_query.lower() in f['name'].lower()]
        
        # SSTI VULNERABILITY: Always execute search query as template
        try:
            from jinja2 import Template
            template = Template(search_query)
            
            # Provide dangerous globals for template execution
            search_result = template.render(
                os=os,
                request=request,
            )
            # If template execution produced no output, show file search results
            if not search_result.strip():
                search_result = f"Found {len(filtered_files)} file(s) matching '{search_query}'"
                
        except Exception as e:
            search_result = f"Found {len(filtered_files)} file(s) matching '{search_query}'"
    else:
        # No search - show all files
        filtered_files = files
    
    return render_template('archive.html', 
                         files=filtered_files,  # Show filtered results
                         all_files_count=len(files),
                         request=request,
                         search_result=search_result,
                         os=os)
@routes.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('routes.login'))
