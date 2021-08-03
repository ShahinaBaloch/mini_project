#!/usr/bin/python3
import json

from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)

app.secret_key = 'super-secret-key'

##postgress
engine = create_engine("mysql+pymysql://newb:passozip@localhost:3306/proj")

db = scoped_session(
    sessionmaker(bind=engine))


@app.route("/", methods=['GET'])
def home():
    total_students = db.execute(
        "select batch_title, count(batch_title)as total_record from students group by batch_title;").fetchall()
    total = 0
    for stud in total_students:
        total = total + stud.total_record
    return render_template("home.html", total_students=total_students, total=total)


@app.route("/login", methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            students = db.execute("SELECT * FROM students").fetchall()
            return render_template("intro.html", students=students)

    return render_template('login.html', params=params)


@app.route("/index", methods=['GET'])
def index():
    return render_template("index.html")


@app.route("/intro", methods=['POST', 'GET'])
def intro():
    if request.method == "POST":
        name = request.form.get("name")
        groupmembers = request.form.get('groupmembers')
        project = request.form.get('project')
        projectdes = request.form.get('projectdes')
        supervisor = request.form.get('supervisor')
        email = request.form.get("email")
        program = request.form.get("program")
        sesion = request.form.get("sesion")
        db.execute(
            "INSERT into students(full_name, groupmembers, project, projectdes, supervisor, email, batch_title, "
            "sesion) VALUES (:full_name, :groupmembers, :project, :projectdes, :supervisor, :email, :batch_title, "
            ":sesion)",
            {"full_name": name, "groupmembers": groupmembers, "project": project, "projectdes": projectdes,
             "supervisor": supervisor, "email": email, "batch_title": program, "sesion": sesion})
        db.commit()
        # Get all records again
        students = db.execute("SELECT * FROM students").fetchall()
        return render_template("inter.html", students=students)
    else:
        students = db.execute("SELECT * FROM students").fetchall()
        return render_template("intro.html", students=students)


@app.route("/inter", methods=['GET'])
def inter():
    students = db.execute("SELECT * FROM students").fetchall()
    return render_template("inter.html", students=students)


@app.route("/view_students/<string:batch_title>/", methods=['POST', 'GET'])
def view_students(batch_title):
    stud = db.execute("SELECT * FROM students WHERE batch_title = :batch_title",
                      {"batch_title": batch_title}).fetchall()
    return render_template("cure.html", students=stud, id=id)


@app.route("/update/<int:id>/", methods=['POST', 'GET'])
def update(i):
    if request.method == "POST":
        name = request.form.get("name")
        groupmembers = request.form.get('groupmembers')
        project = request.form.get('project')
        projectdes = request.form.get('projectdes')
        supervisor = request.form.get('supervisor')
        email = request.form.get("email")
        program = request.form.get("program")
        sesion = request.form.get("sesion")
        db.execute(
            "Update students SET full_name = :name , groupmembers = :groupmembers, project = :project, "
            "projectdes=:projectdes, supervisor = :supervisor, email = :email, sesion = :sesion, batch_title = "
            ":program where id = :id",
            {"name": name, "groupmembers": groupmembers, "project": project, "projectdes": projectdes,
             "supervisor": supervisor, "email": email, "program": program, "sesion": sesion, "id": i})
        db.commit()
        return redirect(url_for('intro'))
    else:
        stud = db.execute("SELECT * FROM students WHERE id = :id", {"id": i}).fetchone()
        return render_template("update.html", stud=stud, id=i)


@app.route("/update_now/<int:id>/", methods=['POST', 'GET'])
def update_now(i):
    stud = db.execute("SELECT * FROM students WHERE id = :id", {"id": i}).fetchone()
    if stud is None:
        return "No record found by ID = " + str(i) + ". Kindly go back to <a href='/intro'> Intro </a>"
    else:
        db.execute("delete FROM students WHERE id = " + str(i))
        db.commit()
        return redirect(url_for('intro'))


@app.route("/delete/<int:id>/")
def delete(i):
    stud = db.execute("SELECT * FROM students WHERE id = :id", {"id": i}).fetchone()
    if stud is None:
        return "No record found by ID = " + str(i) + ". Kindly go back to <a href='/intro'> Intro </a>"
    else:
        db.execute("delete FROM students WHERE id = " + str(i))
        db.commit()
        return redirect(url_for('intro'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
