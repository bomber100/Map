import sqlite3
from flask import redirect, render_template, request, session
from connection import getCursor


def typechange():

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("typechange.html", types = types)


def amountchange():

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("amountchange.html", amounts = amounts)

def changeTheType():

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    name = str(request.form.get("type_name"))
    
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

    db.connection.commit()
    return redirect("/typechange")


def addtypes():
    """Add the marker's type"""
    
    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    doneAction = "/addtypes"
    doneVisibility = "class=hidden"

    if request.method == "GET":
        return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility)
    
    else:
        name = request.form.get("name")
        if not name:
            return render_template("error.html", error = "Must provide type")
        # print(map_id)
        same = db.execute("SELECT * FROM types  WHERE map_id = ? AND type = ?", [map_id, name])
        if(type(same) == type(None)):
            return render_template("error.html", error = "This type already exists")
        db.execute("INSERT INTO types(type, map_id) VALUES(?, ?)", [str(name), map_id])
        types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
        db.connection.commit()
        doneAction = "/addamounts"
        doneVisibility = ""
        return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility, types = types)
    

def addamounts():
    """Add the marker's amount"""
    
    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    doneAction = "/addamounts"
    doneVisibility = "class=hidden"

    if request.method == "GET":
        return render_template("addamounts.html", doneAction = doneAction, doneVisibility = doneVisibility)
    
    else:
        name = request.form.get("name")
        if not name:
            return render_template("error.html", error = "Must provide amount")
        # print(map_id)
        same = db.execute("SELECT * FROM amounts WHERE map_id = ? AND value = ?", [map_id, name])
        if(type(same) == type(None)):
            return render_template("error.html", error = "This amount already exists")
        db.execute("INSERT INTO amounts(value, map_id) VALUES(?, ?)", [str(name), map_id])
        amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
        db.connection.commit()
        doneAction = "/"
        doneVisibility = ""
        return render_template("addamounts.html", doneAction = doneAction, doneVisibility = doneVisibility, amounts = amounts)

def changeTheAmount():
    """Update the marker's amount"""
    
    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
        
    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    name = str(request.form.get("amount_name"))
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
    
    db.connection.commit()
    return redirect("/amountchange")