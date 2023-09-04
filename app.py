# Uses a single route

from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template("greet.html", name=request.form.get("name", "world"))
    return render_template("index.html")

@app.route("/r")
def r():
    #return render_template("greet.html", name = "BUG")
    print("kuku")
    return redirect("/")
