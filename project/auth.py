import sqlite3
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from connection import getCursor

def login():
    """Log user in"""    

    # db = getCursor
    session.clear()
    if request.method == "POST":
        print("this is POST")
        if not request.form.get("username"):
            return render_template("error.html", error = "Must provide username")

        elif not request.form.get("password"):
            return render_template("error.html", error = "Must provide password")

        username = str(request.form.get("username"))
        db = getCursor()
        rows = db.execute("SELECT id, hash FROM users WHERE username = ?", ([username])).fetchone()
        
        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[1], request.form.get("password")):
            return render_template("error.html", error = "Invalid username and/or password")

        # Remember which user has logged in
        user_id = rows[0]
        
        session["user_id"] = rows[0]
        # Redirect user to home page
        return redirect("/selectmap")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
def register():
    """Register user"""

    db = getCursor()
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", ([request.form.get("username")])).fetchone()
        if not request.form.get("username"):
            return render_template("error.html", error = "Must provide username")

        elif not request.form.get("password"):
            return render_template("error.html", error = "Must provide password")
        
        elif len(request.form.get("password")) < 8:
            return render_template("error.html", error = "Password must be at least 8 characters long")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", error = "Passwords don`t match")

        elif not request.form.get("country"):
            return render_template("error.html", error = "Must provide country")

        elif rows != None:
            return render_template("error.html", error = "This username is already taken")
        print(str(request.form.get("username")))

        db.execute("INSERT INTO users(username, hash, country, role) values(?, ?, ?, ?)", [(str(request.form.get("username"))),
        (str(generate_password_hash(request.form.get("password")))), str(request.form.get("country")), ("not_activated")])
        db.connection.commit()

        return redirect("/selectmap")

    else:
        return render_template("register.html")    
    
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")    

def deleteaccount():
    """Delete User's account"""

    db = getCursor()
    if (str(session) == "<FileSystemSession {}>"):
        return redirect("/login")
    
    user_id = session["user_id"]
    admined_maps = db.execute("SELECT m.name FROM user_roles u JOIN maps m ON u.role = ? AND u.user_id = ? AND u.map_id = m.id AND m.number_of_admins = ?", ["admin", user_id, 1]).fetchall()
    
    if type(admined_maps) != type(None):
        error_str = "You are the only admin of the following maps: "
        for i in admined_maps:
            error_str += i[0]
            error_str += ", "
        error_str = error_str[:-2]
        error_str += ". "
        error_str += "Please promote another user before deleting your account"
        return render_template("error.html", error = error_str)

    db.execute("DELETE FROM user_roles WHERE user_id = ?", [user_id])
    db.execute("DELETE FROM users WHERE user_id = ?", [user_id])
    db.connection.commit()
    session.clear()
    return redirect("/login")


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