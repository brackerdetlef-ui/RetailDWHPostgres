RetailDWHPostgres
Projektbeschreibung
RetailDWHPostgres ist ein Lern- und Referenzprojekt zum Aufbau eines modernen Data Warehouse auf Basis von PostgreSQL. Das Projekt verfolgt das Ziel, eine Architektur zu entwickeln, die später mit möglichst wenigen Änderungen auch auf Cloud-Plattformen wie Snowflake oder Google BigQuery betrieben werden kann.

Dabei werden ausschließlich etablierte Open-Source-Werkzeuge verwendet.

Geplante und eingesetzte Komponenten:

PostgreSQL (v15+)

Python (v3.10+)

dbt (Data Build Tool)

Dagster (Orchestrierung)

Git / GitHub

Datengrundlage & Kooperation
Dieses Data Warehouse arbeitet nicht mit isolierten Beispieldaten, sondern ist direkt mit dem Schwesterprojekt RetailDWGen verzahnt.

Daten-Generator: https://github.com/brackerdetlef-ui/RetailDWGen/

Die dort erzeugten, realistischen Handelsdaten (Stammdaten wie Artikel, Kunden, Lieferanten sowie Transaktionsdaten) dienen als direkte Quellgrundlage für dieses DWH. Der integrierte Python-Loader greift standardmäßig auf das Ausgabe-Verzeichnis von RetailDWGen zu, um die CSV-Dateien hochperformant einzulesen.

Projektarchitektur
Die Datenverarbeitung erfolgt konsequent nach dem ELT-Prinzip (Extract, Load, Transform).

[ RetailDWGen (Output) ]
│
▼ (CSV-Dateien)
[ Loader (Python / psycopg3) ]
│
▼
[ PostgreSQL (Schema: raw) ]
│
▼
[ dbt stage ]
│
▼
[ dbt intermediate ]
│
▼
[ dbt mart ]

Die Orchestrierung der einzelnen Verarbeitungsschritte sowie die Überwachung der Pipelines erfolgt später zentral über Dagster.

Voraussetzungen
Python: Version 3.10 oder höher

PostgreSQL: Version 15 oder höher (inkl. installierter Client-Bibliotheken für psycopg3)

Datenbasis: Ein lokales Verzeichnis mit generierten CSV-Daten aus dem Projekt RetailDWGen.

Installation & Einrichtung
Repository klonen & Verzeichnis betreten:
git clone 
cd RetailDWHPostgres

Virtuelle Python-Umgebung erstellen & aktivieren:
python3 -m venv .venv
source .venv/bin/activate

Abhängigkeiten installieren:
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

Hinweis: Zur Dokumentation der exakt installierten Versionen kann anschließend "pip freeze > requirements.lock" ausgeführt werden.

PostgreSQL-Konfiguration
Projektbenutzer und Datenbank anlegen:
Melden Sie sich als PostgreSQL-Administrator an (sudo -u postgres psql) und führen Sie folgende SQL-Befehle aus:

CREATE ROLE retaildwh WITH LOGIN PASSWORD '';
CREATE DATABASE "retailDWH" OWNER retaildwh ENCODING 'UTF8';

Datenbankschemas initialisieren:
Verbinden Sie sich mit der neuen Datenbank (\c retailDWH) und legen Sie die DWH-Schichten an:

CREATE SCHEMA raw          AUTHORIZATION retaildwh;
CREATE SCHEMA stage        AUTHORIZATION retaildwh;
CREATE SCHEMA intermediate AUTHORIZATION retaildwh;
CREATE SCHEMA mart         AUTHORIZATION retaildwh;
CREATE SCHEMA control      AUTHORIZATION retaildwh;

Bedeutung der Schemas
raw (Landing Zone): Unveränderte Quelldaten. Es erfolgen keinerlei Transformationen. Befüllung erfolgt ausschließlich via High-Speed-COPY durch den Loader.

stage (Technische Bereinigung): Vereinheitlichung von Datentypen, Feldnamen und Formaten. Qualitätsprüfungen. (Exklusiv über dbt verwaltet).

