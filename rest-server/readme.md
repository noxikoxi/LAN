## Server Rest

### Potrzebna jest istniejąca baza danych aby mógł funkcjonować
- można stworzyc baze z pomocą skrypty create_db.sh
- serwer zwraca i przyjmuje dane w formacie TSV

Serwer działa z 3 tabelkami:
- osoby
- psy
- rasy

Osoby przechowuje informacje o osobach (imie, nazwisko, tel, adres)<br>
Psy przechowuje informacje o psach (imie, rasa, id_wlasciciela)<br>
Rasy przechowuje możliwe rasy do wybrania dla psów (nazwa)<br>

### Możliwe endpointy i metody:
&emsp; **GET**
- */osoby* &emsp; | zwraca tabele osoby
- */osoby/[id]* &emsp; | zwraca rekord o danym id z tabeli osoby
- */osoby/search/?[filtry oddzielone &]* &emsp; | zwraca rekordy z tabeli osoby z zastosowanymi filtrami
- */psy* &emsp; | zwraca tabele psy
- */psy/[id]* &emsp; | zwraca rekord o danim id z tabeli psy
- */psy/search/?[filtry oddzielone &]** &emsp; | zwraca rekordy z tabeli psy z zastosowanymi filtrami
- */psy/rasy* &emsp; | zwraca tabele rasy
- */psy/rasy/[nazwa]* &emsp; | zwraca nazwe jeżeli istniej w bazie inaczej 404
<br>&emsp; **POST**
- Zapytania POST wymagają podania wszystkich kolumn dla rekordów (Z wyjątkiem /psy tam można pominąc wlasciciel_id)
- */osoby* &emsp; | dodaje rekord do tabeli osoby
- */psy* &emsp; | dodaje rekord do tabeli psy
- */psy/rasy* &emsp; | dodaje rekord do tabeli rasy
<br>&emsp; **PUT**
- Zapytania PUT nie wymagają podania wszystkich kolumn dla rekordów
- */osoby/[id]* &emsp; | Zmienia rekord o podanym id z tabeli osoby
- */psy/[id]* &emsp; | Zmienia rekord o podanym id z tabeli psy
<br>&emsp; **DELETE**
- Niemożliwym jest usunięcie osoby, która posiada psa oraz rasy jeżeli jakiś pies jest tej rasy
- */osoby/[id]* &emsp; | Usuwa rekord o danym id z tabeli osoby
- */psy/[id]* &emsp; | Usuwa rekord o danym id z tabeli psy
- */psy/rasy/[nazwa]* &emsp; | Usuwa rekord o podanej nazwie z tabeli rasy

Przykłady:<br>
- POST /osoby<br>
imie&emsp;nazwisko&emsp;tel&emsp;adres<br>
Adam&emsp;Kowalski&emsp;+48123456789&emsp;ul. Kalwaryjska 5 34-100 Wadowice
<br>
- POST /psy<br>
imie&emsp;rasa&emsp;wlasciciel_id<br>
Burek&emsp;Kundel&emsp;1
- POST /rasy<br>
nazwa<br>
Beagle

Dla Put analogicznie, ale nie trzeba podawać wszystkich kolumn.<br>
GET/DELETE nie przyjmuja żadnych danych.

