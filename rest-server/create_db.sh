#!/bin/sh

# Skrypt tworzący bazę bazę danych potrzebną do testowania programu z pliku rest_webapp.py

# Zainicjuj bazę

rm -f osoby.sqlite

sqlite3 osoby.sqlite "
CREATE TABLE osoby (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imie VARCHAR NOT NULL,
    nazwisko TEXT NOT NULL,
    telefon TEXT NOT NULL,
    adres TEXT NOT NULL
);
CREATE TABLE rasy (
    nazwa VARCHAR PRIMARY KEY
);
CREATE TABLE psy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imie VARCHAR NOT NULL,
    rasa VARCHAR NOT NULL,
    wlasciciel_id INTEGER,
    FOREIGN KEY(wlasciciel_id) REFERENCES osoby(id),
    FOREIGN KEY(rasa) REFERENCES rasy(nazwa)
);

INSERT INTO osoby VALUES (1, 'Anna', 'Nowak', '+48124569988',
    'Rynek Główny 2, 30-001 Kraków');
INSERT INTO osoby VALUES (2, 'Jan', 'Kowalski', '+48127770022',
    'ul. Podzamcze 1, 31-001 Kraków');
INSERT INTO osoby VALUES (3, 'Maria', 'Konopa', '+48153980005',
    'ul. Fatimska 10, 34-100 Wadowice');
INSERT INTO osoby VALUES (4, 'Adam', 'Biedro', '+48225118649',
    'ul. Kalwaryjska 2, 34-100 Wadowice');
INSERT INTO osoby VALUES (5, 'Janusz', 'Woda', '+48325889654',
    'ul. Krakowksa 10, 34-100 Wadowice');

INSERT INTO rasy VALUES ('Kundel');
INSERT INTO rasy VALUES ('Jamnik');
INSERT INTO rasy VALUES ('Akita');
INSERT INTO rasy VALUES ('Beagle');
INSERT INTO rasy VALUES ('Owczarek Niemiecki');
INSERT INTO rasy VALUES ('West');
INSERT INTO rasy VALUES ('Bokser');
INSERT INTO rasy VALUES ('Buldog');
INSERT INTO rasy VALUES ('Bulterier');

INSERT INTO psy VALUES (1, 'Burek', 'Jamnik', 1);
INSERT INTO psy VALUES (2, 'Okruszek', 'Beagle', 1);
INSERT INTO psy VALUES (3, 'Luna', 'West', 2);
INSERT INTO psy VALUES (4, 'Leon', 'Buldog', 3);
INSERT INTO psy VALUES (5, 'Rambo', 'Owczarek Niemiecki', 4);
"

# Wypisanie zawartosci bazy danych

echo "Początkowa zawartość bazy:"
echo "Tabela osoby"
sqlite3 --header osoby.sqlite "SELECT * FROM osoby"
echo ""
echo "Tabela rasy"
sqlite3 --header osoby.sqlite "SELECT * FROM rasy"
echo ""
echo "Tabela psy"
sqlite3 --header osoby.sqlite "SELECT * FROM psy"
