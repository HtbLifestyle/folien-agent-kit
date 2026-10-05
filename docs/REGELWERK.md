# Regelwerk folien-kit

Gilt für alle Decks unter `praesentationen/decks/` eines Dokumentprojekts.
Die F-Regeln prüft `tools/folien_pruefen.py` maschinell; F-04 blockiert
zusätzlich der PreToolUse-Hook `guard-leinwand` beim Schreiben.

## Leinwand-Regeln (maschinell, F)

- **F-01** Folienbudget: Kopfzeile `Budget: <n> Folien`; mehr Folien als n
  sind ein Befund. Richtwerte: Briefing ≤ 12, Workshop-Input ≤ 8,
  Session-Rahmen ≤ 6, Abschluss ≤ 10 — das konkrete n setzt die Spezifikation.
- **F-02** ≤ 25 sichtbare Wörter je Folie. Nicht sichtbar (zählt nicht):
  Sprechnotiz:, Demo:, Jetzt du:, Handout:, Form:, Skizze:, Codezäune,
  Folientitel.
- **F-03** Ein Gedanke je Folie: höchstens ein zusammenhängender Bullet-Block.
- **F-04** Keine Fußnoten auf der Leinwand. Belege laufen über die
  Handout:-Zeile (Modul + Folie/Abschnitt); der Hook blockiert Verstöße.
- **F-05** Beispiel vor Regel: eine Regel:-Zeile verlangt eine
  Beispiel:-Zeile davor auf derselben Folie.
- **F-06** Leinwandzeit: Kopfzeile `Leinwandzeit: <n> min`; die Summe der
  `(~n min)`-Angaben darf sie nicht reißen. Richtwert: ≤ 25–30 min je
  90-Minuten-Session — der Rest ist Arbeit der Teilnehmer.

## Darstellungs-Regeln (geprüft von Agenten, D)

- **D-01** Jede Folie trägt `**Form:** <Typ>` aus dem Vokabular (Kernsatz ·
  Schaubild · Vergleich · Beleg-Folie · Zahl · Live-Demo · Jetzt du · Kasten ·
  Quellen); Schaubilder zusätzlich `**Skizze:** <ein Satz>`.
- **D-02** Jede Zahl auf der Leinwand trägt ihre Herkunft als Unterzeile:
  gemessen (wo) oder Programmziel. Zahlen ohne Herkunft sind verboten.
- **D-03** Jede Jetzt-du-Folie nennt Auftrag, Minuten und Fertig-Kriterium.
- **D-04** Spätestens jede dritte Folie ist aktiv (Demo oder Jetzt du);
  bewusste Ausnahmen stehen als ⚠-Zeile im Dramaturgie-Block.

## Rollen-Regeln (FP)

- **FP-01** Die Skill entscheidet, Agenten liefern. Spezifikation, Gate-Läufe
  und Fix-Entscheidungen sind Skill-Arbeit; kein Agent verwaltet Gate-Dateien.
- **FP-02** Ersteller prüfen nicht: der folien-writer sieht keinen
  Prüfbericht vor Abgabe, die Prüfer (belegkette-pruefer, trainer-leser,
  publikum-entwickler) haben keine Schreibrechte.
- **FP-03** Das Publikum ist Messinstrument und bleibt memoryfrei; ein
  Publikum, das sich erinnert, misst nicht mehr. Writer und trainer-leser
  dürfen Handwerk im Memory halten (nur aus dem Protokoll Belegtes).
- **FP-04** Die Belegkette läuft Leinwand → Handout → Claim. Das Handout
  (die Module unter praesentationen/module/) ist die einzige Inhaltsquelle
  des Writers; neue Inhalte entstehen nie im Deck.
- **FP-05** Jede Blockade und jeder Gate-Lauf landet im Laufprotokoll
  `.claude/folien-log/lauf.jsonl` — sonst ist Evaluieren blind.

## Deck-Format

```
# <Deck-Name> — <Session, Board-Titel>
Budget: <n> Folien
Leinwandzeit: <n> min
Handout: praesentationen/module/<modul>.md

## Dramaturgie
<4–6 Zeilen: Hook, Problem-vor-Lösung, Aktiv-Rhythmus, Peak, Abschluss-Check>

## Folie 1: <Titel> (~n min)
**Form:** <Typ>
Beispiel: <der konkrete Fall zuerst>
Regel: <eine Zeile>
Sprechnotiz: <Trainer-Stimme, zählt nicht>
Handout: <Modul, Folie/Abschnitt>
```
