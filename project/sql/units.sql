CREATE table "units"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"name" TEXT,
"country" TEXT,
"type" INTEGER,
"lat" TEXT,
"lng" TEXT,
"amount" INTEGER,
"map_id" INTEGER,
"comment" TEXT,
FOREIGN KEY (map_id) REFERENCES maps(id) 
)