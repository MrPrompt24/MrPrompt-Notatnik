#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt konfiguracyjny — pobiera słownik Hunspell języka polskiego (pl_PL)
dla MrPrompt Notatnik. Ten sam słownik jest używany w LibreOffice.
Pliki trafiają do folderu "slownik" obok programu.
"""

import os
import sys
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/LibreOffice/dictionaries/master/pl_PL/"
FILES = ("pl_PL.aff", "pl_PL.dic")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slownik")


def setup() -> bool:
    """Pobierz słownik, jeśli go brakuje. Zwraca True, gdy pliki są na dysku."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for name in FILES:
        target = os.path.join(OUTPUT_DIR, name)
        if os.path.exists(target) and os.path.getsize(target) > 1000:
            continue
        print(f"Pobieranie: {name} ...")
        try:
            req = urllib.request.Request(BASE_URL + name, headers={"User-Agent": "MrPromptNotatnik/2.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
            with open(target, "wb") as fh:
                fh.write(data)
        except Exception as exc:
            print(f"[BLAD] Nie udalo sie pobrac {name}: {exc}")
            print("Sprawdz polaczenie z internetem i sprobuj ponownie.")
            return False

    print(f"[OK] Slownik gotowy: {OUTPUT_DIR}")
    return True


if __name__ == "__main__":
    sys.exit(0 if setup() else 1)
