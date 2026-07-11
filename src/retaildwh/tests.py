#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
Projekt : RetailDWHPostgres
Modul   : tests.py

Beschreibung:
    Systemtests für die Projektumgebung.

    Prüft:
    - Konfiguration
    - .env Integration
    - PostgreSQL Verbindung
    - erforderliche Data-Warehouse-Schemas

Autor   : Detlef Bracker
Version : 0.1.0
============================================================
"""

from retaildwh.config import Config
from retaildwh.database import Database


REQUIRED_SCHEMAS = [
    "raw",
    "stage",
    "intermediate",
    "mart",
    "control"
]


def test_config():
    """
    Prüft die Projektkonfiguration.
    """

    try:
        cfg = Config()

        database = cfg.database()

        required = [
            "host",
            "port",
            "database",
            "user",
            "password"
        ]

        missing = [
            item
            for item in required
            if not database.get(item)
        ]

        if missing:
            print(
                "[FEHLER] Fehlende Konfiguration: "
                + ", ".join(missing)
            )
            return False

        print("[OK] Konfiguration geladen")
        print("[OK] .env Werte vorhanden")

        return True

    except Exception as error:

        print(f"[FEHLER] Konfiguration: {error}")

        return False


def test_database():
    """
    Prüft die PostgreSQL-Verbindung.
    """

    try:

        cfg = Config()

        db = Database(cfg.database())

        version = db.test_connection()

        db.close()

        if version:

            print("[OK] PostgreSQL Verbindung")

            return True

        print("[FEHLER] PostgreSQL Verbindung")

        return False


    except Exception as error:

        print(f"[FEHLER] Datenbank: {error}")

        return False


def test_schemas():
    """
    Prüft die benötigten DWH-Schemas.
    """

    try:

        cfg = Config()

        db = Database(cfg.database())

        existing = db.get_schemas()

        db.close()

        success = True

        for schema in REQUIRED_SCHEMAS:

            if schema in existing:

                print(f"[OK] Schema {schema}")

            else:

                print(f"[FEHLER] Schema {schema} fehlt")

                success = False

        return success


    except Exception as error:

        print(f"[FEHLER] Schema-Test: {error}")

        return False


def main():
    """
    Führt alle Systemtests aus.
    """

    print("=" * 60)
    print("RetailDWHPostgres - Systemtest")
    print("=" * 60)
    print()

    results = []

    results.append(test_config())
    results.append(test_database())
    results.append(test_schemas())

    print()
    print("=" * 60)

    if all(results):
        print("Systemtest erfolgreich.")
    else:
        print("Systemtest mit Fehlern beendet.")

    print("=" * 60)


if __name__ == "__main__":
    main()
