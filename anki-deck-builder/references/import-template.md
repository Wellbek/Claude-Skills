# {{SUBJECT}} - Anki Deck Import Guide

This deck covers the essential, must-know basics of {{SUBJECT}}, built from
{{SOURCE_DESCRIPTION}} (e.g. "the N chapters of the course slides,
`Slides/01 ... .pdf` through `Slides/NN ... .pdf`").

It intentionally stays at basics depth ({{TOTAL_CARDS}} cards total) rather
than being exhaustive - it is meant as a refresher/quiz deck, not a full
source-of-truth deck.

## What you get
- `{{OUTPUT_NAME}}.apkg` - one-click Anki package (recommended). Imports all
  {{DECK_COUNT}} sub-decks automatically.
- `{{OUTPUT_NAME}}_all.tsv` - all cards in one tab-separated file (HTML
  fields, tag-driven).
- `{{OUTPUT_NAME}}_<deck>.tsv` - one TSV per chapter sub-deck.
- `{{OUTPUT_NAME}}_merged.json` - the full compiled card set as JSON (for
  auditing / regenerating).

## Deck structure ({{TOTAL_CARDS}} cards across {{DECK_COUNT}} chapters)
- {{SUBJECT}}
{{DECK_LIST}}
<!-- one line per deck, e.g.: "  - 01 <Chapter Name> (N)" -->

## Option A - Import the .apkg (easiest)
1. Open Anki desktop.
2. File > Import > select `{{OUTPUT_NAME}}.apkg`.
3. Done. Sub-decks appear under "{{SUBJECT}}".

## Option B - Import the TSV(s)
The TSV files have Anki import directives built in (`#html:true`,
`#separator:tab`, `#tags column:4`, `#deck:...`).
1. In Anki: File > Import > select `{{OUTPUT_NAME}}_all.tsv` (or each
   per-chapter TSV).
2. Confirm the fields map as Front / Back / Extra / Tags (the directives
   set this automatically). Click Import.

## Card types
- **Q&A** (Front / Back) - the bulk ({{QA_COUNT}} cards). Concise
  question, direct answer + short explanation.
- **MCQ** - multiple choice (4 options, A-D), {{MCQ_COUNT}} cards. Front
  shows the stem + options; Back shows the correct letter, why it's right,
  and briefly why the others are wrong. Tagged `mcq`.

## Tags (use these to build filtered/study decks)
- `topic::<kebab>` - per-card topic tags.
- `high-yield` - the most fundamental/core concepts ({{HIGH_YIELD_COUNT}}
  cards) - study these first if pressed for time.
- `mcq` - the {{MCQ_COUNT}} multiple-choice cards.

Tips:
- Study high-yield first: search `tag:high-yield`.
- Drill multiple choice: `tag:mcq`.
- By chapter: browse the relevant sub-deck.

## MCQ correctness
Every MCQ was built so the front's option list and the back's "Correct: X"
line come from the same `answer` value (see `anki-deck-builder`'s
`card-schema.md` for why this matters), and was checked with
`verify_mcqs.py` before compiling: 4 options, valid answer letter, exactly
one "Correct:" statement in the back, and that statement matching the
`answer` field.

## Scope note
This deck deliberately covers only the essential/basic concepts from each
chapter (definitions, core formulas, key rules of thumb), not every
example, proof, or edge case in the source material.
If deeper coverage of any chapter is wanted, ask for it and more cards can
be generated for that chapter specifically.

## Regenerating
`python3 <anki-deck-builder skill dir>/scripts/compile.py --course-dir
"<this course's folder>"` rebuilds the `.apkg` and TSVs from
`Anki/.ankiskill/out_cards.json` + `Anki/.ankiskill/deck_config.json`.
To edit the card content itself, edit `Anki/.ankiskill/build_cards.py` and
re-run it, then re-run `compile.py`.
