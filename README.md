# folien-agent-kit

Agenten-Pipeline für Dünn-Decks: Leinwand-Foliensätze mit harten Budgets,
gebaut aus belegten Handout-Modulen eines Dokumentprojekts (siehe
recherche-agent-kit). Die Leinwand trägt einen Gedanken je Folie und keinen
Beleg-Apparat; die Belegkette läuft Leinwand → Handout → Claim.

- `tools/folien_pruefen.py` — maschinelles Gate F-01…F-06 (+ Selbsttest)
- `hooks/` — guard-leinwand (blockiert Fußnoten auf Folien, PreToolUse),
  guard-folien (misst nach jedem Schreiben, PostToolUse)
- `agents/` — folien-writer · belegkette-pruefer · trainer-leser ·
  publikum-entwickler
- `skills/deck` — Orchestrierung: Spezifikation → Bau → Gate → drei Prüfer →
  Fix-Entscheidung
- `docs/REGELWERK.md` — F-/D-/FP-Regeln und Deck-Format

Logs: `.claude/folien-log/lauf.jsonl` im Dokumentprojekt. Memories:
`.claude/agent-memory/folien-kit-<agent>/`; das Publikum bleibt memoryfrei.
