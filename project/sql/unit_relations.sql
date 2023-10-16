CREATE TABLE "unit_relations"(
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"unit_id" INTEGER,
"amount_id" INTERGER,
"type_id" INTEGER,
FOREIGN KEY (unit_id) REFERENCES units(id),
FOREIGN KEY (amount_id) REFERENCES amounts(id),
FOREIGN KEY (type_id) REFERENCES types(id)
)