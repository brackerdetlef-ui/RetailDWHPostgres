#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
RetailDWHPostgres
Systemtest

Startet die Systemtests für das Projekt.

Aufruf:

    python test.py

Später sind zusätzliche Testgruppen vorgesehen:

    python test.py db
    python test.py config
    python test.py schemas

============================================================
"""

from retaildwh.tests import main


if __name__ == "__main__":
    main()
