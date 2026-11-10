# Zadanie 2 – SQL Injection

## Zadanie

Vytvorte webovú aplikáciu, ktorá bude náchylná na útok typu SQL Injection.

## Použité technológie

- Python
- Flask
- PostgreSQL
- psycopg
- HTML
- CSS
- JavaScript
- pytest

## Spustenie aplikácie

1. V PostgreSQL vytvorte databázu s názvom sql_injection.

2. V pgAdmin otvorte Query Tool pre databázu sql_injection a spustite SQL skripty z priečinka sql v tomto poradí:

   1. sql/01_schema.sql
   2. sql/02_seed.sql
   3. sql/03_role.sql

   Pred spustením súboru sql/03_role.sql nastavte vlastné heslo pre databázového používateľa sql_lab_app.

3. Vytvorte a nastavte databázového používateľa sql_lab_app. Aplikácia sa nemá pripájať ako používateľ postgres.

4. V koreňovom priečinku projektu vytvorte súbor .env:

   FLASK_SECRET_KEY=vlastny-lokalny-kluc
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=sql_injection
   DB_USER=sql_lab_app
   DB_PASSWORD=vlastne-heslo-databazoveho-pouzivatela

   (nedávať na Git!)

5. V PowerShelli v priečinku projektu vytvorte virtuálne prostredie a nainštalujte knižnice:

   py -3.14 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt

6. Spustite aplikáciu príkazom:

   .\.venv\Scripts\python.exe run.py

7. V prehliadači otvorte adresu http://127.0.0.1:5000.

## Opis aplikácie

Aplikácia obsahuje päť ukážok SQL Injection:

1. Tautology-based SQL Injection – obídenie prihlásenia.
2. UNION-based SQL Injection – získanie údajov z inej tabuľky.
3. Error-based SQL Injection – zobrazenie databázových chýb.
4. Boolean-based Blind SQL Injection – zisťovanie informácií pomocou pravdivých a nepravdivých podmienok.
5. Data Manipulation SQL Injection – zmena ceny produktu cez formulár recenzie.

Každý modul má režimy Vulnerable a Secure. Obsahuje aj možnosť Show Explanation, kde je ukázaný útok, príčina zraniteľnosti a jej oprava.
