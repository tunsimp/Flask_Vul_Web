# app/routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from . import db
from .models import User
from sqlalchemy import text  # Import text for raw SQL queries
from .utils import is_valid_input
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
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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
        
        # Vulnerability 1: Weak file extension validation
        # Can be bypassed with double extensions like file.php.jpg
        if file and allowed_file(file.filename):
            
            # Vulnerability 2: Path traversal - not using secure_filename()
            # Allows ../../../etc/passwd type attacks
            filename = file.filename
            
            # Vulnerability 3: No file size limit
            # Could lead to DoS attacks
            
            # Vulnerability 4: Files saved in web-accessible directory
            # Uploaded files can be directly executed
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file.save(file_path)
                
                # Vulnerability 5: Reflects user input without sanitization
                return render_template('upload.html', 
                                     message=f'File {filename} uploaded successfully!',
                                     file_url=f'/uploads/{filename}')
                
            except Exception as e:
                return render_template('upload.html', message='Upload failed')
        else:
            return render_template('upload.html', 
                                 message='File type not allowed. Only txt, pdf, png, jpg, jpeg, gif files are permitted.')
    
    return render_template('upload.html')

# Route to serve uploaded files (makes them web-accessible)
@routes.route('/uploads/<filename>')
def uploaded_file(filename):
    # Vulnerability 6: No access control on uploaded files
    # Anyone can access any uploaded file
    return send_from_directory(UPLOAD_FOLDER, filename)

@routes.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('routes.login'))
