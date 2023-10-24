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



# mapcon = con = sqlite3.connect('map.db', check_same_thread=False)
# mapdb = mapcon.connect()

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

        user_id = rows[0]
        # role = db.execute("SELECT role FROM users WHERE id = ?", ([user_id])).fetchone()
        # if role[0] == "blocked":
        #     return render_template("error.html", error = "Your account has been blocked")
        
        session["user_id"] = rows[0]
        # Redirect user to home page
        return redirect("/selectmap")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/")
def index():
    admin = False
    adminVisibility = "class=hidden"
    # print(map_id)
    
    if (str(session) == "<FileSystemSession {}>"):
        print("something")
        return render_template("loginstart.html")
    else:
        user_id = session["user_id"]
        map_id = session['map_id']
        role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()

        if type(role) == type(None):
            db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "not_activated", map_id])
            con.commit()
            return render_template("error.html", error = "Your account is not activated. Please contact the admins to be activated")

        if role[0] == "not_activated":
            return render_template("error.html", error = "Your account is not activated. Please contact the admins to be activated")
        
        if role[0] == "admin":
            admin = True


    markers = []
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    unitAmount = []

    if admin == True:
        reportedMarkers = db.execute("SELECT name, lat, lng, id, comment FROM units WHERE map_id = ?", [map_id]).fetchall()
        
        adminVisibility = ""
        
        for marker in reportedMarkers:
            #print("id: " + str(marker[3]))
            marker_type = ""
            marker_amount = ""
            
            theTypes = db.execute("SELECT t.type FROM unit_relations ur JOIN types t ON ur.unit_id = ? AND t.type != -1 AND t.id = ur.type_id", [int(marker[3])]).fetchall()
            #print(theTypes)
            unitAmount = db.execute("SELECT a.id, a.value FROM unit_relations u JOIN amounts a ON u.amount_id = a.id AND u.unit_id = ? AND u.Amount_id != -1 LIMIT 1", [int(marker[3])]).fetchone()
            
            for theType in theTypes:
                marker_type += theType[0]
                marker_type += ", "

            if type(unitAmount) != type(None):
                marker_amount = str(unitAmount[1])
                

            if(len(marker_type) > 1):
                marker_type = marker_type[:-1]
                marker_type = marker_type[:-1]

            # Remove the last ", " elements

            

            comment = marker[4]
            if (type(comment) != type(None)): 
                comment = '<br />'.join(comment.splitlines())
            m = {'name': marker[0], 'location': [marker[1], marker[2]], 'comment': comment, 'id': marker[3], 'type': marker_type, 'amount': marker_amount}
            markers.append(m)

    return render_template("index.html", types=types, markers=markers, adminVisibility=adminVisibility, amounts = amounts, unitAmount = unitAmount)

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

        db.execute("INSERT INTO users(username, hash, country, role) values(?, ?, ?, ?)", [(str(request.form.get("username"))),
        (str(generate_password_hash(request.form.get("password")))), str(request.form.get("country")), ("not_activated")])
        con.commit()

        return redirect("/selectmap")

    else:
        return render_template("register.html")

@app.route("/report", methods=["GET", "POST"])
def report():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")

    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] == "not_activated":
        return render_template("error.html", error = "Only activated users can make reports. Please contact the admins to be activated.")
    
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
    print(reportedType)
    lat = str(request.form.get("lat"))
    lng = str(request.form.get("lng"))
    
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return render_template("error.html", error = "Invalid coordinates")
    
    amount = int(request.form.get("amount"))
    neededId = db.execute("SELECT max(id) FROM units").fetchone()[0] + 1
    print("Needed id is: " + str(neededId))
    db.execute("INSERT INTO units(id, user_id, name, lat, lng, country, comment, map_id) values(?, ?, ?, ?, ?, ?, ?, ?)", [neededId, user_id, (str(request.form.get("name"))),
        lat, lng, str(request.form.get("country")), str(request.form.get("comment")), (map_id)])
    
    for i in reportedType:
        db.execute("INSERT INTO unit_relations(unit_id, type_id, amount_id) values(?, ?, ?)", [neededId, int(i), amount])
    
    con.commit()

    return redirect("/")



