#!/usr/bin/env python3
"""PreToolUse: harte Grenze der Leinwand — kein Beleg-Apparat auf Folien.

Blockiert (Exit 2) Schreibzugriffe auf praesentationen/decks/*.md, wenn der
neue Text Fußnoten-Syntax enthält (F-04). Belege gehören ins Handout; die
Leinwand trägt höchstens eine Handout:-Zeile. Bei allem Unerwarteten wird
durchgelassen — ein kaputter Hook, der blockt, wird abgeschaltet und schützt
dann nichts mehr.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def spur(w: Path, **felder):
    try:
        pfad = w / ".claude" / "folien-log" / "lauf.jsonl"
        pfad.parent.mkdir(parents=True, exist_ok=True)
        with pfad.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"zeit": datetime.now().isoformat(timespec="seconds"),
                                **felder}, ensure_ascii=False) + "\n")
    except Exception:
        pass


def neuer_text(eingabe: dict) -> str:
    for feld in ("content", "new_string"):
        if isinstance(eingabe.get(feld), str):
            return eingabe[feld]
    if isinstance(eingabe.get("edits"), list):
        return "\n".join(b.get("new_string", "") for b in eingabe["edits"] if isinstance(b, dict))
    return ""


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if daten.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        sys.exit(0)
    pfad_roh = (daten.get("tool_input") or {}).get("file_path") or ""
    teile = Path(pfad_roh).as_posix()
    if "/praesentationen/decks/" not in teile and not teile.startswith("praesentationen/decks/"):
        sys.exit(0)
    text = neuer_text(daten.get("tool_input") or {})
    treffer = re.findall(r"\[\^[A-Za-z0-9][\w-]*\]", text)
    if treffer:
        w = None
        p = Path(daten.get("cwd") or ".").resolve()
        for k in (p, *p.parents):
            if (k / "praesentationen").is_dir():
                w = k
                break
        if w:
            spur(w, ereignis="blockade", hook="guard-leinwand",
                 datei=Path(pfad_roh).name, anzahl=len(treffer),
                 regeln=["F-04"], beispiel=treffer[0])
        print(
            "Blockiert nach F-04 — die Leinwand trägt keine Fußnoten "
            f"({len(treffer)} gefunden, z. B. {treffer[0]}). Belege gehören ins "
            "Handout-Modul; auf der Folie steht höchstens eine Handout:-Zeile.",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
