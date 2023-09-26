CREATE table "subunits"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"unit_id" INTEGER,
"type" TEXT,
"amount" INTEGER,
"map_id" INTEGER,
FOREIGN KEY (map_id) REFERENCES maps(id)
)