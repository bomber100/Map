import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
#from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

app = Flask(__name__)
con = sqlite3.connect('map.db', check_same_thread=False)
db = con.cursor()
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()
    #print("login")
    if request.method == "POST":
        #print("post")
        if not request.form.get("username"):
            return render_template("error.html", error = "Must provide username")

        elif not request.form.get("password"):
            return render_template("error.html", error = "Must provide password")

        username = str(request.form.get("username"))
        #print(username)
        rows = db.execute("SELECT id, hash FROM users WHERE username = ?", ([username])).fetchone()
        #print(rows)

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[1], request.form.get("password")):
            return render_template("error.html", error = "Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("get")
        return render_template("login.html")

@app.route("/")
def index():
    visibility = ""
    register = "class=hidden"
    admin = False
    adminVisibility = "class=hidden"
    #print(str(session))
    if (str(session) == "<FileSystemSession {}>"):
        visibility = "class=hidden"
        register = ""
        print("something")
    else:
        user_id = session["user_id"]
        role = db.execute("SELECT role FROM users WHERE id = ?", ([user_id])).fetchone()
        if role[0] == "admin":
            admin = True
    markers = []
    types = db.execute("SELECT id, type FROM types ORDER BY id").fetchall()

    if admin == True:
        reportedMarkers = db.execute("SELECT name, lat, lng FROM units").fetchall()
        adminVisibility = ""
        print("admin")
        for marker in reportedMarkers:
            m = {'name': marker[0], 'location': [marker[1], marker[2]]}
            markers.append(m)

    return render_template("index.html", visibility=visibility, register=register, types=types, markers=markers, adminVisibility=adminVisibility)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", ([request.form.get("username")])).fetchone()
        if not request.form.get("username"):
            return render_template("error.html", error = "Must provide username")

        elif not request.form.get("password"):
            return render_template("error.html", error = "Must provide password")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", error = "Passwords don`t match")

        elif not request.form.get("country"):
            return render_template("error.html", error = "Must provide country")

        elif rows != None:
            return render_template("error.html", error = "This username is already taken")
        print(str(request.form.get("username")))

        db.execute("INSERT INTO users(username, hash, country) values(?, ?, ?)", [(str(request.form.get("username"))),
        (str(generate_password_hash(request.form.get("password")))), str(request.form.get("country"))])
        con.commit()

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/report", methods=["GET", "POST"])
def report():
    if not request.form.get("lat"):
        return render_template("error.html", error = "Must provide latitude")
    # elif not request.form.get("country"):
    #     return render_template("error.html", error = "Must provide country")
    elif not request.form.get("lat"):
        return render_template("error.html", error = "Must provide longitude")
    elif not request.form.get("type"):
        return render_template("error.html", error = "Must provide type")
    elif not request.form.get("amount"):
        return render_template("error.html", error = "Must provide amount")
    elif not request.form.get("name"):
        return render_template("error.html", error = "Must provide name")

    elif len(str(request.form.get("comment"))) > 1000:
        return render_template("error.html", error = "The comment is too long")

    reportedType = request.form.getlist("type")
    unitType = ""
    for i in reportedType:
        unitType += i
    lat = str(request.form.get("lat"))
    lng = str(request.form.get("lng"))
    amount = int(request.form.get("amount"))
    unit_id = tracker(lat, lng, amount, unitType)

    if unit_id == -1:
        db.execute("INSERT INTO units(name, lat, lng, amount, type, country, comment) values(?, ?, ?, ?, ?, ?, ?)", [(str(request.form.get("name"))),
            lat, lng, amount, unitType, str(request.form.get("country")), str(request.form.get("comment"))])
    else:
        db.execute("UPDATE units SET lat = ?, lng = ?, amount = ? WHERE id = ?", [lat, lng, amount, unit_id])
    con.commit()

    return redirect("/")

def tracker(lat, lng, amount, unitType):
    # To be continued...
    return -1



# @app.route("/add")
# def add():
#     if not request.form.get("add"):

@app.route("/typechange")
def typechange():
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    types = db.execute("SELECT type FROM types ORDER BY id").fetchall()
    return render_template("typechange.html", types = types)
