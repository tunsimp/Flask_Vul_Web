from flask import Flask,render_template,request,session

app= Flask(__name__)
app.secret_key="2208"
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form['name']
        password=request.form['password']
        if username==password:
            return render_template("index.html")
        else: 
            return render_template("login.html")
    elif request.method=="GET":
        return render_template("login.html")
    else: 
        return "Invalid Method"

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method=="POST":
        username=request.form['name']
        password=request.form['password']
        repassword=request.form['repassword']
        if username==password:
            return render_template("login.html")
        else: 
            return render_template("register.html")
    elif request.method=="GET":
        return render_template("register.html")
    else: 
        return "Invalid Method"

if __name__=="__main__":
    app.run()