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
    selected = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Course('{self.course}', '{self.selected}')"

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subject = db.Column(db.String(25), nullable=True)
    divisions = db.relationship('Division', backref='subject', lazy=True)
    
    def __repr__(self):
        return f"Subject('{self.subject}')"
    
class Division(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    division = db.Column(db.String(20), nullable=True)
    grades = db.relationship('Grade', backref='division', lazy=True)

    def __repr__(self):
        return f"Division('{self.division}')"
    
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=True)
    percentage = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Grade('{self.grade}', '{self.percentage}')"
    
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
        #Store selected course by user
        selected_course_id = int(request.form.get("selected_option"))

        #Update "selected" to false on all columns
        Course.query.filter_by(user_id = session["user_id"]).update({"selected": False})

        #Update "selected" to true on the selected course
        selected_course = Course.query.filter_by(id = selected_course_id).first()
        selected_course.selected = True

        db.session.commit()

        #Check for new subjects


        return redirect("/index")
    else:
        #Query through all the DB to print it on the dropdown
        courses = Course.query.filter_by(user_id = session["user_id"]).all()
        course = Course.query.filter_by(user_id = session["user_id"], selected = True).first()

        #Query through all the course DB to print it on the table
        subjects = course.subjects
        divisions = Division.query.all()
        grades = Grade.query.all()
        if len(course.subjects) < 1:
            div2 = []
            return render_template("index.html", div2=div2, courses=courses, divisions=divisions, subjects = subjects, grades = grades)
        div2 = course.subjects[0].divisions

        #Get the SB overalls
        overall_list = []
        currentSb = 0
        i = 0
        for subject in subjects:
            col = subject.divisions
            for div in col:
                for grade in grades:
                    if grade.division_id == div.id:
                        currentSb += grade.grade * (grade.percentage / 100)
                        i += 1
                overall_list.append(currentSb / i)
        #Get the DIV overalls


        return render_template("index.html", div2=div2, courses=courses, divisions=divisions, subjects = subjects, grades = grades)
        
@app.route("/NewCourse", methods=["GET", "POST"])
@login_required
def addCourse():
    if request.method == "POST":
        course_name = request.form.get("course_name")
        courses = Course.query.filter_by(user_id = session["user_id"]).all()
        if not courses:
            course = Course(user_id = session["user_id"], course = course_name, selected = True)
        else:
            course = Course(user_id = session["user_id"], course = course_name, selected = False)
        db.session.add(course)
        db.session.commit()
        return redirect("/index")
    else:
        return render_template("newcourse.html")
    
@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def addSubject():
    if request.method == "POST":
        subject = request.form.get("subject_input")
        course = Course.query.filter_by(user_id = session["user_id"], selected = True).first()
        if len(course.subjects) < 1:
            sub = Subject(course_id = course.id, subject = subject)
            db.session.add(sub)
            db.session.commit()
            return redirect("/index")
        divisions = course.subjects[0].divisions
        sub = Subject(course_id = course.id, subject = subject)
        db.session.add(sub)
        db.session.commit()
        for division in divisions:
            div = Division(subject_id = sub.id, division = division.division)
            db.session.add(div)
            db.session.commit()
            grade = request.form.get(f"{division.id}_grade")
            percentage = request.form.get(f"{division.id}_grade_percentage")
            row = Grade(division_id = div.id, grade = grade, percentage = percentage)
            db.session.add(row)
            db.session.commit()
        return redirect("/index")
    else:
        course = Course.query.filter_by(user_id = session["user_id"], selected = True).first()
        if len(course.subjects) < 1:
            return render_template("/add_subject.html")
        else:
            divisions = course.subjects[0].divisions
            return render_template("/add_subject.html", divisions=divisions)

@app.route("/add_division", methods=["GET", "POST"])
@login_required
def addDivision():
    if request.method == "POST":
        course = Course.query.filter_by(user_id = session["user_id"], selected = True).first()
        name = request.form.get("division_input")
        for subject in course.subjects:
            div = Division(subject_id = subject.id, division = name)
            db.session.add(div)
        db.session.commit()
        return redirect("/index")
    else:
        return render_template("/add_division.html")
    

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    btn_id = request.form.get('deletebtn')
    
    #Delete subject
    sub = Subject.query.filter_by(id=btn_id).first()
    
    #Delete divisions
    div = Division.query.filter_by(subject_id=btn_id).all()

    for div in div:
        grd = Grade.query.filter_by(division_id=div.id).first()
        if grd:
            db.session.delete(grd)
            db.session.commit()
    
    div = Division.query.filter_by(subject_id=btn_id).all()
    for div in div:
        db.session.delete(div)
        db.session.commit()

    
    db.session.delete(sub)
    db.session.commit()

    return redirect("/index")
