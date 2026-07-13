#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Projekt : RetailDWHPostgres
Datei   : csv_loader.py
Version : 0.1.0

Beschreibung:
CSV-Importer.

Importiert CSV-Dateien in das Schema "raw".

Autor   : Detlef Bracker
Lizenz  : MIT License
============================================================
"""

from pathlib import Path


class CSVLoader:
    """Importiert CSV-Dateien in das Raw-Schema."""

    def __init__(self, config, database, source):
        self.config = config
        self.db = database
        self.source = source

        self.csv_root = Path(
            self.config.get("paths", "csv_source")
        ).expanduser()

        self.schema = self.config.get(
            "database",
            "schema_raw"
        )

        self.directory = None
        self.entity = None
        self.table = None
        self.file = None

    # ---------------------------------------------------------

    def run(self):
        print("[INFO] CSV-Importer gestartet")
        print()

        self.parse_source()
        self.find_files()
        self.validate_files()
        self.load_files()
        self.archive_files()

    # ---------------------------------------------------------

    def parse_source(self):
        parts = self.source.split("/")

        if len(parts) != 2:
            raise ValueError(
                "Ungültiger Ladeauftrag. Erwartet wird 'bereich/entitaet'."
            )

        self.directory = parts[0]
        self.entity = parts[1]
        self.table = f"{self.entity}_001"

        print(f"[OK] Bereich     : {self.directory}")
        print(f"[OK] Entität     : {self.entity}")
        print(f"[OK] Zieltabelle : {self.schema}.{self.table}")
        print()

    # ---------------------------------------------------------

    def find_files(self):
        folder = self.csv_root / self.directory

        if not folder.exists():
            raise FileNotFoundError(f"Verzeichnis nicht gefunden: {folder}")

        pattern = f"{self.entity}_*.csv"
        files = []

        for file in sorted(folder.glob(pattern)):
            if "check" in file.stem.lower():
                continue
            files.append(file)

        if len(files) == 0:
            raise FileNotFoundError(
                f"Keine CSV-Datei gefunden ({pattern})"
            )

        if len(files) > 1:
            print("[FEHLER] Mehrere passende Dateien gefunden:")
            print()
            for file in files:
                print(f"  {file.name}")
            print()
            raise RuntimeError(
                "Mehr als eine passende CSV-Datei gefunden."
            )

        self.file = files[0]

        print("[OK] CSV-Datei gefunden")
        print(f"     {self.file.name}")
        print()

    # ---------------------------------------------------------

    def validate_files(self):
        print("[INFO] Prüfe CSV-Datei ...")

        if not self.file.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {self.file}")

        size = self.file.stat().st_size
        if size == 0:
            raise RuntimeError("CSV-Datei ist leer.")

        print(f"[OK] Dateigröße : {size:,} Bytes")

        if self.file.suffix.lower() != ".csv":
            raise RuntimeError("Datei besitzt keine CSV-Erweiterung.")

        print("[OK] Dateiendung : .csv")

        with open(self.file, "r", encoding="utf-8", newline="") as fp:
            header = fp.readline().strip()

        if not header:
            raise RuntimeError("CSV-Datei besitzt keine Kopfzeile.")

        if ";" not in header:
            raise RuntimeError(
                "CSV-Datei besitzt kein ';' als Trennzeichen."
            )

        columns = [c.strip() for c in header.split(";")]

        if len(columns) < 2:
            raise RuntimeError("CSV-Datei besitzt zu wenige Spalten.")

        duplicates = sorted(
            {c for c in columns if columns.count(c) > 1}
        )

        if duplicates:
            raise RuntimeError(
                "Doppelte Spaltennamen gefunden: "
                + ", ".join(duplicates)
            )

        print(f"[OK] Spalten      : {len(columns)}")
        print("[OK] UTF-8        : gültig")
        print("[OK] Kopfzeile    : vorhanden")
        print("[OK] Trennzeichen : ';'")
        print()

    # ---------------------------------------------------------

    def load_files(self):
        print("[INFO] CSV-Import")
        print("       Noch nicht implementiert.")
        print()

    # ---------------------------------------------------------

    def archive_files(self):
        print("[INFO] Archivierung")
        print("       Noch nicht implementiert.")
        print()
