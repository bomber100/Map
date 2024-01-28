# CUSTOM MAP BUILDER
#### Video Demo:  https://youtu.be/E0oCOAB58ww
#### Description:
**Map Builder** is a web application which allows users to report information about locations all over the world, and to share it with others. The application makes use of Flask to deal with the backend, and the frontend is written in HTML and CSS. All the data is stored using an SQLite database. The markers are shown on the map using Google Maps API.

The main application is located in the **application.py** file. It contains all the endpoints supported by the application and controls all required data operations.

The program begins with the _index.html_ webpage. The corresponding endpoint of it is “/” . 
First of all, the program checks whether or not the user has logged in. 

### Users
These endpoints are responsible for manipulating user data:\
_/register\
/logout\
/deleteaccount\
/cabinet\
/passwordchange_

Corresponding frontend files are:\
_register.html\
login.html\
cabinet.html\
passwordchange.html_

### Admins
Admins can manipulate users. The users have to be approved on a particular map in order to access it. Admins have the rights to approve and block them.\
However, admins may be different for different maps. 
It is implemented in the following endpoints: 
_/block\ 
/approve_

Corresponding frontend files are:\
_block.html\
approval.html_

### Maps
Any user can create their own map (they automatically become an admin on that map), select a different map or report some information, which is represented by the 
_/createmap, /selectmap_, and _/report_ endpoints, respectively.\
However, only admins can delete markers with information from maps and delete the whole maps. These actions are represented by the _/deletemarker_ and _/deletemap_ endpoints.\
The first two endpoints can be accessed from _createmap.html_ and _selectmap.html_, and the last three are all accessed from the _index.html_ webpage.

### Map changing
The following endpoints represent map changing operations which are only available to admins. The first three add new types, alter existing ones or delete them, while the last three work identically for amounts.
_/typechange\
/changeTheType\
/addtypes\
/amountchange\
/changeTheAmount\
/addamounts_


### Database
Here is the database schema:\
![Scheme of the Database.](https://gcdnb.pbrd.co/images/BJv3jz1OrmVa.png?o=1 "Scheme of the Database")

All the maps are stored in the _map_ table, information about the users is in the _users_ and _userroles_ tables. Reported points are stored in the _units_ table, and the types and amounts they can have are in the _types_ and _amounts_ tables, respectively. 

During development, I decided that reported points should be able to have multiple types. To implement this, I created a table called _unitrelations_ which maps each point to its types and amount.

