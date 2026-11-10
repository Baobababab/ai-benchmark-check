"""Recommend the cheapest model that is statistically tied with the best one.

    python recommend.py --list [filter]            list benchmarks you can ask about
    python recommend.py <benchmark> [--open]       recommend a model for that benchmark
    python recommend.py <benchmark> --top N        show the N best models of that benchmark
    python recommend.py --model <name>             one model: lab, price, release date, rank in every benchmark

Scores come from data/scores.csv, prices and model facts from data/models.csv (see README).
data/SNAPSHOT.md is a ready-made overview of the same data, written by fetch.py.
"""

import argparse
import csv
import math
import re
import statistics
import sys
from datetime import timedelta
from pathlib import Path

DATA = Path(__file__).parent / "data"
Z = 1.96  # 95% confidence: two scores closer than Z standard errors are "tied"
CEILING = 0.95  # a correctness score above this separates models poorly, so we warn
RISKY = {"Unreleased", "Limited access"}  # availability labels from Epoch worth a warning
KEY_BENCHMARKS = [  # shown in the snapshot, besides the Epoch Capabilities Index
    ("text_style_control/overall", "Writing and chat (human preference)"),
    ("text_style_control/coding", "Coding (human preference)"),
    ("text_style_control/hard_prompts", "Hard prompts (human preference)"),
    ("text_style_control/instruction_following", "Following instructions (human preference)"),
    ("webdev/webdev-react", "Web UI (human preference)"),
    ("vision_style_control/ocr", "Reading images (human preference)"),
    ("search/overall", "Web search answers (human preference)"),
    ("document/overall", "Document questions (human preference)"),
    ("gpqa_diamond", "Science questions (correctness)"),
    ("frontiermath_tiers_1_3_v2", "Maths (correctness)"),
    ("otis_mock_aime_2024_2025", "Competition maths (correctness)"),
    ("simpleqa_verified", "Factual accuracy (correctness)"),
]


def key(name):
    """Normalise a model name so the same model matches across sources.

    'Claude Fable 5.2 (Max)', 'claude-fable-5-2_max' and 'claude-fable-5-2' -> 'claudefable52'.
    """
    n = re.sub(r"\s*\(.*?\)", "", name.lower().split("/")[-1])  # drop '(High)' style tags
    n = re.sub(
        r"_(minimal|none|low|medium|high|xhigh|max|promax|unknown|\d+k)$", "", n.strip()
    )  # drop '_max' effort tags
    n = re.sub(r"-(\d{8}|\d{4}-\d{2}-\d{2})$", "", n)  # drop date stamps
    return re.sub(r"[^a-z0-9]", "", n)


def load():
    with open(DATA / "scores.csv", encoding="utf-8", newline="") as f:
        scores = [
            {**r, "score": float(r["score"]), "se": float(r["se"]) if r["se"] else None} for r in csv.DictReader(f)
        ]
    with open(DATA / "models.csv", encoding="utf-8", newline="") as f:
        models = {r["key"]: r for r in csv.DictReader(f)}
    return scores, models


def blended(m):
    """USD per million tokens, assuming 3 input tokens for every output token."""
    return (3 * float(m["input"]) + float(m["output"])) / 4


def prepare(rows, models, open_only=False):
    """Attach price and facts to each row. Keep one row per model: its best variant (High, Max...)."""
    best = {}
    for r in rows:
        k = key(r["model"])
        m = models.get(k, {})
        r = {
            **r,
            "price": blended(m) if m.get("input") else None,
            "open": m.get("open_weights") == "True",
            "lab": m.get("lab", ""),
            "access": m.get("access", ""),
            "name": m.get("name", ""),
        }
        if k not in best or r["score"] > best[k]["score"]:
            best[k] = r
    return [r for r in best.values() if r["open"] or not open_only]


