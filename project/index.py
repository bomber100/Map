import sqlite3
from flask import redirect, render_template, session
from connection import getCursor

def index():
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")    
    if 'map_id' not in session:
        return redirect("/selectmap")
    
    db = getCursor()
    isAdmin = False
    adminVisibility = "class=hidden"
    
    user_id = session["user_id"]
    map_id = session['map_id']
    
    role = getUserRole(user_id, map_id)
    if role == "not_activated":
        return render_template("error.html", error = "Your account is not activated. Please contact the admins to be activated")
    
    if role == "admin":
        isAdmin = True

    markers = []
    avgPositions = [51.505922705780414, -0.07502156799536142] # London Tower Bridge
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    map_name = db.execute("SELECT name FROM maps WHERE id = ?", [map_id]).fetchone()
    unitAmount = []

    if isAdmin == True:
        reportedMarkers = db.execute("SELECT name, lat, lng, id, comment FROM units WHERE map_id = ?", [map_id]).fetchall()
        if len(reportedMarkers) > 0:
            avgPositions = db.execute("SELECT avg(lat), avg(lng) FROM units WHERE map_id = ?", [map_id]).fetchone()
        
        adminVisibility = ""
        
        for marker in reportedMarkers:
            json = makeJson(marker, db)
            markers.append(json)

    return render_template("index.html", types = types, markers = markers, adminVisibility = adminVisibility, amounts = amounts, unitAmount = unitAmount, map_name = map_name, avgPositions = avgPositions)


def makeJson(marker, db):
    marker_type = ""
    marker_amount = ""
    
    types = db.execute("SELECT t.type FROM unit_relations ur JOIN types t ON ur.unit_id = ? AND t.type != -1 AND t.id = ur.type_id", [int(marker[3])]).fetchall()

    unitAmount = db.execute("SELECT a.id, a.value FROM units u JOIN amounts a ON u.amount = a.id AND u.id = ? AND u.amount != -1", [int(marker[3])]).fetchone()
    
    for t in types:
        marker_type += t[0]
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
    json = {'name': marker[0], 'location': [marker[1], marker[2]], 'comment': comment, 'id': marker[3], 'type': marker_type, 'amount': marker_amount}
    return json


def getUserRole(user_id, map_id):
    db = getCursor()

    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    approvalNeeded = db.execute("SELECT approval_needed FROM maps WHERE id = ?", [map_id]).fetchone()

    if type(role) == type(None):
        if (approvalNeeded[0]):
            db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "not_activated", map_id])
            role = ("not_activated")
        else:
            db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "activated", map_id])
            role = ("activated")
        db.connection.commit()  

    return role[0]