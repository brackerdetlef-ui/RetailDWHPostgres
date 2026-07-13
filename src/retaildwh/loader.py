#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Projekt : RetailDWHPostgres
Datei   : loader.py
Version : 0.1.0

Beschreibung:
Zentrale Lade-Engine des Retail Data Warehouse.

Der Loader steuert den Import von Quelldaten in das
Schema "raw". Die eigentliche Importlogik wird an einen
Importer (CSV, JSON, XML, ...) delegiert.

Autor   : Detlef Bracker
Lizenz  : MIT License
============================================================
"""

from retaildwh.config import Config
from retaildwh.database import Database

# momentan existiert nur dieser Importer
from retaildwh.importer.csv_loader import CSVLoader


class Loader:
    """Zentrale Steuerung des Datenimports."""

    def __init__(self, source_type: str, source: str):

        self.source_type = source_type.lower()
        self.source = source

        self.config = Config()
        self.db = Database(self.config.database())

        self.importer = None

    # ---------------------------------------------------------

    def run(self):
        """Startet den Ladevorgang."""

        self.print_header()

        if not self.connect_database():
            return False

        if not self.select_importer():
            return False

        self.importer.run()

        self.finish()

        return True

    # ---------------------------------------------------------

    def print_header(self):

        print("=" * 60)
        print("RetailDWHPostgres")
        print("Loader")
        print("=" * 60)
        print()

        print(f"Quelltyp : {self.source_type}")
        print(f"Auftrag  : {self.source}")
        print()

    # ---------------------------------------------------------

    def connect_database(self):

        try:

            version = self.db.test_connection()

            print("[OK] PostgreSQL verbunden")
            print(version)
            print()

            return True

        except Exception as exc:

            print("[FEHLER] Datenbankverbindung")
            print(exc)

            return False

    # ---------------------------------------------------------

    def select_importer(self):

        if self.source_type == "csv":

            self.importer = CSVLoader(
                config=self.config,
                database=self.db,
                source=self.source,
            )

            return True

        print(f"[FEHLER] Importtyp '{self.source_type}' wird nicht unterstützt.")

        return False

    # ---------------------------------------------------------

    def finish(self):

        self.db.close()

        print()
        print("=" * 60)
        print("Ladevorgang beendet.")
        print("=" * 60)
