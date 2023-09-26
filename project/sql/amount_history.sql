CREATE table "amount_history"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"subunit_id" INTEGER,
"amount" INTEGER,
"time" timestamp,
"map_id" INTEGER,
FOREIGN KEY (map_id) REFERENCES maps(id)
)