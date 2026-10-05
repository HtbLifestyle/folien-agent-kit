#!/usr/bin/env python3
"""Prüft Dünn-Decks gegen die messbaren Leinwand-Regeln.

    folien_pruefen.py <deck.md> [...] [--still]

Geprüft wird nur Mechanisches (P-04):
  F-01  Folienbudget: Kopfzeile `Budget: <n> Folien` wird gegen die Zahl
        der `## Folie`-Überschriften gehalten (Quellen-Folie zählt mit).
  F-02  Sichtbarer Text je Folie ≤ 25 Wörter (Bullets und Freitext;
        nicht gezählt: Sprechnotiz:, Demo:, Jetzt du:, Form:, Skizze:,
        Handout:, Code-Zäune, Folientitel).
  F-03  Ein Gedanke je Folie: höchstens EIN zusammenhängender Bullet-Block.
  F-04  Keine Fußnoten auf der Leinwand: `[^...]` ist verboten; Belege
        gehören ins Handout. Erlaubt ist je Folie eine `Handout:`-Zeile.
  F-05  Beispiel vor Regel: trägt eine Folie eine `Regel:`-Zeile, muss
        davor auf derselben Folie eine `Beispiel:`-Zeile stehen.
  F-06  Leinwandzeit: Summe der `(~n min)`-Angaben der Folientitel gegen
        die Kopfzeile `Leinwandzeit: <n> min`.

Exit 0 ohne Befund, 1 mit Befunden. Schreibt gates/folien-report.md,
wenn das Deck in einem Dokumentprojekt liegt.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gemeinsam as g  # noqa: E402

FOLIE = re.compile(r"^## Folie (\d+)[^\n]*?(?:\(~(\d+)\s*min\))?\s*$", re.M)
WORT = re.compile(r"\b[\wäöüÄÖÜß-]+\b")
META = ("Sprechnotiz:", "Demo:", "Jetzt du:", "**Form:**", "**Skizze:**",
        "Handout:", "**Sprechnotiz", "**Demo", "**Jetzt du", "**Handout")


def folien_teilen(text: str) -> list[tuple[int, int | None, str]]:
    """Liefert (foliennummer, minuten, folientext)."""
    treffer = list(FOLIE.finditer(text))
    ergebnis = []
    for i, m in enumerate(treffer):
        ende = treffer[i + 1].start() if i + 1 < len(treffer) else len(text)
        minuten = int(m.group(2)) if m.group(2) else None
        ergebnis.append((int(m.group(1)), minuten, text[m.end():ende]))
    return ergebnis


def sichtbarer_text(folie: str) -> list[str]:
    """Sichtbare Zeilen; Leerzeilen bleiben als "" erhalten, damit der
    Blockzähler Bullet-Gruppen trennen kann. META-Zeilen (Sprechnotiz: usw.)
    verschlucken auch ihre umbrochenen Folgezeilen bis zur Leerzeile —
    der Fehlbefund des ersten Pilotlaufs (12x F-02 auf einem sauberen Deck)."""
    zeilen, im_zaun, im_meta, out = folie.splitlines(), False, False, []
    for z in zeilen:
        s = z.strip()
        if s.startswith(("```", "~~~")):
            im_zaun = not im_zaun
            continue
        if im_zaun or s.startswith("---"):
            continue
        if not s:
            im_meta = False
            out.append(s)
            continue
        if any(s.startswith(m) for m in META):
            im_meta = True
            continue
        if im_meta:
            continue
        out.append(s)
    return out


def pruefen(datei: Path) -> list[dict]:
    text = datei.read_text(encoding="utf-8", errors="replace")
    b: list[dict] = []

    def befund(regel, ort, meldung):
        b.append({"regel": regel, "ort": f"{datei.name}:{ort}", "text": meldung})

    folien = folien_teilen(text)
    if not folien:
        befund("F-01", 1, "Keine `## Folie`-Überschriften gefunden — kein Dünn-Deck?")
        return b

    m = re.search(r"^Budget:\s*(\d+)\s*Folien", text, re.M)
    if not m:
        befund("F-01", 1, "Kopfzeile `Budget: <n> Folien` fehlt")
    elif len(folien) > int(m.group(1)):
        befund("F-01", 1, f"{len(folien)} Folien bei Budget {m.group(1)}")

    for nr, minuten, inhalt in folien:
        zeilen = sichtbarer_text(inhalt)
        woerter = sum(len(WORT.findall(z)) for z in zeilen if z)
        if woerter > 25:
            befund("F-02", nr, f"Folie {nr}: {woerter} sichtbare Wörter (max 25)")

        bloecke, offen = 0, False
        for z in zeilen:
            ist_bullet = z.startswith(("-", "*", "•")) or re.match(r"^\d+[.)]", z)
            if ist_bullet and not offen:
                bloecke += 1
            offen = ist_bullet
        if bloecke > 1:
            befund("F-03", nr, f"Folie {nr}: {bloecke} getrennte Bullet-Blöcke (max 1)")

        if re.search(r"\[\^[A-Za-z0-9][\w-]*\]", inhalt):
            befund("F-04", nr, f"Folie {nr}: Fußnote auf der Leinwand — gehört ins Handout")

        regel_pos = inhalt.find("Regel:")
        if regel_pos >= 0:
            beispiel_pos = inhalt.find("Beispiel:")
            if beispiel_pos < 0 or beispiel_pos > regel_pos:
                befund("F-05", nr, f"Folie {nr}: `Regel:` ohne vorangehendes `Beispiel:`")

    m = re.search(r"^Leinwandzeit:\s*(\d+)\s*min", text, re.M)
    if m:
        soll = int(m.group(1))
        ist = sum(mi for _, mi, _ in folien if mi)
        if ist > soll:
            befund("F-06", 1, f"Leinwandzeit {ist} min über Budget {soll} min")
    else:
        befund("F-06", 1, "Kopfzeile `Leinwandzeit: <n> min` fehlt")

    return b


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dateien", nargs="+")
    ap.add_argument("--still", action="store_true")
    a = ap.parse_args()

    dateien = [Path(d) for d in a.dateien if Path(d).exists()]
    befunde = [x for d in dateien for x in pruefen(d)]

    w = g.wurzel(dateien[0].resolve().parent if dateien else None)
    if w is not None:
        z = ["<!-- GENERIERT von folien_pruefen.py -->", "# Gate: Folien", "",
             f"Stand {g.heute()} · {len(dateien)} Decks · {len(befunde)} Befunde", ""]
        z += [f"- `{x['ort']}` — {x['regel']} — {x['text']}" for x in befunde] or ["Kein Befund.", ""]
        g.bericht_schreiben(w, "folien-report.md", "\n".join(z))
        nach_regel: dict[str, int] = {}
        for x in befunde:
            nach_regel[x["regel"]] = nach_regel.get(x["regel"], 0) + 1
        g.spur(w, "gate", werkzeug="folien_pruefen",
               dateien=[d.name for d in dateien], befunde=len(befunde),
               nach_regel=nach_regel, ausloeser="lauf")

    if not a.still:
        print(f"{len(dateien)} Decks, {len(befunde)} Befunde")
        for x in befunde[:20]:
            print(f"  {x['regel']}  {x['ort']}  {x['text'][:90]}")
    raise SystemExit(1 if befunde else 0)


if __name__ == "__main__":
    main()
