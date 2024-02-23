from flask import redirect, render_template, request, session
from connection import getCursor

def addMarker():
    """Add a new marker to the Map"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")

    if 'map_id' not in session:
        return redirect("/selectmap")
    
    map_id = session['map_id']
    user_id = session["user_id"]
    
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] == "not_activated":
        return render_template("error.html", error = "Only activated users can make reports. Please contact the admins to be activated.")
    
    if not request.form.get("lat"):
        return render_template("error.html", error = "Must provide latitude")
    
    elif not request.form.get("lat"):
        return render_template("error.html", error = "Must provide longitude")
    
    elif not request.form.get("type"):
        return render_template("error.html", error = "Must provide type")
    
    elif not request.form.get("amount"):
        return render_template("error.html", error = "Must provide amount")
    
    elif not request.form.get("name"):
        return render_template("error.html", error = "Must provide name")

    elif len(str(request.form.get("comment"))) > 200:
        return render_template("error.html", error = "The comment must be less than 200 characters long")


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
    neededId = db.execute("SELECT MAX(id) FROM locations").fetchone()[0] + 1
    
    db.execute("INSERT INTO locations(id, name, lat, lng, country, comment, map_id, amount_id) values(?, ?, ?, ?, ?, ?, ?, ?)", 
               [neededId, (str(request.form.get("name"))), lat, lng, 
                str(request.form.get("country")), str(request.form.get("comment")), (map_id), amount])
    
    for i in reportedType:
        db.execute("INSERT INTO type_relations(location_id, type_id) values(?, ?)", [neededId, int(i)])
    
    db.connection.commit()

    return redirect("/")


def deleteMarker():
    """Remove the marker"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")
    
    map_id = session['map_id']
    user_id = session["user_id"]
    
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Markers can only be deleted by admins")
    
    try:
        marker_id = request.form.get("marker_id")
        db.execute("DELETE FROM locations WHERE id = ?", [marker_id])
        db.execute("DELETE FROM type_relations WHERE location_id = ?", [marker_id])
        db.connection.commit()
        
        return redirect("/")
    except:
        return render_template("error.html", error = "Failed to process the marker")