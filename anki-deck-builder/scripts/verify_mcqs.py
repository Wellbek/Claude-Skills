#!/usr/bin/env python3
"""Structurally verify every MCQ card in an anki-deck-builder cards JSON.

Catches the class of bug found in an earlier hand-generated deck: the
`answer` field (used to build the "Correct: X" line) silently disagreeing
with the letter actually justified in the back's explanation text, which
produced two contradictory "Correct:" statements on the card back.

Checks, per MCQ card:
  - exactly 4 options
  - answer letter is one of A-D
  - front contains exactly one <ol> and its <li> count matches len(options)
  - back contains exactly one "Correct: X" statement, and X == answer

Usage:
  python3 verify_mcqs.py /path/to/out_cards.json
"""
import json
import re
import sys


def verify(cards):
    mcqs = [c for c in cards if c.get("type") == "mcq"]
    issues = []
    for i, c in enumerate(mcqs):
        deck = c.get("deck", "?")
        front = c.get("front", "")
        back = c.get("back", "")
        options = c.get("options")
        answer = c.get("answer", "")

        if not options or len(options) != 4:
            issues.append((deck, i, "options count != 4", options))
            continue
        if answer not in "ABCD":
            issues.append((deck, i, "answer not in A-D", answer))
            continue
        if front.count("<ol") != 1:
            issues.append((deck, i, "front <ol> count != 1", front.count("<ol")))
        if front.count("<li>") != len(options):
            issues.append((deck, i, "front <li> count != options count", front.count("<li>"), len(options)))

        corrects = re.findall(r"Correct:\s*([A-D])", back)
        if len(corrects) != 1:
            issues.append((deck, i, "back 'Correct:' statement count != 1", corrects))
        elif corrects[0] != answer:
            issues.append((deck, i, "answer/back mismatch", f"answer={answer}", f"back_says={corrects[0]}"))

    return mcqs, issues


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    with open(sys.argv[1], encoding="utf-8") as f:
        cards = json.load(f)

    mcqs, issues = verify(cards)
    print(f"total cards: {len(cards)}")
    print(f"total mcqs: {len(mcqs)}")

    if issues:
        print(f"\nFAIL: {len(issues)} structural issue(s) found:")
        for issue in issues:
            print(" ", issue)
        sys.exit(1)

    print("PASS: all MCQs structurally sound (options/answer/back all consistent).")
    for c in mcqs:
        idx = "ABCD".index(c["answer"])
        print(f"  [{c.get('deck','?')}] answer {c['answer']} -> {c['options'][idx]}")


if __name__ == "__main__":
    main()
