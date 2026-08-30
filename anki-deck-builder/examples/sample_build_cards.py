#!/usr/bin/env python3
"""Worked example of the anki-deck-builder card-authoring pattern.

Not tied to any real subject - just shows how a real Anki/.ankiskill/
build_cards.py would call qa()/mcq() and dump the result. Run it and
point scripts/compile.py --course-dir at a folder containing an
Anki/.ankiskill/ with this output + a matching deck_config.json to see
the whole pipeline work end to end.
"""
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


D1 = "01 Basics"
D2 = "02 Applications"

qa(D1, "What is a <b>flashcard</b>?",
   "A small card testing a single fact, with a question on one side and the answer on the other.<br>"
   "Spaced-repetition apps like Anki schedule reviews based on how easily you recall each card.",
   "flashcards", tags=["high-yield"])

qa(D1, "What does <b>spaced repetition</b> do?",
   "It schedules a card's next review further out each time you recall it easily, and sooner if you struggle - "
   "concentrating review time on the cards you're most likely to forget.",
   "spaced-repetition")

mcq(D2, "Which of these is the best use case for a flashcard deck?",
    ["A single fact you'll never need again", "A large body of interrelated facts you need to recall quickly and repeatedly",
     "A step-by-step procedure best followed from a checklist", "A one-time calculation"],
    "B",
    "Flashcards suit discrete, recallable facts reviewed over time - not one-off lookups or procedures better served by a checklist.<br>"
    "A/D are one-time needs with no reason to memorize. C is procedural, not a recall task.",
    "use-cases", tags=["high-yield"])

qa(D2, "Why keep MCQ options to exactly 4 (A-D)?",
   "It's a simple, consistent convention that keeps cards quick to read and matches common exam formats - "
   "not a hard technical limit, just the convention this pipeline standardizes on.",
   "mcq-format")

qa(D2, "Why use <code>topic::&lt;kebab-case&gt;</code> tags instead of free-text tags?",
   "Consistent kebab-case topic tags make Anki's tag browser and search (<code>tag:topic::flashcards</code>) reliable - "
   "free-text tags fragment into near-duplicates over time.",
   "tagging")

with open("Anki/.ankiskill/out_cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, indent=1, ensure_ascii=False)

print(f"wrote {len(cards)} cards")
