from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '4986487tgjh54gkl5748685g43987n'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
Session(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"
    
class Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String, nullable=False)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def hello():
    if session.get("user_id") is not None:
        return redirect("/index")
    return render_template("startscreen.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    #Clear session
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).all()
        if len(user) != 1 or not check_password_hash(user[0].password, password):
            error = "*Invalid password or username"
            return render_template("login.html", error=error)
        session["user_id"] = user[0].id
        return redirect("/index")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("password") !=  request.form.get("confirm_password"):
            error = "*Password validation incorrect"
            return render_template("register.html", error=error)
        else:
            username = request.form.get("username")
            password = generate_password_hash(request.form.get("password"))
            usertaken = User.query.filter_by(username=username).all()
            if len(usertaken) > 0:
                error = "*Username taken"
                return render_template("register.html", error=error)
            else:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                session["user_id"] = user.id
        return redirect("/index")
    else:
        return render_template("register.html")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")
