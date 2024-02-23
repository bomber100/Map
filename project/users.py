from flask import redirect, render_template, request, session, Markup
from werkzeug.security import check_password_hash, generate_password_hash
from connection import getCursor

def passwordChange():
    """Change the user's password"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")

    if request.method == "GET":
        return render_template("passwordchange.html")
    
    if not request.form.get("oldPass"):
        return render_template("error.html", error = "Must provide password")
    
    if not request.form.get("password"):
        return render_template("error.html", error = "Must provide new password")
    
    if not request.form.get("confirmPass"):
        return render_template("error.html", error = "Passwords don't match")
    
    oldPass = request.form.get("oldPass")
    newPass = request.form.get("password")
    confirmPass = request.form.get("confirmPass")

    if (newPass != confirmPass):
        return render_template("error.html", error = "Passwords don't match")
    
    if(newPass == oldPass):
        return render_template("error.html", error = "Your new password cannot be the same as your old password")

    user_id = session["user_id"]
    
    db = getCursor()
    hash = db.execute("SELECT hash FROM users WHERE id = ?", [user_id]).fetchone()
    user_Name = db.execute("SELECT username FROM users WHERE id = ?", [user_id]).fetchone()
    isAdmin = "class=hidden"

    if not check_password_hash(hash[0], request.form.get("oldPass")):
        return render_template("error.html", error = "Invalid password")

    db.execute("UPDATE users SET hash = ? WHERE id = ?", [(str(generate_password_hash(request.form.get("password")))), (user_id)])
    db.connection.commit()

    return render_template("cabinet.html", isAdmin = isAdmin, user_Name = user_Name)  

def approveUser():
    """Approve the user"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    user_id = session["user_id"]
    
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Users can only be approved by admins")
    
    if request.method == "GET":
        users = db.execute("SELECT u.id, u.username, u.country, u.registration_date FROM users u JOIN user_roles ur ON ur.user_id = u.id WHERE ur.role = ? AND ur.map_id = ?", ["not_activated", map_id]).fetchall()
        return render_template("approval.html", users = users)
    
    else:
        actions = ["activated", "blocked"]
        if not request.form.get("action") or request.form.get("action") not in actions:
            return render_template("error.html", error = "Invalid action")
        
        try:
            user_id = int(request.form.get("user_id"))
            db.execute("UPDATE user_roles SET role = ? WHERE user_id = ? AND map_id = ?", [str(request.form.get("action")), user_id, map_id])
            db.connection.commit()
        except:
            return render_template("error.html", error = "Failed to process the user")
        return redirect("/approve")
    

def cabinet():
    """Open user's personaldetails """

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    user_id = session["user_id"]
    isAdmin = "class=hidden"

    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    approvalNeeded = db.execute("SELECT approval_needed FROM maps WHERE id = ?", [map_id]).fetchone()
    user_Name = db.execute("SELECT username FROM users WHERE id = ?", [user_id]).fetchone()

    if type(role) == type(None):
            if(approvalNeeded[0]):
                roleName = "not_activated"
            else:
                roleName = "activated"
            
            db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, roleName, map_id])
            db.connection.commit()

    elif role[0] == "admin":
        isAdmin = ""

    return render_template("cabinet.html", isAdmin = isAdmin, user_Name = user_Name)  


def blockUser():
    """Block the user"""

    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    user_id = session["user_id"]
    
    db = getCursor()
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Users can only be blocked by admins")
    
    if request.method == "GET":
        users = db.execute("SELECT u.id, u.username, u.country, ur.role, u.registration_date, ur.reason FROM users u JOIN user_roles ur ON ur.user_id = u.id WHERE ur.map_id = ? AND (ur.role = ? OR ur.role = ?)", [map_id, "activated", "blocked"]).fetchall()
        return render_template("block.html", users = users)

    else:
        actions = ["activated", "blocked"]
        if not request.form.get("action") or request.form.get("action") not in actions:
            return render_template("error.html", error = "Invalid action")
        
        try:
            user_id = int(request.form.get("user_id"))
            reason = str(request.form.get("reason"))
            db.execute("UPDATE user_roles SET role = ?, reason = ? WHERE user_id = ? AND map_id = ?", [str(request.form.get("action")), reason, user_id, map_id])
            db.connection.commit()
        except:
            return render_template("error.html", error = "Failed to process the user")
        return redirect("/block")
    
def deleteAccount():
    """Delete User's account"""
    
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    user_id = session["user_id"]
    db = getCursor()
    admined_maps = db.execute("SELECT m.name " + 
                              "  FROM user_roles u "
                              "  INNER JOIN maps      m ON m.id = u.map_id " + 
                              "  LEFT JOIN user_roles r ON r.map_id = m.id AND r.role = 'admin' AND r.user_id <> u.user_id   " + 
                              "  WHERE u.role = 'admin'  " + 
                              "      AND u.user_id = ?  " + 
                              "      AND r.id IS NULL ", [user_id]).fetchall()
    
    if type(admined_maps) != type(None):
        error_str = ""
        for map in admined_maps:
            error_str += Markup("<br><i>")
            error_str += map[0]
            error_str += Markup("</i>")
        
        if (error_str != ""):
            error_str = Markup("You are the only admin of the following maps:") + error_str
            error_str += Markup("<br>Please promote another user before deleting your account")
            return render_template("error.html", error = error_str)

    db.execute("DELETE FROM user_roles WHERE user_id = ?", [user_id])
    db.execute("DELETE FROM users WHERE id = ?", [user_id])
    db.connection.commit()
    session.clear()
    return redirect("/login")