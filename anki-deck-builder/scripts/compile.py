#!/usr/bin/env python3
"""Generic compiler for anki-deck-builder decks.

Reads <course-dir>/Anki/.ankiskill/out_cards.json and
<course-dir>/Anki/.ankiskill/deck_config.json, and writes the real
deliverables (.apkg, TSVs, merged JSON) into <course-dir>/Anki/.

deck_config.json schema:
{
  "top_deck": "Course Display Name",
  "output_name": "Course_Slug",
  "deck_order": ["01 Chapter One", "02 Chapter Two", ...]
}

Usage:
  python3 compile.py --course-dir "/path/to/Course"
"""
import argparse
import hashlib
import json
import os
import re


def load_config(ankiskill_dir):
    with open(os.path.join(ankiskill_dir, "deck_config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    for key in ("top_deck", "output_name", "deck_order"):
        if key not in cfg:
            raise ValueError(f"deck_config.json missing required key: {key}")
    return cfg


def load_cards(ankiskill_dir):
    with open(os.path.join(ankiskill_dir, "out_cards.json"), encoding="utf-8") as f:
        return json.load(f)


def stable_id(salt, name, low, high):
    """Deterministic id derived from (salt, name), stable across re-runs of
    the same subject and collision-safe across different subjects."""
    h = hashlib.md5(f"{salt}::{name}".encode("utf-8")).hexdigest()
    return low + (int(h[:12], 16) % (high - low))


def normalize(c, deck_order):
    c.setdefault("type", "qa")
    c.setdefault("deck", deck_order[0])
    c.setdefault("front", "")
    c.setdefault("back", "")
    c.setdefault("tags", [])
    if not isinstance(c["tags"], list):
        c["tags"] = [t for t in re.split(r"[,\s]+", str(c["tags"])) if t]
    if c["type"] == "mcq" and c.get("options"):
        c["tags"] = list(dict.fromkeys(c["tags"] + ["mcq"]))
    extra_parts = []
    if c["type"] == "mcq" and c.get("answer") and c.get("options"):
        extra_parts.append("Answer: " + c["answer"])
    c["extra"] = " · ".join(extra_parts)
    return c


CARD_CSS = """
.card{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:17px;line-height:1.5;color:#1a1a1a;background:#fafafa;}
.q{margin-bottom:6px;}
.a{margin-top:6px;}
.extra{margin-top:14px;font-size:13px;color:#888;border-top:1px solid #eee;padding-top:6px;}
img{max-width:100%;height:auto;border:1px solid #ddd;border-radius:6px;}
code,pre{background:#f0f0f0;border-radius:4px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
pre{padding:8px;overflow-x:auto;font-size:14px;}
code{padding:1px 4px;}
table{border-collapse:collapse;margin:6px 0;}
th,td{border:1px solid #ccc;padding:4px 8px;text-align:left;}
th{background:#eee;}
ol{margin:6px 0;}
b{color:#0b3d91;}
"""


def build_apkg(cards, cfg, out_dir):
    import genanki

    model_id = stable_id("anki-deck-builder-model", cfg["top_deck"], 1 << 30, (1 << 31) - 1)
    MODEL = genanki.Model(
        model_id,
        f"{cfg['top_deck']} Card",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}],
        templates=[{
            "name": "Card 1",
            "qfmt": '<div class="q">{{Front}}</div>',
            "afmt": '<div class="q">{{Front}}</div><hr id=answer><div class="a">{{Back}}</div>{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}',
        }],
        css=CARD_CSS,
    )

    decks = {}
    deck_objs = []
    for name in cfg["deck_order"]:
        did = stable_id("anki-deck-builder-deck", f"{cfg['top_deck']}::{name}", 1 << 30, (1 << 31) - 1)
        d = genanki.Deck(did, f"{cfg['top_deck']}::{name}")
        decks[name] = d
        deck_objs.append(d)

    pkg = genanki.Package(deck_objs)
    n_added = 0
    for c in cards:
        deck_name = c["deck"] if c["deck"] in decks else cfg["deck_order"][0]
        guid_field = c.get("front", "") + c.get("back", "")
        h = hashlib.md5(guid_field.encode("utf-8")).hexdigest()[:8]
        guid = int(h, 16)
        note = genanki.Note(
            model=MODEL,
            fields=[c["front"], c["back"], c.get("extra", "")],
            tags=list(dict.fromkeys(c["tags"])),
            guid=guid,
        )
        decks[deck_name].add_note(note)
        n_added += 1

    out_path = os.path.join(out_dir, f"{cfg['output_name']}.apkg")
    pkg.write_to_file(out_path)
    return out_path, n_added


def tsv_escape(s):
    return s.replace("\t", " ").replace("\n", "<br>")


def write_tsv(cards, path, top_deck, deck=None):
    lines = ["#separator:tab", "#html:true", f"#deck:{deck or top_deck}", "#tags column:4",
             "Front\tBack\tExtra\tTags"]
    for c in cards:
        tags = " ".join(c["tags"])
        lines.append("\t".join([tsv_escape(c["front"]), tsv_escape(c["back"]), tsv_escape(c.get("extra", "")), tags]))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(cards)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--course-dir", required=True, help="Path to the course folder (contains Anki/.ankiskill/)")
    args = ap.parse_args()

    ankiskill_dir = os.path.join(args.course_dir, "Anki", ".ankiskill")
    out_dir = os.path.join(args.course_dir, "Anki")

    cfg = load_config(ankiskill_dir)
    raw_cards = load_cards(ankiskill_dir)
    cards = [normalize(c, cfg["deck_order"]) for c in raw_cards]
    print(f"loaded {len(cards)} cards for '{cfg['top_deck']}'")

    from collections import Counter
    by_deck = Counter(c["deck"] for c in cards)
    by_type = Counter(c["type"] for c in cards)
    hy = sum(1 for c in cards if "high-yield" in c["tags"])
    print("\nBy deck:")
    for d in cfg["deck_order"]:
        print(f"  {by_deck.get(d, 0):3d}  {d}")
    print("By type:", dict(by_type))
    print(f"high-yield: {hy}")

    apkg_path, n = build_apkg(cards, cfg, out_dir)
    print(f"\nWROTE apkg: {apkg_path} ({n} notes)")

    cnt = write_tsv(cards, os.path.join(out_dir, f"{cfg['output_name']}_all.tsv"), cfg["top_deck"])
    print(f"WROTE combined TSV: {cfg['output_name']}_all.tsv ({cnt} rows)")

    for d in cfg["deck_order"]:
        sub = [c for c in cards if c["deck"] == d]
        if sub:
            slug = re.sub(r"[^a-z0-9]+", "-", d.lower()).strip("-")
            write_tsv(sub, os.path.join(out_dir, f"{cfg['output_name']}_{slug}.tsv"), cfg["top_deck"], deck=f"{cfg['top_deck']}::{d}")
    print("WROTE per-deck TSVs")

    with open(os.path.join(out_dir, f"{cfg['output_name']}_merged.json"), "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=1, ensure_ascii=False)
    print(f"\nDONE. {len(cards)} cards across {len(cfg['deck_order'])} decks.")


if __name__ == "__main__":
    main()
