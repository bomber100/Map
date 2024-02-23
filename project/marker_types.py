from flask import redirect, render_template, request, session
from connection import getCursor


def typeChangeForm():
    """Open the type change form"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    db = getCursor()
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("typechange.html", types = types)


def amountChangeForm():
    """Open the amount change form"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    db = getCursor()
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    return render_template("amountchange.html", amounts = amounts)

def changeType():
    """Update the Type"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    map_id = session['map_id']    
    name = str(request.form.get("type_name"))    
    id = str(request.form.get("type_id"))
    action = str(request.form.get("type_action"))

    db = getCursor()
    if (action == "insert") :
        db.execute("INSERT INTO types(type, map_id) VALUES (?, ?)", [(name), (map_id)])

    elif (action == "update") :
        db.execute("UPDATE types SET type = ? WHERE id = ?", [name,id])

    elif (action == "delete") :
        db.execute("DELETE FROM locations WHERE id IN(SELECT location_id FROM type_relations WHERE type_id = ?)", [(id)])
        db.execute("DELETE FROM types WHERE id = ?", [(id)])

    db.connection.commit()
    return redirect("/typechange")


def addTypes():
    """Add the marker's type"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    doneAction = "/addtypes"
    doneVisibility = "class=hidden"

    if request.method == "GET":
        return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility)
    
    name = request.form.get("name")
    if not name:
        return render_template("error.html", error = "Must provide type")
    
    db = getCursor()
    typeExists = db.execute("SELECT 1 FROM types WHERE map_id = ? AND type = ?", [map_id, name])
    if(type(typeExists) == type(None)):
        return render_template("error.html", error = "This type already exists")
    
    db.execute("INSERT INTO types(type, map_id) VALUES(?, ?)", [str(name), map_id])
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    db.connection.commit()
    doneAction = "/addamounts"
    doneVisibility = ""
    return render_template("addtypes.html", doneAction = doneAction, doneVisibility = doneVisibility, types = types)
    

def addAmounts():
    """Add the marker's amount"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    doneAction = "/addamounts"
    doneVisibility = "class=hidden"

    if request.method == "GET":
        return render_template("addamounts.html", doneAction = doneAction, doneVisibility = doneVisibility)
    
    name = request.form.get("name")
    if not name:
        return render_template("error.html", error = "Must provide amount")
    # print(map_id)
    
    db = getCursor()
    amountExists = db.execute("SELECT 1 FROM amounts WHERE map_id = ? AND value = ?", [map_id, name])
    if(type(amountExists) == type(None)):
        return render_template("error.html", error = "This amount already exists")
    
    db.execute("INSERT INTO amounts(value, map_id) VALUES(?, ?)", [str(name), map_id])
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    db.connection.commit()
    doneAction = "/"
    doneVisibility = ""
    return render_template("addamounts.html", doneAction = doneAction, doneVisibility = doneVisibility, amounts = amounts)

def changeAmount():
    """Update the marker's amount"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")
    
    if not request.form.get("type_action"):
        return render_template("error.html", error = "Action is unknown")

    map_id = session['map_id']
    name = str(request.form.get("amount_name"))
    id = str(request.form.get("amount_id"))
    action = str(request.form.get("type_action"))

    db = getCursor()
    if (action == "insert") :
        db.execute("INSERT INTO amounts(value, map_id) VALUES (?, ?)", [(name), (map_id)])

    elif (action == "update") :
        db.execute("UPDATE amounts SET value = ? WHERE id = ?", [name, id])

    elif (action == "delete") :
        db.execute("DELETE FROM locations WHERE amount_id = ?", [(id)])
        db.execute("DELETE FROM amounts WHERE id = ?", [(id)])

    else:
        return render_template("error.html", error = "Action is unknown")
    
    db.connection.commit()
    return redirect("/amountchange")