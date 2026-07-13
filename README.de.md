# RetailDWHPostgres

## Projektbeschreibung

RetailDWHPostgres ist ein Lern- und Referenzprojekt zum Aufbau eines modernen Data Warehouse auf Basis von PostgreSQL. 
Das Projekt verfolgt das Ziel, eine Architektur zu entwickeln, die spaeter mit moeglichst wenigen Aenderungen auch auf Cloud-Plattformen wie Snowflake oder Google BigQuery betrieben werden kann.

Dabei werden ausschliesslich etablierte Open-Source-Werkzeuge verwendet.

**Geplante und eingesetzte Komponenten:**
* PostgreSQL (v15+)
* Python (v3.10+)
* dbt (Data Build Tool)
* Dagster (Orchestrierung)
* Git / GitHub

---

## Datengrundlage & Kooperation

Dieses Data Warehouse arbeitet nicht mit isolierten Beispieldaten, sondern ist direkt mit dem Schwesterprojekt **RetailDWGen** verzahnt. 

* **Daten-Generator:** [RetailDWGen auf GitHub](https://github.com/brackerdetlef-ui/RetailDWGen/)

Die dort erzeugten, realistischen Handelsdaten (Stammdaten wie Artikel, Kunden, Lieferanten sowie Transaktionsdaten) dienen als direkte Quellgrundlage für dieses DWH. Der integrierte Python-Loader greift standardmaessig auf das Ausgabe-Verzeichnis von `RetailDWGen` zu, um die CSV-Dateien hochperformant einzulesen.

---

## Projektarchitektur

Die Datenverarbeitung erfolgt konsequent nach dem **ELT-Prinzip** (Extract, Load, Transform).

```
  RetailDWGen (Output)
        │
        ▼ (CSV-Dateien)
      Loader (Python / psycopg3)
        │
        ▼
 PostgreSQL (Schema: raw)
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

Die Orchestrierung der einzelnen Verarbeitungsschritte sowie die Ueberwachung der Pipelines erfolgt spaeter zentral ueber **Dagster**.

---

## Voraussetzungen

* **Python:** Version 3.10 oder hoeher
* **PostgreSQL:** Version 15 oder hoeher (inkl. installierter Client-Bibliotheken fuer `psycopg3`)
* **Datenbasis:** Ein lokales Verzeichnis mit generierten CSV-Daten aus dem Projekt `RetailDWGen`.

---

## Installation & Einrichtung

### 1. Repository klonen & Verzeichnis betreten
```bash
git clone <repository-url>
cd RetailDWHPostgres
```

### 2. Virtuelle Python-Umgebung erstellen & aktivieren
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Abhaengigkeiten installieren
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```
*Hinweis: Zur Dokumentation der exakt installierten Versionen kann anschliessend `pip freeze > requirements.lock` ausgefuehrt werden.*

---

## PostgreSQL-Konfiguration

### 1. Projektbenutzer und Datenbank anlegen
Melden Sie sich als PostgreSQL-Administrator an (`sudo -u postgres psql`) und fuehren Sie folgende SQL-Befehle aus:

```sql
-- Projektbenutzer erzeugen
CREATE ROLE retaildwh WITH LOGIN PASSWORD '<lokales Passwort>';

-- Datenbank anlegen
CREATE DATABASE "retailDWH" OWNER retaildwh ENCODING 'UTF8';
```

### 2. Datenbankschemas initialisieren
Verbinden Sie sich mit der neuen Datenbank (`\c retailDWH`) und legen Sie die DWH-Schichten an:

```sql
CREATE SCHEMA raw          AUTHORIZATION retaildwh;
CREATE SCHEMA stage        AUTHORIZATION retaildwh;
CREATE SCHEMA intermediate AUTHORIZATION retaildwh;
CREATE SCHEMA mart         AUTHORIZATION retaildwh;
CREATE SCHEMA control      AUTHORIZATION retaildwh;
```

### Bedeutung der Schemas

| Schema | Aufgabe | Beschreibung |
| :--- | :--- | :--- |
| **raw** | Landing Zone | Unveraenderte Quelldaten. Es erfolgen keinerlei Transformationen. Befuellung erfolgt ausschliesslich via High-Speed-COPY durch den Loader. |
| **stage** | Technische Bereinigung | Vereinheitlichung von Datentypen, Feldnamen und Formaten. Qualitaetspruefungen. (Exklusiv ueber dbt verwaltet). |
| **intermediate** | Zwischenergebnisse | Wiederverwendbare, komplexe Joins und Aggregationen, die von mehreren Modellen genutzt werden. (Exklusiv ueber dbt verwaltet). |
| **mart** | Core-Modell | Fachliches Data-Warehouse-Modell (Dimensionen und Faktentabellen) fuer Reporting und BI. (Exklusiv ueber dbt verwaltet). |
| **control** | Metadaten & Steuerung | Enthaelt Ladehistorie, Jobstatus, Scheduler-Informationen und Fehlerprotokolle. |

---

## Projektstruktur

```
RetailDWHPostgres/
│
├── .env                 # Lokale Umgebungsvariablen (nicht versioniert)
├── .env.example         # Vorlage fuer Umgebungsvariablen
├── .gitignore           # Git-Ausschlussregeln
├── pyproject.toml       # Projektspezifikationen (v0.3.0)
├── requirements.txt     # Python-Abhaengigkeiten
├── requirements.lock    # Fixierte Paketversionen
├── README.md            # Englische Dokumentation (geplant)
├── README.de.md         # Diese Dokumentation
│
├── archive/             # Verzeichnis fuer verarbeitete Quellmedien
├── config/              # Konfigurationsdateien (config.yaml)
├── dbt/                 # dbt-Transformationsmodelle
├── docs/                # Projektdokumentation
├── loader/              # Logik der Lade-Engine
├── logs/                # System- und Lade-Protokolle
├── orchestration/       # Dagster-Pipelines und Repositories
├── scripts/             # Hilfsskripte fuer Administration und Deployment
├── sql/                 # Reine SQL-Skripte und DDLs
├── src/                 # Python-Quellcode des Projekts (retaildwh)
└── tests/               # Test-Suiten fuer Pipeline-Komponenten
```

---

## Konfiguration

### `config/config.yaml`
Enthaelt die allgemeine, nicht-sensitive Projektkonfiguration sowie die Pfade zu den Datenquellen:
```yaml
paths:
  csv_source: ~/Projekte/RetailDWGen/output   # Pfad zum Generator-Output
  archive: ./archive
```
*Hinweis: Tilde-Pfade (`~`) werden vom Loader automatisch in das absolute Benutzerverzeichnis aufgeloest.*

### `.env`
Enthaelt ausschliesslich lokale, sensitive Zugangsdaten (Host, Port, Passwoerter) und wird niemals in Git versioniert. Nutzen Sie `.env.example` als Vorlage.

---

## Verwendung des Loaders

Um den Import einer bestimmten Entitaet aus den Quell-Stammdaten in den `raw`-Layer der PostgreSQL-Datenbank zu starten, fuehren Sie die `load.py` mit dem entsprechenden Pfad-Argument aus:

```bash
python load.py csv stammdaten/artikel
```

Der Loader ermittelt automatisch die neueste CSV-Datei im Quellpfad, prueft die Struktur, erstellt die Ziel-Tabelle im Schema `raw` dynamisch, falls diese noch nicht existiert, und schreibt die Daten via ultraschnellem `psycopg3`-Schreibstream (`COPY`). Nach erfolgreichem Laden wird die Datei automatisch ins Archiv verschoben.

---

## Projektstand

### Aktuell umgesetzt (v0.3.0)
* [x] Virtuelle Python-Umgebung & modernisierte Paketstruktur eingerichtet.
* [x] PostgreSQL-Datenbankstruktur sowie DWH-Zielschemas definiert.
* [x] Konfigurationsverwaltung ueber `config.yaml` und `.env` implementiert.
* [x] **High-Speed-CSV-Loader fertiggestellt:** Dynamische Tabellenerstellung im `raw`-Layer sowie performanter Daten-Streaming-Import via nativem `psycopg3 COPY` implementiert.
* [x] Automatische dateibasierte Archivierung nach erfolgreichem Daten-Commit integriert.

### Nächste Schritte
* [ ] Erweiterung der Ladehistorie und Jobsteuerung im `control`-Schema.
* [ ] dbt-Projekt fuer die Transformationen (`stage` -> `intermediate` -> `mart`) initialisieren.
* [ ] Dagster zur Orchestrierung der gesamten ELT-Pipeline einbinden.

---

## Autor

**Detlef Bracker**
RetailDWHPostgres ist ein Open-Source-Projekt zur Demonstration moderner Softwareentwicklung, relationaler Datenmodellierung sowie Data-Warehouse-Architekturen im Handelsumfeld.

---

## Lizenz

Dieses Projekt steht unter der **MIT License**.  
Copyright © Detlef Bracker  
Weitere Informationen befinden sich in der Datei `LICENSE`.
