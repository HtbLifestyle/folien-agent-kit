"""Gemeinsame Helfer für die folien-kit Werkzeuge. Nur Standardbibliothek."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

SPUR = Path(".claude") / "folien-log" / "lauf.jsonl"


def heute() -> str:
    return date.today().isoformat()


def wurzel(start: Path | None = None) -> Path | None:
    """Wurzel des Dokumentprojekts: der Ordner, der `praesentationen/` enthält.
    Liefert None statt Abbruch — das Gate läuft auch auf losen Dateien."""
    p = (start or Path.cwd()).resolve()
    for k in (p, *p.parents):
        if (k / "praesentationen").is_dir():
            return k
    return None


def spur(w: Path | None, ereignis: str, **felder):
    """Laufprotokoll — Datengrundlage fürs Evaluieren. Stört nie den Aufrufer."""
    if w is None:
        return
    from datetime import datetime
    try:
        pfad = w / SPUR
        pfad.parent.mkdir(parents=True, exist_ok=True)
        with pfad.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"zeit": datetime.now().isoformat(timespec="seconds"),
                                "ereignis": ereignis, **felder}, ensure_ascii=False) + "\n")
    except Exception:
        pass


def bericht_schreiben(w: Path, name: str, inhalt: str) -> Path:
    pfad = w / "gates" / name
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad
