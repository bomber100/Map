import sqlite3

con = sqlite3.connect('map.db', check_same_thread=False)

def getCursor():
    try:
        cur = con.cursor()
        cur.execute('SELECT 1') # Attempt to execute a simple non-modifying query
        return cur
    except sqlite3.Error as e:        
        print(f"An error occurred: {e}")
        return None
