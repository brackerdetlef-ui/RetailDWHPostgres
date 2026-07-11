#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
Projekt : RetailDWHPostgres
Modul   : config.py

Beschreibung:
    Liest die Projektkonfiguration aus der Datei
    config/config.yaml und ergänzt die Werte aus der
    lokalen .env-Datei.

Autor   : Detlef Bracker
Version : 0.1.0
============================================================
"""

from pathlib import Path
import os

import yaml
from dotenv import load_dotenv


class Config:
    """Verwaltung der Projektkonfiguration."""

    def __init__(self):

        # Projektverzeichnis bestimmen
        self.project_root = Path(__file__).resolve().parents[2]

        # .env laden
        load_dotenv(self.project_root / ".env")

        # config.yaml laden
        config_file = self.project_root / "config" / "config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Konfigurationsdatei nicht gefunden: {config_file}"
            )

        with open(config_file, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    # --------------------------------------------------------

    def get(self, *keys, default=None):
        """
        Zugriff auf verschachtelte YAML-Einträge.

        Beispiel:

            cfg.get("database", "schemas", "raw")
        """

        value = self.config

        for key in keys:

            if not isinstance(value, dict):
                return default

            value = value.get(key)

            if value is None:
                return default

        return value

    # --------------------------------------------------------

    def getenv(self, variable):
        """
        Liest eine Umgebungsvariable aus der .env-Datei.
        """

        return os.getenv(variable)

    # --------------------------------------------------------

    def database(self):
        """
        Liefert die Datenbankparameter.
        """

        db = self.config["database"]

        return {

            "host": os.getenv(db["host"]),

            "port": os.getenv(db["port"]),

            "database": os.getenv(db["database"]),

            "user": os.getenv(db["user"]),

            "password": os.getenv(db["password"])

        }
