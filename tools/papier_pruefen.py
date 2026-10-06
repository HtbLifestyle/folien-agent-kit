#!/usr/bin/env python3
"""Prüft Short Papers gegen die messbaren Nachschlag-Regeln.

    papier_pruefen.py <paper.md> [...]

  SP-01  Wortbudget: Kopfzeile `Wortbudget: <n>`; Fließtext (ohne Codezäune,
         Mermaid, Bild-Zeilen, Vertiefungs-Block) darf sie nicht reißen.
         Richtwert 900 — ein Paper ist ein Spickzettel, kein Kapitel.
  SP-02  Pflichtstruktur in dieser Reihenfolge: `## Was du jetzt kannst`,
         `## Die Handgriffe`, `## Wenn es klemmt`, `## Vertiefung`.
  SP-03  Jeder Handgriff (nummerierte Zeile unter „Die Handgriffe") trägt
         in seinem Block einen Codezaun, ein Bild (`![`), ein Mermaid oder
         eine Screenshot-Marke (`[Screenshot:`).
  SP-04  Keine Fußnoten im Paper; Belege gehören in den Vertiefungs-Block
         als Handout-/Kapitel-Verweise.
  SP-05  `## Was du jetzt kannst` hat höchstens 3 Sätze.
  SP-06  Jeder Mermaid-Block im Paper stimmt zeichengenau mit einer `.mmd`
         unter `praesentationen/grafiken/` überein (ohne die `%%`-Kopfzeilen).
         Eine Grafik ist EINE Quelle für Deck und Paper — wird die .mmd
         geglättet, darf die Kopie im Paper nicht zurückbleiben.

Exit 0 ohne Befund, 1 mit Befunden. Schreibt gates/papier-report.md.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gemeinsam as g  # noqa: E402

PFLICHT = ["## Was du jetzt kannst", "## Die Handgriffe", "## Wenn es klemmt", "## Vertiefung"]
WORT = re.compile(r"\b[\wäöüÄÖÜß-]+\b")


def fliesstext(text: str) -> str:
    """Ohne Codezäune und ohne Vertiefungs-Block."""
    text = text.split("## Vertiefung")[0]
    out, zaun = [], False
    for z in text.splitlines():
        if z.lstrip().startswith(("```", "~~~")):
            zaun = not zaun
            continue
        if zaun or z.lstrip().startswith("!["):
            continue
        out.append(z)
    return "\n".join(out)


def pruefen(datei: Path) -> list[dict]:
    text = datei.read_text(encoding="utf-8", errors="replace")
    b = []
    def befund(regel, meldung):
        b.append({"regel": regel, "ort": datei.name, "text": meldung})

    m = re.search(r"^Wortbudget:\s*(\d+)", text, re.M)
    if not m:
        befund("SP-01", "Kopfzeile `Wortbudget: <n>` fehlt")
    else:
        woerter = len(WORT.findall(fliesstext(text)))
        if woerter > int(m.group(1)):
            befund("SP-01", f"{woerter} Wörter Fließtext bei Budget {m.group(1)}")

    pos = -1
    for p in PFLICHT:
        np = text.find(p)
        if np < 0:
            befund("SP-02", f"Pflichtabschnitt `{p}` fehlt")
        elif np < pos:
            befund("SP-02", f"`{p}` steht vor dem vorherigen Pflichtabschnitt")
        else:
            pos = np

    hg = re.search(r"## Die Handgriffe(.*?)(?=^## )", text, re.S | re.M)
    if hg:
        bloecke = re.split(r"^(?=\d+[.)]\s)", hg.group(1), flags=re.M)
        nr = 0
        for block in bloecke:
            if not re.match(r"^\d+[.)]\s", block):
                continue
            nr += 1
            if not ("```" in block or "![" in block or "[Screenshot:" in block):
                befund("SP-03", f"Handgriff {nr} ohne Kasten, Bild oder Screenshot-Marke")

    vor_vertiefung = text.split("## Vertiefung")[0]
    if re.search(r"\[\^[A-Za-z0-9][\w-]*\]", vor_vertiefung):
        befund("SP-04", "Fußnote im Paper — Belege gehören in den Vertiefungs-Block")

    kann = re.search(r"## Was du jetzt kannst(.*?)(?=^## )", text, re.S | re.M)
    if kann:
        # Nur Fließtext zählen: Codezäune (auch Mermaid) tragen Punkte wie
        # `-. label .-`, die sonst als Satzgrenze gelesen werden. Gemessen am
        # Fehlalarm bei P-T13 (2026-10-06).
        roh, zaun = [], False
        for z in kann.group(1).splitlines():
            if z.lstrip().startswith(("```", "~~~")):
                zaun = not zaun
                continue
            if not zaun:
                roh.append(z)
        saetze = [s for s in re.split(r"(?<=[.!?])\s+", "\n".join(roh).strip()) if s.strip()]
        if len(saetze) > 3:
            befund("SP-05", f"`Was du jetzt kannst` hat {len(saetze)} Sätze (max 3)")

    # SP-06: Mermaid im Paper gegen die .mmd-Quelle. Der Vergleich ignoriert
    # Listen-Einrückung (im Paper steht der Block in einem Handgriff) und die
    # %%-Kopfzeilen der Quelldatei, sonst nichts.
    w = g.wurzel(datei.resolve().parent)
    gdir = (w / "praesentationen" / "grafiken") if w is not None else None
    if gdir is not None and gdir.is_dir():
        quellen = {}
        for mmd in sorted(gdir.glob("*.mmd")):
            roh = [z for z in mmd.read_text(encoding="utf-8").splitlines()
                   if not z.lstrip().startswith("%%")]
            quellen[mmd.name] = _norm(roh)
        for nr, block in enumerate(re.findall(r"```mermaid\n(.*?)```", text, re.S), 1):
            kopie = _norm(block.splitlines())
            if not kopie:
                continue
            if kopie in quellen.values():
                continue
            # Ähnlichste Quelle benennen, damit der Riss adressierbar ist.
            import difflib
            kt = "\n".join(kopie)
            rang = sorted(
                ((difflib.SequenceMatcher(None, kt, "\n".join(q)).ratio(), n)
                 for n, q in quellen.items()),
                reverse=True,
            )
            hinweis = (f"weicht von `{rang[0][1]}` ab ({rang[0][0]:.0%} gleich)"
                       if rang and rang[0][0] > 0.5 else "zu keiner .mmd zeichengleich")
            befund("SP-06", f"Mermaid-Block {nr} {hinweis} — Grafik ist eine Quelle")
    return b


def _norm(zeilen: list[str]) -> list[str]:
    """Leerzeilen weg, gemeinsame Einrückung weg — der Rest bleibt zeichengenau."""
    z = [x.rstrip() for x in zeilen if x.strip()]
    if not z:
        return []
    tiefe = min(len(x) - len(x.lstrip()) for x in z)
    return [x[tiefe:] for x in z]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dateien", nargs="+")
    ap.add_argument("--ausloeser", default="lauf")
    a = ap.parse_args()
    dateien = [Path(d) for d in a.dateien if Path(d).exists()]
    befunde = [x for d in dateien for x in pruefen(d)]
    w = g.wurzel(dateien[0].resolve().parent if dateien else None)
    if w is not None:
        z = ["<!-- GENERIERT von papier_pruefen.py -->", "# Gate: Papier", "",
             f"Stand {g.heute()} · {len(dateien)} Papers · {len(befunde)} Befunde", ""]
        z += [f"- `{x['ort']}` — {x['regel']} — {x['text']}" for x in befunde] or ["Kein Befund.", ""]
        g.bericht_schreiben(w, "papier-report.md", "\n".join(z))
        nach_regel = {}
        for x in befunde:
            nach_regel[x["regel"]] = nach_regel.get(x["regel"], 0) + 1
        g.spur(w, "gate", werkzeug="papier_pruefen", dateien=[d.name for d in dateien],
               befunde=len(befunde), nach_regel=nach_regel, ausloeser=a.ausloeser)
    print(f"{len(dateien)} Papers, {len(befunde)} Befunde")
    for x in befunde[:20]:
        print(f"  {x['regel']}  {x['ort']}  {x['text'][:90]}")
    raise SystemExit(1 if befunde else 0)


if __name__ == "__main__":
    main()
