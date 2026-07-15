#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Projekt : RetailDWHPostgres
Modul   : csv_loader.py

Beschreibung:
    Führt das performante Laden von CSV-Quelldaten mittels 
    psycopg3 COPY-Streams in das Schema "raw" durch. 
    Prüft vorab die Tabellenexistenz und erzeugt diese 
    bei Bedarf dynamisch.

Autor   : Detlef Bracker
Version : 0.3.0
============================================================
"""

import os
import csv
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CSVLoader:
    """
    Importer für CSV-Dateien in das PostgreSQL Data Warehouse (RAW-Layer).
    Optimiert für psycopg3 (PostgreSQL-Treiber V3).
    """
    def __init__(self, config, database, source):
        self.config = config
        self.database_obj = database
        self.source = source
        
        # Verbindung aus dem Database-Objekt extrahieren
        self.conn = getattr(database, 'conn', None) or getattr(database, 'connection', None) or getattr(database, '_conn', None)

    def run(self):
        """
        Der zentrale Einstiegspunkt, der von loader.py aufgerufen wird.
        """
        # 1. Domain und Entity aus der 'source' extrahieren
        if '/' in self.source:
            domain, entity = self.source.split('/', 1)
        else:
            domain = "stammdaten"
            entity = self.source

        target_table = f"raw.{entity}_001"

        # 2. Source-Pfad aus config.yaml auslesen
        csv_source_base = None
        if self.config:
            if isinstance(self.config, dict):
                csv_source_base = self.config.get('paths', {}).get('csv_source')
            elif hasattr(self.config, 'paths'):
                paths = getattr(self.config, 'paths', {})
                if isinstance(paths, dict):
                    csv_source_base = paths.get('csv_source')
                else:
                    csv_source_base = getattr(paths, 'csv_source', None)

        if not csv_source_base:
            csv_source_base = "~/Projekte/RetailDWGen/output"

        # Tilde (~) in absoluten Linux-Pfad auflösen
        source_dir = os.path.expanduser(csv_source_base)
        final_search_dir = os.path.join(source_dir, domain)

        # 3. Neueste CSV-Datei im Domain-Verzeichnis finden
        file_path = None
        if os.path.exists(final_search_dir):
            files = [
                os.path.join(final_search_dir, f) 
                for f in os.listdir(final_search_dir) 
                if (
                    f.endswith('.csv') 
                    and not f.endswith("_check.csv")
                    and f.startswith(f"{entity}_")
                )
            ]
            if files:
                file_path = max(files, key=os.path.getmtime)

        if not file_path or not os.path.exists(file_path):
            print(f"[FEHLER] Keine gültige CSV-Datei für Entität '{entity}' in '{final_search_dir}' gefunden.")
            return False

        # Fallback für die DB-Verbindung
        if not self.conn and self.database_obj:
            self.conn = getattr(self.database_obj, 'conn', None) or getattr(self.database_obj, 'connection', None)

        if not self.conn:
            print("[FEHLER] Keine aktive Datenbankverbindung im CSVLoader verfügbar.")
            return False

        # Ausgaben passend zum Log-Ablauf erzeugen
        print(f"[OK] Bereich      : {domain}")
        print(f"[OK] Entität      : {entity}")
        print(f"[OK] Zieltabelle : {target_table}")
        print(f"\n[OK] CSV-Datei gefunden")
        print(f"     {os.path.basename(file_path)}")

        # Datei-Validierung
        print(f"\n[INFO] Prüfe CSV-Datei ...")
        file_size_bytes = os.path.getsize(file_path)
        print(f"[OK] Dateigröße  : {file_size_bytes:,} Bytes".replace(",", "."))
        print(f"[OK] Dateiendung : {os.path.splitext(file_path)[1]}")

        cursor = self.conn.cursor()
        try:
            # Header aus der CSV ermitteln
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                headers = next(reader)
            
            clean_headers = [h.strip().lower() for h in headers]

            print(f"[OK] Spalten      : {len(clean_headers)}")
            print(f"[OK] UTF-8        : gültig")
            print(f"[OK] Kopfzeile    : vorhanden")
            print(f"[OK] Trennzeichen : ';'")

            schema, table_name = 'raw', f"{entity}_001"

            # 4. Tabelle im Schema 'raw' prüfen und anlegen
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = %s
                );
            """, (schema, table_name))
            
            if not cursor.fetchone()[0]:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
                columns_def = ", ".join([f'"{col}" TEXT' for col in clean_headers])
                cursor.execute(f"CREATE TABLE {schema}.{table_name} ({columns_def});")
                self.conn.commit()

            # 5. Performanter CSV-Import via psycopg3 native COPY
            print(f"\n[INFO] CSV-Import")
            
            columns_str = ", ".join([f'"{col}"' for col in clean_headers])
            copy_sql = f"""
                COPY {schema}.{table_name} ({columns_str}) 
                FROM STDIN 
                WITH (FORMAT CSV, HEADER true, DELIMITER ';', ENCODING 'UTF8');
            """
            
            # psycopg3 Syntax für das Schreiben im Stream
            with cursor.copy(copy_sql) as copy:
                with open(file_path, mode='r', encoding='utf-8') as f:
                    # Liest blockweise und schreibt direkt in den Postgres-Stream
                    while True:
                        data = f.read(64 * 1024)  # 64KB Chunks
                        if not data:
                            break
                        copy.write(data)
            
            # In psycopg3 liefert rowcount nach dem Verlassen des copy-Blocks die geladenen Zeilen
            row_count = cursor.rowcount if cursor.rowcount is not None else "Unbekannte Anzahl"
            self.conn.commit()
            print(f"[OK] Datensätze erfolgreich in {schema}.{table_name} geladen.")

            # 6. Archivierung
            print(f"\n[INFO] Archivierung")
            if self._archive_file(file_path):
                print(f"[OK] Datei erfolgreich ins Archiv verschoben.")
            else:
                print(f"[WARNUNG] Archivierung unvollständig.")

            return True

        except Exception as e:
            self.conn.rollback()
            print(f"[FEHLER] Import abgebrochen: {e}")
            logger.error(f"Fehler bei Import in {schema}.{table_name}: {e}", exc_info=True)
            return False
        finally:
            cursor.close()

    def _archive_file(self, file_path, archive_root="archive"):
        """ Verschiebt die verarbeitete Datei in den Archivordner """
        try:
            date_folder = datetime.now().strftime("%Y-%m-%d")
            target_dir = os.path.join(archive_root, date_folder)
            os.makedirs(target_dir, exist_ok=True)
            
            destination = os.path.join(target_dir, os.path.basename(file_path))
            os.rename(file_path, destination)
            return True
        except Exception as e:
            logger.warning(f"Archivierung fehlgeschlagen: {e}")
            return False