############ type routines ####################
@app.route("/typechange")
def typechange():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    

    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("typechange.html", types = types)


@app.route("/amountchange")
def amountchange():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    

    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("amountchange.html", amounts = amounts)


@app.route("/changeTheType", methods = ["POST"])
def changeTheType():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    name = str(request.form.get("type_name"))
    print(name)
    id = str(request.form.get("type_id"))
    action = str(request.form.get("type_action"))

    if (action == "insert") :
        db.execute("INSERT INTO types(type, map_id) VALUES (?, ?)", [(name), (map_id)])

    elif (action == "update") :
        db.execute("UPDATE types SET type = ? WHERE id = ?", [name,id])

    elif (action == "delete") :
        name_type = (db.execute("SELECT type FROM types WHERE id = ?", [(id)]).fetchone())
        db.execute("DELETE FROM units WHERE type = ? AND map_id = ?", [(name_type[0]), (map_id)])
        db.execute("DELETE FROM types WHERE id = ? AND map_id = ?", [(id), (map_id)])
        print(name, map_id, sep=" ")

    con.commit()
    return redirect("/typechange")


@app.route("/cabinet")
def cabinet():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    isAdmin = "class=hidden"
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()

    if type(role) == type(None):
            db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "not_activated", map_id])
            role = ("not_activated")
            con.commit()

    elif role[0] == "admin":
        isAdmin = ""

    return render_template("cabinet.html", isAdmin = isAdmin)
    

@app.route("/passwordchange", methods = ["GET", "POST"])
def passwordChange():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")

    if request.method == "GET":
        return render_template("passwordchange.html")
    
    else:
        if not request.form.get("oldPass"):
            return render_template("error.html", error = "Must provide password")
        
        if not request.form.get("password"):
            return render_template("error.html", error = "Must provide new password")
        
        if not request.form.get("confirmPass"):
            return render_template("error.html", error = "Passwords don't match")
        
        oldPass = request.form.get("oldPass")
        newPass = request.form.get("password")
        print(newPass)
        confirmPass = request.form.get("confirmPass")

        if (newPass != confirmPass):
            return render_template("error.html", error = "Passwords don't match")
        
        if(newPass == oldPass):
            return render_template("error.html", error = "Your new password cannot be the same as your old password")

        user_id = session["user_id"]
        hash = db.execute("SELECT hash FROM users WHERE id = ?", [user_id]).fetchone()

        if not check_password_hash(hash[0], request.form.get("oldPass")):
            return render_template("error.html", error = "Invalid password")

        db.execute("UPDATE users SET hash = ? WHERE id = ?", [(str(generate_password_hash(request.form.get("password")))), (user_id)])
        con.commit()

        return render_template("cabinet.html")



@app.route("/createmap", methods=["GET", "POST"])
def createmap():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("createmap.html")

    else:
        map_name = request.form.get("map_name")
        if (db.execute("SELECT name FROM maps WHERE name = ?", [str(map_name)]).fetchone() != None):
            return render_template("error.html", error = "Map with this name already exists")
        
        db.execute("INSERT INTO maps(name) VALUES(?)", [str(map_name)])
        new_id = int(db.execute("SELECT id FROM maps WHERE name = ?", [str(map_name)]).fetchone()[0]) 
        session["map_id"] = new_id
        db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "admin", map_id])

        con.commit()
        return redirect("/addtypes")


@app.route("/selectmap", methods=["GET", "POST"])
def selectmap():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    

    # user_id = session["user_id"]
    # role = db.execute("SELECT role FROM user_roles WHERE map_id = ? ANd user_id = ?", ([map_id, user_id])).fetchone()
    
    
    if request.method == "GET":
        maps = db.execute("SELECT id, name FROM maps").fetchall()
        return render_template("selectmap.html", maps = maps)
    
    else: 
        map_id = int(request.form.get("map_id"))
        session["map_id"] = map_id
        return redirect("/cabinet")


