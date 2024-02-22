from flask import Flask
from flask_session import Session
from tempfile import mkdtemp

from auth import *
from users import *
from markers import *
from marker_types import *
from map import *
from index import index

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/login", methods=["GET", "POST"])
def login_route():    
    return login()

@app.route("/logout")
def logout_route():
    return logout()

@app.route("/register", methods=["GET", "POST"])
def register_route():
    return register()

@app.route("/deleteaccount", methods = ["POST"])
def deleteaccount_route():
    return deleteaccount()

@app.route("/block", methods = ["GET", "POST"])
def block_route():
    return block_user()

@app.route("/")
def index_route():
    return index()
    
############ type routines ####################
@app.route("/typechange")
def typechange_route():
    return typechange()

@app.route("/amountchange")
def amountchange_route():
    return amountchange()

@app.route("/changeTheType", methods = ["POST"])
def changeTheType_route():
    return changeTheType()

@app.route("/addtypes", methods=["GET", "POST"])
def addtypes_route():
    return addtypes()

@app.route("/addamounts", methods=["GET", "POST"])
def addamounts_route():
    return addamounts()

@app.route("/changeTheAmount", methods = ["POST"])
def changeTheAmount_route():
    return changeTheAmount()

############ users routines ####################
@app.route("/cabinet")
def cabinet_route():
    return cabinet() 

@app.route("/passwordchange", methods = ["GET", "POST"])
def passwordChange_route():
    return passwordChange()

@app.route("/approve", methods=["GET", "POST"])
def approve_route():
    return approve_user()

############ map routines ####################
@app.route("/createmap", methods=["GET", "POST"])
def createmap_route():
    return createmap()

@app.route("/selectmap", methods=["GET", "POST"])
def selectmap_route():
    return selectmap()

@app.route("/deletemap")
def deletemap_route():
    return deletemap()
    
@app.route("/deletemarker", methods = ["POST"])
def deletemarker_route():
    return deletemarker()

@app.route("/report", methods=["GET", "POST"])
def report_route():
    return add_marker()