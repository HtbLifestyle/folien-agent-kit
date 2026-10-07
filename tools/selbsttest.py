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

- Punkt eins mit sehr vielen Wörtern, die hier ausschließlich deshalb stehen, damit die seit dem siebten Oktober geltende Grenze von siebzig sichtbaren Wörtern je Folie in diesem Negativtest sicher und reproduzierbar gerissen wird, denn eine Grenze, deren Verletzung der eigene Selbsttest nicht mehr erzeugen kann, ist keine Grenze, sondern nur noch eine Zeile Dokumentation, die niemand je wieder prüft, und genau diesen stillen Zustand soll dieser absichtlich viel zu lange Stichpunkt mit seinen deutlich über siebzig Wörtern dauerhaft verhindern[^K01-001].

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
    ("F-06: zu dünnes Deck wird gemeldet",
     lambda r: "F-06" in r["duenn"].stdout and "zu dünn" in r["duenn"].stdout),
    ("F-06: Prosa-Minuten zählen nicht mit",
     lambda r: "F-06" not in r["prosa"].stdout),
]

# Vier Decks des Programms lagen still unter ihrem Zielwert, weil F-06 nur
# nach oben prüfte. Zielwert 60, Folien ergeben 20 — muss melden.
DUENN = """# Testdeck dünn
Budget: 2 Folien
Leinwandzeit: 60 min

## Folie 1: Erste (~12 min)

Beispiel: Etwas.
Regel: Etwas gilt.

## Folie 2: Quellen (~8 min)

- Alle Belege im Handout.
"""

# Minutenangaben in der Dramaturgie-Prosa sind keine Leinwandzeit. Eine
# Handzählung, die sie mitnahm, erfand drei Decks eine zu lange Zeit.
PROSA = """# Testdeck Prosa
Budget: 2 Folien
Leinwandzeit: 8 min

## Dramaturgie

- **Peak:** Folie 1 (~5 min) trägt den Kern, der Block danach (~30 min) nicht.

## Folie 1: Erste (~5 min)

Beispiel: Etwas.
Regel: Etwas gilt.

## Folie 2: Quellen (~3 min)

- Alle Belege im Handout.
"""



PAPIER_GATE = HIER / "papier_pruefen.py"

# Mermaid mit `-. label .-` erzeugte einen SP-05-Fehlalarm (Punkt plus
# Leerzeichen wurde als Satzende gelesen). Gemessen am 2026-10-06.
PAPIER_MERMAID = """# Testpapier
Session: T0 · Deck: x · Handout: y
Wortbudget: 900

## Was du jetzt kannst

Du kannst genau eine Sache. Und eine zweite.

```mermaid
flowchart TB
  A[Eins] --> B([Zwei])
  B -. leere Aussparung .- C[Drei]
```

*Eine Bildunterschrift als dritter Satz.*

## Die Handgriffe

1. **Ein Handgriff.**

   ```
   etwas tun
   ```

## Wenn es klemmt

- Es klemmt.

## Vertiefung

- Handout M0, Folie 1
"""


def papier_pruefen(text: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        w = Path(d) / "praesentationen" / "papers"
        w.mkdir(parents=True)
        (Path(d) / "praesentationen" / "grafiken").mkdir()
        f = w / "P-TEST.md"
        f.write_text(text, encoding="utf-8")
        r = subprocess.run([sys.executable, str(PAPIER_GATE), str(f)],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


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
        (d / "duenn.md").write_text(DUENN, encoding="utf-8")
        (d / "prosa.md").write_text(PROSA, encoding="utf-8")
        (d / "SPEZIFIKATION-gut.md").write_text(SPEZ, encoding="utf-8")
        r = {
            name: subprocess.run([sys.executable, str(GATE), str(d / f"{name}.md")],
                                 capture_output=True, text=True)
            for name in ("gut", "schlecht", "duenn", "prosa")
        }
    ok = 0
    for name, test in ERWARTUNGEN:
        if test(r):
            ok += 1
        else:
            print(f"FEHLT: {name}")

    # Papier-Gate: zwei Wartungsfälle vom 2026-10-06 festgenagelt.
    code_m, aus_m = papier_pruefen(PAPIER_MERMAID)
    for name, erfuellt in (
        ("SP-05 zählt Mermaid-Zeilen nicht als Sätze", "SP-05" not in aus_m),
        ("SP-06 meldet einen Mermaid-Block ohne .mmd-Quelle", "SP-06" in aus_m),
    ):
        if erfuellt:
            ok += 1
        else:
            print(f"FEHLT: {name}")
    gesamt = len(ERWARTUNGEN) + 2
    print("─" * 60)
    print(f"{ok} von {gesamt} Erwartungen erfüllt")
    raise SystemExit(0 if ok == gesamt else 1)


if __name__ == "__main__":
    main()
