# GRADES: A webpage to store and calculate your grades
### Video Demo: <URL HERE>
### Description:
My project consists of a webpage where you can create an account to store, visualize and calculate your grades from school, university or whatever you want.

It has been made using using python, html, css and SQL (flask's sqlalchemy). All of this inside a flask framework.
The 3 main functionalities are:
  - User authentification --> Creating, storing and validating usernames and passwords.
  - Storing your grades in 'courses' --> Creating courses wich are tables in wich to store your grades divided by subject and division (this can mean anything, but it's purpose is to divide the grades into trimesters or semesters).
  - Visualizing your grades in a table --> All the grades you stored will be visible (with their overalls) on screen depending on wich course you decide to show

Obviously there are lots of small functionalities like calculating the overall grade of the course or deleting subjects from the database but these can be categorized inside the main 3.

## Basic info
The project is, as I said, run in a flask framework. Inside app.py is all the python written logic of the webpage, the back-end. There also is declared the structure of the database written using the flask's SQLAlchemy library (database stored in the instance folder as web.db). This comunicates via jinja sintax with the front-end wich is written using html and css and is stored in the static and templates folders.

## Database
This database is a relationad DB and it is divided into 5 different tables to store all the necessary information:
 - User --> contains a username, a password and a courses columns.
 - Course --> contains a course, a selected (to know wich course to show on screen) and a subjects column.
 - Subject --> contains a subject and a divisions columns.
 - Division --> contains a division name and a grades columns.
 - Grade --> contains a grade and a percentage columns.

## Functionalities

**User authentification:** When registering, the username and the password are taken with 'request.form.get' from the fields created in html and stored in two variables. Then these are added to the database into a new row. And when logging in the input is also taken from 2 text fields and queried through the database to try and find coincidences. If there aren't any the user isn't let into the index page, if the is one coincidence the user ir redirected to the index page.

**Storing your grades in courses:** When creating a new division it is needed that a subject alredy exists since these are linked in the database to the subjects. So first of all the user must create a subject wich is stores without any divisions atached to it. Then it is eliminated after creating other subjects. When a new division is created it is stored with an external key linking to the first subject on the selected course, then created for all the other subjects.
When creating a subject using again the 'request.form.get' we fetch the user inputs (wich are generated dinamically based on how many divisions there are) and create a new subject row in the subject database. Then wich the fetched grades and percentages new grades are created on the grade database with an external key linking them to their division.

**Visualizing your grades in a table:** Upon sending a 'GET request' to index a table is rendered showing all the grades and subjects of the selected course. This course is selected by a dropdown located on the navbar wich shows all the users courses, the one selected gets it's "selected" value on the database updated to true, and all the others have this same value updated to false. The index route renders a course based on the course that has 'selected == true'. Then all the courses subjects, divisions and grades are loaded into the html. Firstly the subjects are shown, then the divisions are shown taking the ones from the first subject in the database. The divisions are shown using a for loop, and to show the grades we nest another for loop with all the grades inside the last one. This way we can check on every grade if it's division_id corresponds with the current division.id.

The overall grades are calculated adding up every grade on a subject and then every subject's overall. The first are stores in a list of dictionaries with a overall and a subject index each.
Then shown in the table checking on every subject loaded all the overalls and showing on screen the one that corresponds it.