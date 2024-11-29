from flask import Flask,render_template,request,session,redirect,url_for
from datetime import timedelta
app= Flask(__name__)
app.debug = True
app.secret_key="2208"
app.permanent_session_lifetime=timedelta(minutes=5)

@app.route("/")
def home():
    if "user" in session:
        user=session['user']
        return render_template("index.html",username=user)
    else: 
        return redirect(url_for('login'))

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form['name']
        password=request.form['password']
        if username==password:
            session['user']=username
            return redirect(url_for('home'))
        else: 
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST","GET"])
def register():
    if request.method=="POST":
        username=request.form['name']
        password=request.form['password']
        repassword=request.form['repassword']
        if username or password==repassword:
            return render_template("login.html")
        else: 
            return render_template("register.html")
    elif request.method=="GET":
        return render_template("register.html")
    else: 
        return "Invalid Method"

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for('login'))

if __name__=="__main__":
    app.run()