from flask import redirect, render_template, request, session
from connection import getCursor

def createMap():
    """Add a new Map"""
        
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("createmap.html")

    user_id = session["user_id"]
    map_name = request.form.get("map_name")
    approvalNeededstr = request.form.getlist("approvalNeeded")
    approvalNeeded = False
    
    for i in approvalNeededstr:
        approvalNeeded = True

    db = getCursor()
    if (db.execute("SELECT name FROM maps WHERE name = ?", [str(map_name)]).fetchone() != None):
        return render_template("error.html", error = "Map with this name already exists")    
    
    db.execute("INSERT INTO maps(name, approval_needed, number_of_admins) VALUES(?, ?, ?)", [str(map_name), approvalNeeded, 1])
    new_id = int(db.execute("SELECT id FROM maps WHERE name = ?", [str(map_name)]).fetchone()[0]) 
    session["map_id"] = new_id
    db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "admin", new_id])

    db.connection.commit()
    return redirect("/addtypes")
    
def selectMap():
    """Select a new Map"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if request.method == "GET":
        db = getCursor()
        maps = db.execute("SELECT id, name FROM maps").fetchall()
        return render_template("selectmap.html", maps = maps)
    
    else: 
        map_id = int(request.form.get("map_id"))
        session["map_id"] = map_id
        return redirect("/")
    
def deleteMap():
    """Delete  Map"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']        
    user_id = session["user_id"]
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Maps can only be deleted by admins")
    
    else:
        db.execute("DELETE FROM locations WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM types WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM amounts WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM user_roles WHERE map_id = ?", [map_id])
        db.execute("DELETE FROM maps WHERE id = ?", [map_id])
        db.connection.commit()
        session['map_id'] = None
        return redirect("/selectmap")    