import sqlite3
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from connection import getCursor

def passwordChange():
    """Change the user's password"""

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")

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
        db.connection.commit()

        return render_template("cabinet.html")

def approve_user():
    """Approve the user"""

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
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
            db.connection.commit()
        except:
            return render_template("error.html", error = "Failed to process the user")
        return redirect("/approve")
    

def cabinet():
    """Open user's personaldetails """

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    
    isAdmin = "class=hidden"
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    approvalNeeded = db.execute("SELECT approval_needed FROM maps WHERE id = ?", [map_id]).fetchone()
    user_Name = db.execute("SELECT username FROM users WHERE id = ?", [user_id]).fetchone()

    if type(role) == type(None):
            if(approvalNeeded[0]):
                db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "not_activated", map_id])
                print("cabinet")
                role = ("not_activated")
            else:
                db.execute("INSERT INTO user_roles(user_id, role, map_id) VALUES (?, ?, ?)", [user_id, "activated", map_id])
                role = ("activated")
            db.connection.commit()

    elif role[0] == "admin":
        isAdmin = ""

    return render_template("cabinet.html", isAdmin = isAdmin, user_Name = user_Name)  


def block_user():
    """Block the user"""

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    if 'map_id' not in session:
        return redirect("/selectmap")

    map_id = session['map_id']
    user_id = session["user_id"]
    role = db.execute("SELECT role FROM user_roles WHERE user_id = ? AND map_id = ?", ([user_id, map_id])).fetchone()
    if role[0] != "admin":
        return render_template("error.html", error="Users can only be blocked by admins")
    
    if request.method == "GET":
        users = db.execute("SELECT u.id, u.username, u.country, ur.role, u.registration_date, ur.reason FROM users u JOIN user_roles ur ON u.id = ur.user_id AND ur.map_id = ? AND (ur.role = ? OR ur.role = ?)", [map_id, "activated", "blocked"]).fetchall()
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