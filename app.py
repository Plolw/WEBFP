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


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def hello():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    #Clear session
    session.clear()

    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("password") !=  request.form.get("confirm_password"):
            error = "*Password validation incorrect"
            return render_template("register.html", error=error)
        return redirect("/")
    else:
        return render_template("register.html")
    