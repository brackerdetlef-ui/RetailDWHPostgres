# RetailDWHPostgres

## Projektbeschreibung

RetailDWHPostgres ist ein Lern- und Referenzprojekt zum Aufbau eines modernen Data Warehouse auf Basis von PostgreSQL.

Das Projekt verfolgt das Ziel, eine Architektur zu entwickeln, die später mit möglichst wenigen Änderungen auch auf Cloud-Plattformen wie Snowflake oder Google BigQuery betrieben werden kann.

Dabei werden ausschließlich etablierte Open-Source-Werkzeuge verwendet.

Geplante Komponenten:

* PostgreSQL
* Python
* dbt
* Dagster
* Git / GitHub

---

# Projektarchitektur

Die Datenverarbeitung erfolgt nach dem ELT-Prinzip.

```text
CSV / Quelldaten
        │
        ▼
      Loader
        │
        ▼
 PostgreSQL (raw)
        │
        ▼
      dbt stage
        │
        ▼
  dbt intermediate
        │
        ▼
     dbt mart
```

Die Orchestrierung der einzelnen Verarbeitungsschritte erfolgt später über Dagster.

---

# Projektstruktur

```text
RetailDWHPostgres/

│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── README.de.md
│
├── archive/
├── config/
├── dbt/
├── docs/
├── loader/
├── logs/
├── orchestration/
├── scripts/
├── sql/
├── src/
└── tests/
```

---

# Python-Umgebung

Projektverzeichnis anlegen

```bash
mkdir RetailDWHPostgres
cd RetailDWHPostgres
```

Git initialisieren

```bash
git init
```

Virtuelle Python-Umgebung erstellen

```bash
python3 -m venv .venv
```

Virtuelle Umgebung aktivieren

```bash
source .venv/bin/activate
```

pip install -e .





Python-Version prüfen

```bash
python --version
```

pip aktualisieren

```bash
python -m pip install --upgrade pip
```

## Python-Abhängigkeiten

Installation der Projektabhängigkeiten:

```bash
pip install -r requirements.txt
```

Anschließend können die tatsächlich installierten Versionen dokumentiert werden:

```bash
pip freeze > requirements.lock
```

---

# PostgreSQL

## Projektbenutzer anlegen

Als PostgreSQL-Administrator anmelden

```bash
sudo -u postgres psql
```

Projektbenutzer erzeugen

```sql
CREATE ROLE retaildwh
WITH
    LOGIN
    PASSWORD '<lokales Passwort>';
```

## Datenbank anlegen

```sql
CREATE DATABASE "retailDWH"
OWNER retaildwh
ENCODING 'UTF8'
TEMPLATE template0;
```

Mit der Datenbank verbinden

```sql
\c retailDWH
```

---

# Datenbankschemas

Folgende Schemas werden angelegt.

```sql
CREATE SCHEMA raw          AUTHORIZATION retaildwh;
CREATE SCHEMA stage        AUTHORIZATION retaildwh;
CREATE SCHEMA intermediate AUTHORIZATION retaildwh;
CREATE SCHEMA mart         AUTHORIZATION retaildwh;
CREATE SCHEMA control      AUTHORIZATION retaildwh;
```

## Bedeutung der Schemas

| Schema       | Aufgabe                                                     |
| ------------ | ----------------------------------------------------------- |
| raw          | Unveränderte Quelldaten (Landing Zone)                      |
| stage        | Technische Bereinigung und Standardisierung                 |
| intermediate | Wiederverwendbare fachliche Zwischenergebnisse              |
| mart         | Fachliches Data-Warehouse-Modell für Reporting und Analysen |
| control      | Ladehistorie, Scheduler, Monitoring und Metadaten           |

---

# Konfiguration

## config/config.yaml

Enthält die allgemeine Projektkonfiguration.

Beispiele:

* Projektinformationen
* Verzeichnisse
* Datenbankschemas
* Loader-Konfiguration
* Logging

Passwörter und Zugangsdaten werden **nicht** in dieser Datei gespeichert.

## .env

Die Datei `.env` enthält ausschließlich lokale Zugangsdaten und wird nicht versioniert.

Sie ist in `.gitignore` eingetragen.

Die Datei `.env.example` dient als Vorlage.

---

# Projektstand

Aktuell umgesetzt

* Git-Projekt erstellt
* Virtuelle Python-Umgebung eingerichtet
* PostgreSQL-Datenbank erstellt
* Projektbenutzer erstellt
* Data-Warehouse-Schemas definiert
* Grundstruktur des Projektes geplant
* Konfigurationsdateien vorbereitet

---

# Nächste Schritte

* Python-Projektstruktur aufbauen
* Konfigurationsverwaltung entwickeln
* Verbindung zu PostgreSQL herstellen
* CSV-Loader entwickeln
* Ladehistorie implementieren
* Dagster integrieren
* dbt-Projekt integrieren
* GitHub-Repository erstellen

