---
name: evaluieren
description: "Bewertet die Folien-Pipeline selbst statt der Decks: Writer-Erstwurf-Qualität, Prüfer-Ertrag und -Rauschen, Hook-Blockaden, Kosten je Rolle — und leitet daraus Finetuning an Prompts, Spezifikations-Vorlage und Memories ab. Triggers on: /folien-kit:evaluieren [durchlauf-beschreibung]"
disable-model-invocation: true
argument-hint: "[was gerade gelaufen ist]"
---

Du prüfst das Werkzeug, nicht das Deck. Diese Skill ändert die Pipeline im
Plugin-Repo folien-agent-kit — sag immer, in welchem Repo du schreibst.

## Vorgehen

1. Spawn `lauf-auswerter`. Er liest Protokoll, Gate-Berichte, Decks und
   Git-Historie und liefert Befunde mit Zahlen.
2. Frag den Nutzer im Chat, wo er eingegriffen hat und was ihn an den Decks
   gestört hat — das wertvollste Signal steht in keinem Protokoll.
3. Entscheide, welche Befunde zu Änderungen führen (P-02-Prinzip: der Agent
   urteilt, du entscheidest).
4. Führ die Änderungen aus und benenne je Änderung die Zahl, die sie
   begründet.

Fehlt das Protokoll oder ist es fast leer: nicht aus dem Gedächtnis bewerten.
Dann ist die richtige Änderung ein zusätzlicher Protokolleintrag in der
deck-Skill, und die Bewertung läuft nach dem nächsten Durchlauf.

## Was du änderst, und was nicht

Ändern: Agenten-Prompts, die Spezifikations-Vorlage in der deck-Skill,
Richtwerte im REGELWERK-Kommentar, Reihenfolge der Skill-Schritte, Memories.
Nicht ohne Rückfrage: die F-Grenzen selbst (25 Wörter, Budgets) und die
FP-Rollenregeln — das sind Grundentscheidungen. Niemals: eine Grenze lockern,
weil viele Befunde kommen; viele richtige Befunde sind ein Deck-Problem.

## Memory pflegen

- `folien-writer`: wiederkehrende Gate-Befunde des ERSTEN Wurfs, die er
  selbst vermeiden kann; Streichungen, die die Skill zurücknahm.
- `trainer-leser`: Stellen, an denen seine Uhr systematisch von der
  Realität abwich (nur wenn eine zweite Quelle das belegt).
- `publikum-entwickler`: nichts. Bleibt leer (FP-03) — Messinstrument.
- `belegkette-pruefer`: Ketten-Muster, die mehrfach rissen.
Nur Protokoll-Belegtes eintragen; Vermutung verschlechtert dauerhaft.

## Ergebnis

```
DATENLAGE / BEFUNDE DES AGENTEN / NUTZEREINGRIFFE (erfragt)
ÄNDERUNGEN AUSGEFÜHRT (repo/datei — änderung — begründende Zahl)
MEMORY GEPFLEGT / NICHT GEÄNDERT, OBWOHL AUFFÄLLIG / RÜCKFRAGEN
PROTOKOLLLÜCKEN
```