@app.route("/addtypes", methods=["GET", "POST"])
def addtypes():
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    doneAction = "/addtypes"
    doneVisibility = "class=hidden"

    if request.method == "GET":
        return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility)
    
    else:
        name = request.form.get("name")
        if not name:
            return render_template("error.html", error = "Must provide type")
        print(map_id)
        db.execute("INSERT INTO types(type, map_id) VALUES(?, ?)", [str(name), map_id])
        con.commit()
        doneAction = "/"
        doneVisibility = ""
        return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility)


@app.route("/deletemap")
def deletemap():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Maps can only be deleted by admins")
    
    else:
        db.execute("DELETE FROM units WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM types WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM amounts WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM maps WHERE id = ?", [map_id])
        db.execute("DELETE FROM user_roles WHERE map_id = ?", [map_id])
        con.commit()
        session['map_id'] = None
        return redirect("/selectmap")
    

@app.route("/changeTheAmount", methods = ["POST"])
def changeTheAmount():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    name = str(request.form.get("amount_name"))
    print(name)
    id = str(request.form.get("amount_id"))
    action = str(request.form.get("type_action"))

    # print("action = " + action + ", name = " + name + ", id = " + id)

    if (action == "insert") :
        db.execute("INSERT INTO amounts(value, map_id) VALUES (?, ?)", [(name), (map_id)])

    elif (action == "update") :
        db.execute("UPDATE amounts SET value = ? WHERE id = ?", [name, id])

    elif (action == "delete") :
        name_type = (db.execute("SELECT type FROM types WHERE id = ?", [(id)]).fetchone())
        db.execute("DELETE FROM units WHERE type = ? AND map_id = ?", [(name_type[0]), (map_id)])
        db.execute("DELETE FROM types WHERE id = ? AND map_id = ?", [(id), (map_id)])
        print(name, map_id, sep=" ")

    else:
        return render_template("error.html", error = "Action is unknown")
    
    con.commit()
    return redirect("/amountchange")


@app.route("/approve", methods=["GET", "POST"])
def approve():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Users can only be approved by admins")
    
    if request.method == "GET":

        users = db.execute("SELECT u.id, u.username, u.country, u.registration_date FROM users u JOIN user_roles ur ON u.id = ur.user_id AND ur.role = ? AND ur.map_id = ?", ["not_activated", map_id]).fetchall()
        return render_template("approval.html", users = users)
    
    else:
        actions = ["activated", "blocked"]
        if not request.form.get("action") or request.form.get("action") not in actions:
            return render_template("error.html", error = "Invalid action")
        
        try:
            user_id = int(request.form.get("user_id"))
            db.execute("UPDATE user_roles SET role = ? WHERE user_id = ? AND map_id = ?", [str(request.form.get("action")), user_id, map_id])
            con.commit()
        except:
            return render_template("error.html", error = "Failed to process the user")
        return redirect("/approve")
    

@app.route("/deletemarker", methods = ["POST"])
def deletemarker():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    

    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Markers can only be deleted by admins")
    
    try:
        marker_id = request.form.get("marker_id")
        db.execute("DELETE FROM units WHERE id = ?", [marker_id])
        db.execute("DELETE FROM unit_relations WHERE unit_id = ?", [marker_id])
        con.commit()
        return redirect("/")
    except:
        return render_template("error.html", error = "Failed to process the marker")



@app.route("/block", methods = ["GET", "POST"])
def block():

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    map_id = session['map_id']
    
    if (type(map_id) == type(None)):
        return redirect("/selectmap")
    
    
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Users can only be blocked by admins")
    
    if request.method == "GET":
        users = db.execute("SELECT u.id, u.username, u.country, ur.role, u.registration_date FROM users u JOIN user_roles ur ON u.id = ur.user_id AND ur.map_id = ? AND (ur.role = ? OR ur.role = ?)", [map_id, "activated", "blocked"]).fetchall()
        return render_template("block.html", users = users)

    else:
        actions = ["activated", "blocked"]
        if not request.form.get("action") or request.form.get("action") not in actions:
            return render_template("error.html", error = "Invalid action")
        
        try:
            user_id = int(request.form.get("user_id"))
            db.execute("UPDATE user_roles SET role = ? WHERE user_id = ? AND map_id = ?", [str(request.form.get("action")), user_id, map_id])
            con.commit()
        except:
            return render_template("error.html", error = "Failed to process the user")
        return redirect("/block")