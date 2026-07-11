#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
Projekt : RetailDWHPostgres
Modul   : database.py

Beschreibung:
    Verwaltung der PostgreSQL-Datenbankverbindung.

    Dieses Modul kapselt:
    - Verbindung zu PostgreSQL
    - einfache SQL-Abfragen
    - Prüfung der Datenbankschemas

Autor   : Detlef Bracker
Version : 0.1.0
============================================================
"""

import psycopg


class Database:
    """
    PostgreSQL Datenbankverbindung.
    """

    def __init__(self, config):
        """
        Initialisiert die Datenbankverbindung.

        Erwartet ein Dictionary:

        {
            host: ...,
            port: ...,
            database: ...,
            user: ...,
            password: ...
        }
        """

        self.config = config
        self.connection = None


    def connect(self):
        """
        Baut die Verbindung zu PostgreSQL auf.
        """

        self.connection = psycopg.connect(
            host=self.config["host"],
            port=self.config["port"],
            dbname=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )

        return self.connection


    def close(self):
        """
        Schließt die Datenbankverbindung.
        """

        if self.connection:
            self.connection.close()
            self.connection = None


    def test_connection(self):
        """
        Prüft, ob die Datenbankverbindung funktioniert.

        Liefert:
            True  - Verbindung OK
            False - Fehler
        """

        try:

            if self.connection is None:
                self.connect()

            with self.connection.cursor() as cursor:

                cursor.execute(
                    "SELECT version();"
                )

                result = cursor.fetchone()

            return result[0]

        except Exception:

            return False


    def get_schemas(self):
        """
        Liefert die vorhandenen Schemas der Datenbank.
        """

        if self.connection is None:
            self.connect()

        sql = """
        SELECT schema_name
        FROM information_schema.schemata
        ORDER BY schema_name;
        """

        with self.connection.cursor() as cursor:

            cursor.execute(sql)

            schemas = cursor.fetchall()

        return [
            schema[0]
            for schema in schemas
        ]
