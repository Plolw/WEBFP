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

app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    courses = db.relationship('Course', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"
    
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.Column(db.String(50), nullable=True)
    subjects = db.relationship('Subject', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.course}')"
    
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=True)
    divisions = db.Column(db.String, nullable=True)
    grades = db.relationship('Grade', backref='subject', lazy=True)

    def __repr__(self):
        return f"Table('{self.subject}')"

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    division = db.Column(db.String(50), nullable=True)
    grade = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"Table('{self.division}', '{self.grade}')"
    
db.create_all()


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
    if request.method == "POST":
        #courses = Grade.query.filter_by(user_id = session["user_id"])
        selected_course = request.form.get("selected_option")
        return redirect("/index")
    else:
        #Store course selected by user
        #Query through all the DB to print it on screen
        courses = Course.query.filter_by(user_id = session["user_id"]).all()
        if not courses: #if there is no courses it would give an error so asign an empty dict to courses
            courses = {}
            return render_template("index.html", courses=courses)
        elif selected_course:
            course = Course.query.filter_by(user_id = session["user_id"], course = selected_course).first()
        else:
            c = Course.query.filter_by(user_id = session["user_id"]).first()
            selected_course = c.course
        print(selected_course)
        #Print the course on screen
        #subjects = Subject.query.filter_by(course_id = course.id).all()
        #grades = Grade.query.filter_by(user_id = session["user_id"]).all()
        #divisions = Grade.query.filter_by(user_id = session["user_id"]).distinct().all()
        return render_template("index.html", courses=courses)
        
@app.route("/NewCourse", methods=["GET", "POST"])
@login_required
def addCourse():
    if request.method == "POST":
        course_name = request.form.get("course_name")
        course = Course(user_id = session["user_id"], course = course_name)
        db.session.add(course)
        db.session.commit()
        return redirect("/index")
    else:
        return render_template("newcourse.html")
