#!/usr/bin/env python3
"""Selbsttest des folien-kit: feste Erwartungen gegen eingebaute Fixtures.

    selbsttest.py

Exit 0 wenn alle Erwartungen erfüllt, 1 sonst. Kein Netz, keine Seiteneffekte
außer einem Temp-Ordner.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
GATE = HIER / "folien_pruefen.py"

GUT = """# Testdeck
Budget: 2 Folien
Leinwandzeit: 8 min

## Folie 1: Beispiel trägt (~5 min)

**Form:** Kernsatz

Beispiel: Du sagst nur noch, was der Brief erreichen soll.
Regel: Neu ist Hilfe an der ganzen Aufgabe.

Sprechnotiz: Diese Zeile zählt nicht zu den sichtbaren Wörtern, auch wenn sie
lang ist, über mehrere Zeilen umbricht und dabei sehr viele Wörter enthält,
die alle nicht auf der Leinwand stehen und darum nicht gezählt werden dürfen.
Handout: M1, Folie 2.

```text
Codezaun zählt ebenfalls nicht, egal wie viele Wörter hier stehen oder wie lang die Zeile wird.
```

## Folie 2: Quellen (~3 min)

- Alle Belege im Handout.
"""

SCHLECHT = """# Testdeck schlecht
Budget: 1 Folien

## Folie 1: Zu viel (~5 min)

Regel: Erst die Regel, Beispiel vergessen.

- Punkt eins mit vielen Wörtern, die hier nur stehen, damit die Grenze von fünfundzwanzig sichtbaren Wörtern sicher gerissen wird[^K01-001].

- Zweiter getrennter Block nach Leerzeile.

## Folie 2: Überzählig (~4 min)

- Noch eine Folie.
"""

ERWARTUNGEN = [
    ("gut: genau der eine F-07", lambda r: r["gut"].returncode == 1 and r["gut"].stdout.count("F-07") == 1),
    ("gut: sonst keine Befunde", lambda r: "1 Befunde" in r["gut"].stdout),
    ("schlecht: Exit 1", lambda r: r["schlecht"].returncode == 1),
    ("schlecht: F-01 Budget", lambda r: "F-01" in r["schlecht"].stdout),
    ("schlecht: F-02 Wörter", lambda r: "F-02" in r["schlecht"].stdout),
    ("schlecht: F-03 zwei Blöcke trotz Leerzeile", lambda r: "F-03" in r["schlecht"].stdout),
    ("schlecht: F-04 Fußnote", lambda r: "F-04" in r["schlecht"].stdout),
    ("schlecht: F-05 Regel ohne Beispiel", lambda r: "F-05" in r["schlecht"].stdout),
    ("schlecht: F-06 Leinwandzeit fehlt", lambda r: "F-06" in r["schlecht"].stdout),
    ("gut: Meta-Zeilen zählen nicht (sonst F-02)", lambda r: "F-02" not in r["gut"].stdout),
    ("gut: Codezaun zählt nicht", lambda r: "Folie 1" not in r["gut"].stdout),
    ("gut: umbrochene Sprechnotiz zählt nicht", lambda r: "F-02" not in r["gut"].stdout),
    ("F-07: fehlender MUSS-Punkt gemeldet", lambda r: "F-07" in r["gut"].stdout and "Verschwundener Punkt" in r["gut"].stdout),
    ("F-07: gedeckter MUSS-Punkt still", lambda r: "Beispiel trägt" not in r["gut"].stdout),
    ("F-07: GESTRICHEN wird übersprungen", lambda r: "Alte Idee" not in r["gut"].stdout),
]


def main():
    SPEZ = (
        "# Spez\n"
        "MUSS: Beispiel trägt — Handout: M1 F2 — 5 min\n"
        "MUSS: Verschwundener Punkt — Handout: M1 F6 — 2 min\n"
        "MUSS: Alte Idee — Handout: M1 F9 — 2 min — GESTRICHEN (Prüfer-Entscheid)\n"
    )
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "gut.md").write_text(GUT, encoding="utf-8")
        (d / "schlecht.md").write_text(SCHLECHT, encoding="utf-8")
        (d / "SPEZIFIKATION-gut.md").write_text(SPEZ, encoding="utf-8")
        r = {
            name: subprocess.run([sys.executable, str(GATE), str(d / f"{name}.md")],
                                 capture_output=True, text=True)
            for name in ("gut", "schlecht")
        }
    ok = 0
    for name, test in ERWARTUNGEN:
        if test(r):
            ok += 1
        else:
            print(f"FEHLT: {name}")
    print("─" * 60)
    print(f"{ok} von {len(ERWARTUNGEN)} Erwartungen erfüllt")
    raise SystemExit(0 if ok == len(ERWARTUNGEN) else 1)


if __name__ == "__main__":
    main()
