from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from connection import getCursor

def login():
    """Log user in"""    

    session.clear()
    if request.method == "POST":
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
        session["user_id"] = user_id
        
        # Redirect user to home page
        return redirect("/selectmap")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
def register():
    """Register user"""
    
    if request.method == "POST":
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

        db = getCursor()
        rows = db.execute("SELECT 1 FROM users WHERE username = ?", ([request.form.get("username")])).fetchone()
        if rows != None:
            return render_template("error.html", error = "This username is already taken")
        
        db.execute("INSERT INTO users(username, hash, country) values(?, ?, ?)", [(str(request.form.get("username"))),
        (str(generate_password_hash(request.form.get("password")))), str(request.form.get("country"))])
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


