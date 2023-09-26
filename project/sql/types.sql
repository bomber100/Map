CREATE table "types"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"type" TEXT,
"image" TEXT,
"map_id" INTEGER,
FOREIGN KEY (map_id) REFERENCES maps(id)
)