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
    return deleteAccount()

@app.route("/block", methods = ["GET", "POST"])
def block_route():
    return blockUser()

@app.route("/")
def index_route():
    return index()
    
############ type routines ####################
@app.route("/typechange")
def typechange_route():
    return typeChangeForm()

@app.route("/amountchange")
def amountchange_route():
    return amountChangeForm()

@app.route("/changeTheType", methods = ["POST"])
def changeType_route():
    return changeType()

@app.route("/addtypes", methods=["GET", "POST"])
def addtypes_route():
    return addTypes()

@app.route("/addamounts", methods=["GET", "POST"])
def addamounts_route():
    return addAmounts()

@app.route("/changeTheAmount", methods = ["POST"])
def changeAmount_route():
    return changeAmount()

############ users routines ####################
@app.route("/cabinet")
def cabinet_route():
    return cabinet() 

@app.route("/passwordchange", methods = ["GET", "POST"])
def passwordChange_route():
    return passwordChange()

@app.route("/approve", methods=["GET", "POST"])
def approve_route():
    return approveUser()

############ map routines ####################
@app.route("/createmap", methods=["GET", "POST"])
def createmap_route():
    return createMap()

@app.route("/selectmap", methods=["GET", "POST"])
def selectmap_route():
    return selectMap()

@app.route("/deletemap")
def deletemap_route():
    return deleteMap()
    
@app.route("/deletemarker", methods = ["POST"])
def deletemarker_route():
    return deleteMarker()

@app.route("/report", methods=["GET", "POST"])
def report_route():
    return addMarker()