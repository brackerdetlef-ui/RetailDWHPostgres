#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Projekt : RetailDWHPostgres
Datei   : load.py
Version : 0.1.0

Beschreibung:
Startprogramm des Retail Data Warehouse.

Autor   : Detlef Bracker
Lizenz  : MIT License
============================================================
"""

from sys import argv

from retaildwh.loader import Loader


def main():

    if len(argv) != 3:
        print("Aufruf:")
        print()
        print("    python load.py csv stammdaten/artikel")
        return

    source_type = argv[1]
    source = argv[2]

    loader = Loader(source_type, source)
    loader.run()


if __name__ == "__main__":
    main()
