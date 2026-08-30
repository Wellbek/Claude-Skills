# Card schema and authoring rules

## The `qa()` / `mcq()` helper block

Start every `.ankiskill/build_cards.py` with this exact block, unmodified.
It is the load-bearing piece of this skill: the `mcq()` helper builds the
front's option list *and* the back's `"Correct: X"` line from the same
`answer` variable, so they cannot disagree.

```python
import json

cards = []

def qa(deck, front, back, topic, tags=None):
    t = ["topic::" + topic]
    if tags:
        t += tags
    cards.append({"type": "qa", "deck": deck, "front": front, "back": back, "tags": t})

def mcq(deck, front_stem, options, answer, back, topic, tags=None):
    lis = "".join(f"<li>{o}</li>" for o in options)
    front = f'{front_stem}<br><br><ol type="A">{lis}</ol>'
    t = ["topic::" + topic, "mcq"]
    if tags:
        t += tags
    cards.append({"type": "mcq", "deck": deck, "front": front,
                  "back": f"<b>Correct: {answer}</b><br>{back}",
                  "options": options, "answer": answer, "tags": t})
```

End the file with:

```python
with open("Anki/.ankiskill/out_cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, indent=1, ensure_ascii=False)
```

## Why the anti-drift construction matters

An earlier hand-generated deck had ~33 MCQ cards where the `answer` field
and the explanation prose in `back` were written independently by an LLM
generation pass and quietly disagreed on the correct letter. The compile
step then prepended `"Correct: {answer}"` (the wrong letter) directly above
an explanation that itself said `"Correct: {other letter} - ..."`,
producing two contradictory statements on the same card back. The user
caught this by manually studying the deck and fixing each card by hand in
Anki. Building the "Correct: X" line from the exact same variable used for
`options`/`answer` makes that class of bug structurally impossible, not
just something to remember to double-check. Always use `verify_mcqs.py`
after compiling anyway, as a second, independent check.

## Card content rules

- **Depth**: basics only per chapter/section — definitions, core formulas,
  key rules of thumb. Not every example, proof, or edge case in the source,
  unless the user specifically asks for exhaustive coverage.
- **No default card-count cap.** Never silently pick a total and start
  authoring. After reading the source material (Step 3 in `SKILL.md`),
  propose a concrete plan — total card count, roughly how many MCQ vs.
  QA, and a rough per-chapter breakdown — and get the user's confirmation
  before writing a single card. See `SKILL.md`'s "Propose and confirm
  scope" step.
- **Card type mix**: QA is the bulk. MCQs are a minority, roughly 1 in 10
  cards, reserved for genuinely test-like distinctions (e.g. "which of
  these four is NOT X", "what does a large F-value suggest").
- **Deck naming**: one deck per source chapter/section, named to match the
  source's own numbering, e.g. `"01 Descriptive Statistics"`,
  `"02 Producing Data and Sampling"`. This becomes `deck_order` in
  `deck_config.json` and each sub-deck nests under `top_deck::<name>` in
  the compiled `.apkg`.
- **Tags**: every card gets `topic::<kebab-case-topic>` (added
  automatically by the helpers). Add `"high-yield"` via the `tags=` kwarg
  for the most fundamental/core concepts in that chapter — aim for roughly
  a quarter to a third of cards. `mcq` is added automatically for MCQ
  cards.

## HTML field rules

Front/Back are rendered as HTML by Anki.

- Use `<b>`, `<i>`, `<code>`, `<pre><code>...</code></pre>` for
  code/formulas, `<ul><li>`/`<ol><li>`, `<table><tr><th>/<td>`, `<br>`.
- Escape `&`, `<`, `>` inside literal code text; don't escape HTML tags
  you intend Anki to render.
- QA back: direct answer first, then a short explanation — not a restated
  question, not a wall of prose.
- For comparisons, prefer a small `<table>` over a bullet list.
- MCQ front: the question stem, then the `<ol type="A">` list (built by
  the helper — never hand-write it).
- MCQ back: `"<b>Correct: X</b> - <explanation>"` (built by the helper),
  optionally followed by one short line on why the nearest wrong option is
  wrong.

## Card JSON shape (what `qa()`/`mcq()` produce)

```json
{
  "type": "qa" | "mcq",
  "deck": "01 <Chapter Name>",
  "front": "<HTML>",
  "back": "<HTML>",
  "tags": ["topic::<kebab>", "high-yield"?, "mcq"?],
  "options": ["A text", "B text", "C text", "D text"],
  "answer": "B"
}
```

`options`/`answer` are only present on `mcq` cards.
