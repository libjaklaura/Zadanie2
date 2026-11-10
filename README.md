# Zadanie 2 – SQL Injection

## Zadanie

Vytvorte webovú aplikáciu, ktorá bude náchylná na útok typu SQL Injection.

## Použité technológie

- Python 3.14
- Flask
- PostgreSQL
- psycopg
- HTML, CSS, JavaScript
- pytest

## Spustenie aplikácie

### 1. Databáza

V PostgreSQL vytvorte databázu s názvom `sql_injection`.

V pgAdmin otvorte Query Tool pre databázu `sql_injection` a spustite SQL skripty v tomto poradí:

- `sql/01_schema.sql`
- `sql/02_seed.sql`
- `sql/03_role.sql`

Pred spustením súboru `sql/03_role.sql` nastavte vlastné heslo pre databázového používateľa `sql_lab_app`. Tento skript vytvorí používateľa a nastaví jeho oprávnenia.

Aplikácia sa pripája cez používateľa `sql_lab_app`, nie cez administrátorský účet `postgres`.

### 2. Nastavenie súboru .env

V koreňovom priečinku projektu vytvorte súbor `.env` podľa `.env.example`:

```dotenv
FLASK_SECRET_KEY=vlastny-lokalny-kluc
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=sql_injection
DB_USER=sql_lab_app
DB_PASSWORD=vlastne-heslo
```

Súbor `.env` obsahuje prihlasovacie údaje, preto sa nesmie nahrávať na GitHub.

### 3. Inštalácia knižníc

V PowerShelli v priečinku projektu vytvorte virtuálne prostredie:

```powershell
py -3.14 -m venv .venv
```

Nainštalujte potrebné knižnice:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Spustenie aplikácie

V PowerShelli spustite:

```powershell
.\.venv\Scripts\python.exe run.py
```

V prehliadači otvorte adresu:

http://127.0.0.1:5000

## Opis aplikácie

Aplikácia obsahuje päť ukážok SQL Injection:

1. **Tautology-based SQL Injection** – obídenie prihlásenia.
2. **UNION-based SQL Injection** – získanie údajov z inej tabuľky.
3. **Error-based SQL Injection** – zobrazenie databázových chýb.
4. **Boolean-based Blind SQL Injection** – zisťovanie informácií pomocou pravdivých a nepravdivých podmienok.
5. **Data Manipulation SQL Injection** – zmena ceny produktu cez formulár recenzie.

Každý modul má režimy **Vulnerable** a **Secure**, medzi ktorými sa dá prepínať.

V časti **Show Explanation** je uvedený príklad útoku, príčina zraniteľnosti a spôsob jej opravy.