def pick(rows, models, open_only=False):
    """Return (best, recommended, tied_priced, tied_unpriced) for one benchmark's rows."""
    pool = prepare(rows, models, open_only)
    if not pool:
        return None, None, [], []
    # A score with no uncertainty (0 or missing) would only tie with identical scores: use the typical one.
    typical = statistics.median([r["se"] for r in pool if r["se"]] or [0])
    # Equal scores: the cheapest wins, so "best" does not depend on file order.
    best = max(pool, key=lambda r: (r["score"], -(r["price"] if r["price"] is not None else math.inf)))
    tied = [r for r in pool if best["score"] - r["score"] <= Z * math.hypot(best["se"] or typical, r["se"] or typical)]
    priced = sorted((r for r in tied if r["price"] is not None), key=lambda r: (r["price"], -r["score"]))
    unpriced = [r for r in tied if r["price"] is None]
    return best, (priced[0] if priced else None), priced, unpriced


def score_text(r, source, name):
    if source == "arena":
        text, scale, digits = f"{r['score']:.0f} Elo", 1, 0
    elif name == "eci":
        text, scale, digits = f"{r['score']:.1f} ECI", 1, 1
    else:
        text, scale, digits = f"{100 * r['score']:.1f}%", 100, 1
    return f"{text} +/-{scale * Z * r['se']:.{digits}f}" if r["se"] else text  # no +/- when there is no uncertainty


def label(r):
    """Name to print. Epoch run ids like 'gemini-4-argon_high' become 'Gemini 4 Argon (high)' when the name is known."""
    if r["source"] != "epoch" or not r["name"]:
        return r["model"]
    setting = re.search(r"_(minimal|none|low|medium|high|xhigh|max|promax)$", r["model"])
    return f"{r['name']} ({setting.group(1)})" if setting else r["name"]


def show(r, source, name):
    price = "price unknown" if r["price"] is None else f"${r['price']:.2f}/M tokens"
    tag = f"  [Epoch: {r['access']}]" if r["access"] in RISKY else ""
    return f"{label(r)}  {score_text(r, source, name)}  {price}{tag}"


def show_model(query, scores, models, benchmarks):
    """Print lab, price, release date and the rank in the key benchmarks for the models matching the query."""
    q = key(query)
    found = {}
    for r in sorted(scores, key=lambda r: r["benchmark"] != "eci"):  # ECI names are the cleanest
        if q in key(r["model"]):
            found.setdefault(key(r["model"]), r["model"])
    if q in found:  # an exact name wins over longer names that contain it (o3 and o3-mini)
        found = {q: found[q]}
    if not found or len(found) > 5:
        print("No model matches." if not found else "Too many models match. Candidates:", file=sys.stderr)
        for name in sorted(found.values())[:20]:
            print(f"  {name}", file=sys.stderr)
        return 1
    source = {bench: src for src, bench in benchmarks}
    shown = [b for b in ["eci"] + [b for b, _ in KEY_BENCHMARKS] if b in source]
    for k, name in found.items():
        m = models.get(k, {})
        price = f"${blended(m):.2f}/M tokens" if m.get("input") else "price unknown"
        note = f", Epoch: {m['access']}" if m.get("access") else ""
        print(f"{name}: lab {m.get('lab') or 'unknown'}, released {m.get('released') or 'unknown'}, {price}{note}")
        others = len({r["benchmark"] for r in scores if key(r["model"]) == k and r["benchmark"] not in shown})
        for bench in shown:
            ranking = prepare([r for r in scores if r["benchmark"] == bench], models)
            for r in ranking:
                if key(r["model"]) == k:
                    rank = 1 + sum(x["score"] > r["score"] for x in ranking)  # equal scores share a rank
                    print(
                        f"  {bench}  {score_text(r, source[bench], bench)}  #{rank} of {len(ranking)}  ({r['model']})"
                    )
        if others:
            print(f"  ... and {others} other benchmarks: python recommend.py <benchmark> --top 100")
    return 0


def snapshot(today):
    """Markdown overview of the whole dataset, so a reader (or an AI agent) gets the full picture at once."""
    scores, models = load()
    by, source = {}, {}
    for r in scores:
        by.setdefault(r["benchmark"], []).append(r)
        source[r["benchmark"]] = r["source"]
    newest = {s: max(r["date"] for r in scores if r["source"] == s) for s in ("arena", "epoch")}
    names = {}  # one display name per model: the ECI name if it has one, else the first one in the file
    for r in by["eci"] + scores:
        names.setdefault(key(r["model"]), r["model"])

    def ranked(name):
        return sorted(prepare(by[name], models), key=lambda r: -r["score"])

    def table(name, n):
        rows = ["| # | Model | Score | Lab | Price $/M | Note |", "|---|---|---|---|---|---|"]
        for i, r in enumerate(ranked(name)[:n], 1):
            price = "n/a" if r["price"] is None else f"{r['price']:.2f}"
            note = f"Epoch: {r['access']}" if r["access"] in RISKY else ""
            cells = [i, label(r), score_text(r, source[name], name), r["lab"] or "-", price, note]
            rows.append("| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |")
        return rows

    out = [
        "# Model data snapshot",
        "",
        f"Written by `fetch.py` on {today}. Do not edit by hand. "
        + f"Newest LMArena score: {newest['arena']}. Newest Epoch result: {newest['epoch']}.",
        "",
        "How to read it:",
        "- LMArena scores are human preference (Elo). They do not measure correctness.",
        "- Epoch scores are correctness on benchmarks (%). ECI is Epoch's own index that combines many of them.",
        "- Price = median listed price on models.dev, 3 input tokens per output token, per token only. "
        + "Reasoning modes (High, Max) use more tokens, so real costs can be higher.",
        "- Each model appears once, with its best variant. "
        + "A model released in the last days can be missing from LMArena for a while, "
        + "and the LMArena website marks very new models as 'Preliminary' (few votes), a flag this data lacks.",
        "- Not covered: agentic coding, speed, latency, long-context accuracy, image and video generation prices.",
        "",
        "## Strongest models overall: Epoch Capabilities Index (ECI), top 15",
        "",
        *table("eci", 15),
        "",
    ]

    arena_keys = {key(r["model"]) for r in scores if r["source"] == "arena"}
    eci_keys = {key(r["model"]) for r in by["eci"]}
    # Only models with a proper name (from LMArena or ECI), not raw Epoch run ids.
    recent = [
        (m["released"], k)
        for k, m in models.items()
        if m["released"] >= (today - timedelta(days=60)).isoformat() and (k in arena_keys or k in eci_keys)
    ]
    out += [
        "## Newest models (released in the last 60 days, date from models.dev)",
        "",
        f"{len(recent)} models qualify" + (", the 20 newest are shown." if len(recent) > 20 else "."),
        "",
        "| Released | Model | Lab | Price $/M | On LMArena | In ECI | Note |",
        "|---|---|---|---|---|---|---|",
    ]
    for released, k in sorted(recent, reverse=True)[:20]:
        m = models[k]
        price = f"{blended(m):.2f}" if m["input"] else "n/a"
        note = f"Epoch: {m['access']}" if m["access"] in RISKY else ""
        on_arena, in_eci = ("yes" if k in ks else "no" for ks in (arena_keys, eci_keys))
        out.append(f"| {released} | {names[k]} | {m['lab'] or '-'} | {price} | {on_arena} | {in_eci} | {note} |")

    out += [
        "",
        "## Best model of each lab (by ECI, top 12 labs)",
        "",
        "| Lab | Model | ECI | Price $/M |",
        "|---|---|---|---|",
    ]
    seen = set()
    for r in ranked("eci"):
        if r["lab"] and r["lab"] not in seen and len(seen) < 12:
            seen.add(r["lab"])
            price = "n/a" if r["price"] is None else f"{r['price']:.2f}"
            out.append(f"| {r['lab']} | {label(r)} | {score_text(r, 'epoch', 'eci')} | {price} |")

    out += ["", "## Key benchmarks, top 5 each"]
    for name, title in KEY_BENCHMARKS:
        if name not in by:  # a renamed or dropped benchmark must not break the update
            continue
        out += ["", f"### {title}: `{name}`", ""]
        top = ranked(name)[0]["score"]
        if source[name] == "epoch" and top >= CEILING:
            out += ["Near the ceiling: the top models are hard to tell apart on this benchmark.", ""]
        out += table(name, 5)

    out += ["", "## All benchmarks (ask `python recommend.py <name> --top 20` for any of them)", ""]
    for s in ("arena", "epoch"):
        out.append(f"- **{s}:** " + ", ".join(sorted(b for b in by if source[b] == s)))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("benchmark", nargs="?", help="benchmark name, or a part of it")
    ap.add_argument("--list", nargs="?", const="", metavar="FILTER", help="list benchmarks")
    ap.add_argument("--open", action="store_true", help="only open-weight models")
    ap.add_argument("--top", type=int, metavar="N", help="show the N best models instead of a recommendation")
    ap.add_argument("--model", metavar="NAME", help="show everything known about one model")
    args = ap.parse_args(argv)
    if args.top is not None and args.top < 1:
        ap.error("--top must be 1 or more")
    if (args.list is not None) + bool(args.model) + bool(args.benchmark) > 1:
        ap.error("use only one of: a benchmark name, --model, --list")
    if (args.open or args.top is not None) and not args.benchmark:
        ap.error("--open and --top need a benchmark name")

    scores, models = load()
    benchmarks = {}
    for r in scores:
        b = benchmarks.setdefault((r["source"], r["benchmark"]), {"keys": set(), "date": ""})
        b["keys"].add(key(r["model"]))
        b["date"] = max(b["date"], r["date"])

    if args.list is not None:
        found = [(k, b) for k, b in sorted(benchmarks.items()) if args.list.lower() in k[1].lower()]
        for (src, name), b in found:
            print(f"{name}  [{src}, {len(b['keys'])} models, newest score {b['date']}]")
        if not found:
            print("No benchmark matches.", file=sys.stderr)
        return 0 if found else 1
    if args.model:
        return show_model(args.model, scores, models, benchmarks)
    if not args.benchmark:
        ap.error("give a benchmark name, --model or --list")

    names = [k for k in benchmarks if k[1] == args.benchmark] or [
        k for k in benchmarks if args.benchmark.lower() in k[1].lower()
    ]
    if len(names) != 1:
        print(
            "No single benchmark matches. Candidates:" if names else "Unknown benchmark. Try --list.", file=sys.stderr
        )
        for src, name in names:
            print(f"  {name}", file=sys.stderr)
        return 1
    source, name = names[0]
    rows = [r for r in scores if r["benchmark"] == name]
    fetched = (DATA / "last_update.txt").read_text().strip()
    header = f"Benchmark: {name} ({source}), newest score {benchmarks[(source, name)]['date']}, data fetched {fetched}"

    if args.top:
        print(header)
        for i, r in enumerate(sorted(prepare(rows, models, args.open), key=lambda r: -r["score"])[: args.top], 1):
            print(f"{i:>3}. {show(r, source, name)}  {r['lab'] or '-'}")
        return 0

    best, rec, priced, unpriced = pick(rows, models, args.open)
    if best is None:
        print("No open-weight model in this benchmark.", file=sys.stderr)
        return 1
    print(header)
    print(f"{'Best (open only):' if args.open else 'Best:':<18}{show(best, source, name)}")
    if rec is None:
        print(f"{'Recommended:':<18}none (no priced model is statistically tied with the best)")
    else:
        extra = ""
        if best["price"] and rec is not best and best["price"] / max(rec["price"], 0.01) >= 1.5:
            extra = f"  <- {best['price'] / max(rec['price'], 0.01):.1f}x cheaper than the best"
        print(f"{'Recommended:':<18}{show(rec, source, name)}{extra}")
    same = [r for r in priced + unpriced if r["score"] == best["score"]]
    if len(same) > 1:
        print(f"Note: {len(same)} models share the top score, so 'Best' is the cheapest of them.")
    if source == "epoch" and name != "eci" and best["score"] >= CEILING:
        print("Warning: the top score is 95% or more, near the ceiling. Models are hard to tell apart here.")
    others = [r for r in priced if r is not rec and r is not best]
    if others:
        print("Also tied with the best, cheapest first:")
        for r in others[:7]:
            print(f"  {show(r, source, name)}")
        if len(others) > 7:
            print(f"  ... and {len(others) - 7} more")
    if unpriced:
        more = f" ... and {len(unpriced) - 8} more" if len(unpriced) > 8 else ""
        print("Tied but no price found (not considered): " + ", ".join(label(r) for r in unpriced[:8]) + more)
    print("Tied = scores within 95% confidence of the best. [Epoch: ...] = availability according to Epoch.")
    print("Price = median listed price on models.dev, 3:1 input:output blend. Per token only.")
    print("Reasoning modes (High, Max) use more tokens, so real costs can be higher.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    raise SystemExit(main())
