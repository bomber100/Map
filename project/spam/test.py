import os
import sqlite3

con = sqlite3.connect('map.db')
db = con.cursor()
for row in db.execute('SELECT * FROM users ORDER BY id'):
    print(row)