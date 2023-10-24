CREATE TABLE user_roles (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
role TEXT,
map_id INTEGER, 
blockReason TEXT,
FOREIGN KEY (map_id) REFERENCES maps(id),
FOREIGN KEY (user_id) REFERENCES users(id)
)