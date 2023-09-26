CREATE table "location_history"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"unit_id" INTEGER,
"time" timestamp,
"location" TEXT,
"map_id" INTEGER,
FOREIGN KEY (map_id) REFERENCES maps(id)
)