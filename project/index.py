import sqlite3
from flask import redirect, render_template, session
from connection import getCursor

def index():
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")    
    if 'map_id' not in session:
        return redirect("/selectmap")
        
    isAdmin = False
    adminVisibility = "class=hidden"
    
    user_id = session["user_id"]
    map_id = session['map_id']
    
    role = getUserRole(user_id, map_id)
    if role == "not_activated":
        return render_template("error.html", error = "Your account is currently inactive. An activation request has been forwarded to the administrators.")
    
    if role == "admin":
        isAdmin = True

    markers = []
    avgPositions = [51.505922705780414, -0.07502156799536142] # London Tower Bridge as a default
    
    db = getCursor()
    types = db.execute("SELECT id, type FROM types WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    amounts = db.execute("SELECT id, value FROM amounts WHERE map_id = ? ORDER BY id", [map_id]).fetchall()
    map_name = db.execute("SELECT name FROM maps WHERE id = ?", [map_id]).fetchone()
    unitAmount = []

    
    reportedMarkers = db.execute("SELECT name, lat, lng, id, comment FROM locations WHERE map_id = ?", [map_id]).fetchall()
    if len(reportedMarkers) > 0:
        avgPositions = db.execute("SELECT avg(lat), avg(lng) FROM locations WHERE map_id = ?", [map_id]).fetchone()
        
    for marker in reportedMarkers:
        json = makeJson(marker)
        markers.append(json)

    if isAdmin == True:
        adminVisibility = ""

    return render_template("index.html", types = types, markers = markers, adminVisibility = adminVisibility, amounts = amounts, unitAmount = unitAmount, map_name = map_name, avgPositions = avgPositions)


def makeJson(marker):
    marker_type = ""
    marker_amount = ""
    
    db = getCursor()
    types = db.execute("SELECT t.type FROM type_relations r JOIN types t ON t.id = r.type_id WHERE r.location_id = ? AND t.type != -1", [int(marker[3])]).fetchall()

    unitAmount = db.execute("SELECT a.id, a.value FROM locations l JOIN amounts a ON a.id = l.amount_id WHERE l.id = ? AND l.amount_id != -1", [int(marker[3])]).fetchone()
    
    for t in types:
        marker_type += t[0]
        marker_type += ", "

    if type(unitAmount) != type(None):
        marker_amount = str(unitAmount[1])

    if(len(marker_type) > 1):
        marker_type = marker_type[:-2]

    # Remove the last ", " elements
    comment = marker[4]
    if (type(comment) != type(None)): 
        comment = '<br />'.join(comment.splitlines())
    json = {'name': marker[0], 'location': [marker[1], marker[2]], 'comment': comment, 'id': marker[3], 'type': marker_type, 'amount': marker_amount}
    return json


def getUserRole(user_id, map_id):
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    
    if type(role) == type(None):
        approvalNeeded = db.execute("SELECT approval_needed FROM maps WHERE id = ?", [map_id]).fetchone()
        if (approvalNeeded[0]):
            roleName = "not_activated"
        else:
            roleName = "activated"
        
        db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, roleName, map_id])
        db.connection.commit()  
    else: 
        roleName = role[0]

    return roleName