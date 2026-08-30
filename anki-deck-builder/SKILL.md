---
name: anki-deck-builder
description: Build an Anki flashcard deck (.apkg + TSVs) from a folder of course/exam source material (PDFs, slides, docs). Use when the user asks to "make anki cards", "create a flashcard deck", "turn these slides/pdfs into anki cards", "build an anki deck for [subject]", or generate a deck in the same cards/build_cards.py + compile.py style as an existing one in this workspace. Produces genanki-based .apkg + TSVs with MCQs whose answer key is structurally verified to never drift from the explanation text.
version: 1.0.0
---

# Anki Deck Builder

Turn a folder of course/exam source material into an importable Anki deck
(`.apkg` + TSVs), using a fixed card schema and a compiler that both live
in this skill, not copy-pasted per course.

Working artifacts (the authored `build_cards.py`, the raw cards JSON, the
deck config) live in a hidden `Anki/.ankiskill/` folder inside the course
directory. Only the finished deliverables — `.apkg`, TSVs, merged JSON,
`IMPORT.md` — sit directly in `Anki/`.

## Workflow

### 1. Scope
Identify the source folder (ask if unclear), the subject/course name, and
where the output should live (`<course>/Anki/`, created if it doesn't
exist).

### 2. Extract
Extract text from every source file before authoring any cards — reading
raw PDFs page-by-page burns far more context for no accuracy gain.
- PDFs: `pdftotext -layout "<file>.pdf" "<scratch-dir>/<file>.txt"`
- pptx/docx: read directly, or convert to text first if large.
Read every extracted file in full before moving on.

### 3. Propose and confirm scope — do not skip this
There is **no default card-count cap**. After reading the material, tell
the user your plan before writing a single card:

> Based on the resources provided, I'm thinking of creating **N cards**
> (~M MCQ, ~Q general Q&A) across K chapters: [chapter] (n1), [chapter]
> (n2), ... — covering [depth level, e.g. "definitions/core formulas
> only" vs. "exhaustive including examples"]. Does that align with what
> you want, or should I go deeper/lighter on any part?

Wait for confirmation (or a correction) before Step 4. If the user gives
a specific number or ratio up front, skip straight to confirming it back
to them in one line instead of re-deriving a full plan.

### 4. Author cards
Create `<course>/Anki/.ankiskill/build_cards.py`. Start it with the exact
`qa()`/`mcq()` helper block from `references/card-schema.md` — copy it
verbatim, don't rewrite it. Then call `qa()`/`mcq()` once per card and end
the file writing `cards` to `Anki/.ankiskill/out_cards.json`.
Read `references/card-schema.md` in full for the content rules (depth,
card-type mix, deck naming, tag conventions) and HTML field rules before
writing cards — do not guess the schema.
Run the script (`python3 Anki/.ankiskill/build_cards.py` from the course
dir) to produce the JSON.

### 5. Configure
Write `<course>/Anki/.ankiskill/deck_config.json`:
```json
{
  "top_deck": "<Course Display Name>",
  "output_name": "<Course_Slug>",
  "deck_order": ["01 <Chapter Name>", "02 <Chapter Name>", "..."]
}
```
`deck_order` must list every deck name used in `build_cards.py`, in the
order they should appear in Anki.

### 6. Compile
Ensure `genanki` is installed (`pip install genanki` if
`python3 -c "import genanki"` fails), then run:
```
python3 <this-skill-dir>/scripts/compile.py --course-dir "<course-dir>"
```
This reads `Anki/.ankiskill/{out_cards.json,deck_config.json}` and writes
`Anki/{<output_name>.apkg, <output_name>_all.tsv,
<output_name>_<deck-slug>.tsv (one per deck), <output_name>_merged.json}`.

### 7. Verify
```
python3 <this-skill-dir>/scripts/verify_mcqs.py "<course-dir>/Anki/.ankiskill/out_cards.json"
```
Must print `PASS` with zero structural issues before continuing — see
"Why the anti-drift construction matters" in `references/card-schema.md`
for what this is guarding against. If it fails, fix the offending
card(s) in `build_cards.py` and re-run Steps 4/6/7.
Also confirm the compiled `.apkg`'s note count matches `out_cards.json`'s
card count (open it as a zip, extract `collection.anki2`, `select
count(*) from notes`) as a final sanity check.

### 8. Document
Write `<course>/Anki/IMPORT.md` from `references/import-template.md`,
filling in every `{{PLACEHOLDER}}` with the actual subject name, counts,
and deck list.

### 9. Report
Report the final per-chapter breakdown and high-yield/MCQ counts to the
user, and offer to expand any chapter that came out thin. Do **not**
`git add`/commit/push anything in the course repo unless the user
separately asks — creating the files is the deliverable, not shipping
them.

## Reference files
- `references/card-schema.md` — the `qa()`/`mcq()` block to copy, content
  rules, HTML rules, tag conventions, and why the anti-drift construction
  matters. Read before Step 4.
- `references/import-template.md` — the `IMPORT.md` skeleton. Read before
  Step 8.
- `examples/sample_build_cards.py` — a small worked example of the full
  authoring pattern on a non-subject-specific toy topic.
- `scripts/compile.py` — the generic compiler (Step 6). Do not copy or
  modify it per course; invoke it in place from this skill directory.
- `scripts/verify_mcqs.py` — the generic MCQ checker (Step 7). Same:
  invoke in place, don't copy.