intermediate (Zwischenergebnisse): Wiederverwendbare, komplexe Joins und Aggregationen, die von mehreren Modellen genutzt werden. (Exklusiv über dbt verwaltet).

mart (Core-Modell): Fachliches Data-Warehouse-Modell (Dimensionen und Faktentabellen) für Reporting und BI. (Exklusiv über dbt verwaltet).

control (Metadaten & Steuerung): Enthält Ladehistorie, Jobstatus, Scheduler-Informationen und Fehlerprotokolle.

Projektstruktur
RetailDWHPostgres/
├── .env                 # Lokale Umgebungsvariablen (nicht versioniert)
├── .env.example         # Vorlage für Umgebungsvariablen
├── .gitignore           # Git-Ausschlussregeln
├── pyproject.toml       # Projektspezifikationen (v0.3.0)
├── requirements.txt     # Python-Abhängigkeiten
├── requirements.lock    # Fixierte Paketversionen
├── README.md            # Englische Dokumentation (geplant)
├── README.de.md         # Diese Dokumentation
│
├── archive/             # Verzeichnis für verarbeitete Quellmedien
├── config/              # Konfigurationsdateien (config.yaml)
├── dbt/                 # dbt-Transformationsmodelle
├── docs/                # Projektdokumentation
├── loader/              # Logik der Lade-Engine
├── logs/                # System- und Lade-Protokolle
├── orchestration/       # Dagster-Pipelines und Repositories
├── scripts/             # Hilfsskripte für Administration und Deployment
├── sql/                 # Reine SQL-Skripte und DDLs
├── src/                 # Python-Quellcode des Projekts (retaildwh)
└── tests/               # Test-Suiten für Pipeline-Komponenten

Konfiguration
config/config.yaml
Enthält die allgemeine, nicht-sensitive Projektkonfiguration sowie die Pfade zu den Datenquellen:
paths:
csv_source: ~/Projekte/RetailDWGen/output
archive: ./archive

Hinweis: Tilde-Pfade (~) werden vom Loader automatisch in das absolute Benutzerverzeichnis aufgelöst.

.env
Enthält ausschließlich lokale, sensitive Zugangsdaten (Host, Port, Passwörter) und wird niemals in Git versioniert. Nutzen Sie .env.example as Vorlage.

Verwendung des Loaders
Um den Import einer bestimmten Entität aus den Quell-Stammdaten in den raw-Layer der PostgreSQL-Datenbank zu starten, führen Sie die load.py mit dem entsprechenden Pfad-Argument aus:

python load.py csv stammdaten/artikel

Der Loader ermittelt automatisch die neueste CSV-Datei im Quellpfad, prüft die Struktur, erstellt die Ziel-Tabelle im Schema raw dynamisch, falls diese noch nicht existiert, und schreibt die Daten via ultraschnellem psycopg3-Schreibstream (COPY). Nach erfolgreichem Laden wird die Datei automatisch ins Archiv verschoben.

Projektstand
Aktuell umgesetzt (v0.3.0)
Virtuelle Python-Umgebung & modernisierte Paketstruktur eingerichtet.

PostgreSQL-Datenbankstruktur sowie DWH-Zielschemas definiert.

Konfigurationsverwaltung über config.yaml und .env implementiert.

High-Speed-CSV-Loader fertiggestellt: Dynamische Tabellenerstellung im raw-Layer sowie performanter Daten-Streaming-Import via nativem psycopg3 COPY implementiert.

Automatische dateibasierte Archivierung nach erfolgreichem Daten-Commit integriert.

Nächste Schritte
Erweiterung der Ladehistorie und Jobsteuerung im control-Schema.

dbt-Projekt für die Transformationen (stage -> intermediate -> mart) initialisieren.

Dagster zur Orchestrierung der gesamten ELT-Pipeline einbinden.

Autor
Detlef Bracker
RetailDWHPostgres ist ein Open-Source-Projekt zur Demonstration moderner Softwareentwicklung, relationaler Datenmodellierung sowie Data-Warehouse-Architekturen im Handelsumfeld.

Lizenz
Dieses Projekt steht unter der MIT License.
Copyright © Detlef Bracker
Weitere Informationen befinden sich in der Datei LICENSE.
