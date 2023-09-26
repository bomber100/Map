CREATE TABLE "amounts"(
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "value" TEXT,
    "map_id" INTEGER,
    FOREIGN KEY (map_id) REFERENCES maps(id) 
)