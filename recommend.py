"""Recommend the cheapest model that is statistically tied with the best one.

    python recommend.py --list [filter]            list benchmarks you can ask about
    python recommend.py <benchmark> [--open]       recommend a model for that benchmark

Scores come from data/scores.csv, prices from data/prices.csv (see README).
"""

import argparse
import csv
import math
import re
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"
Z = 1.96  # 95% confidence: two scores closer than Z standard errors are "tied"


def key(name):
    """Normalise a model name so the same model matches across sources.

    'Claude Fable 5.2 (Max)', 'claude-fable-5-2_max' and 'claude-fable-5-2' -> 'claudefable52'.
    """
    n = re.sub(r"\s*\(.*?\)", "", name.lower().split("/")[-1])  # drop '(High)' style tags
    n = re.sub(r"_(minimal|low|medium|high|xhigh|max)$", "", n.strip())  # drop '_max' effort tags
    n = re.sub(r"-(\d{8}|\d{4}-\d{2}-\d{2})$", "", n)  # drop date stamps
    return re.sub(r"[^a-z0-9]", "", n)


def load():
    with open(DATA / "scores.csv", encoding="utf-8", newline="") as f:
        scores = [
            {**r, "score": float(r["score"]), "se": float(r["se"]) if r["se"] else None} for r in csv.DictReader(f)
        ]
    with open(DATA / "prices.csv", encoding="utf-8", newline="") as f:
        prices = {r["key"]: r for r in csv.DictReader(f)}
    return scores, prices


def blended(price):
    """USD per million tokens, assuming 3 input tokens for every output token."""
    return (3 * float(price["input"]) + float(price["output"])) / 4


def pick(rows, prices, open_only=False):
    """Return (best, recommended, tied_priced, tied_unpriced) for one benchmark's rows."""
    rows = [dict(r) for r in rows]
    for r in rows:
        p = prices.get(key(r["model"]))
        r["price"] = blended(p) if p else None
        r["open"] = p is not None and p["open_weights"] == "True"
    pool = [r for r in rows if r["open"] or not open_only]
    if not pool:
        return None, None, [], []
    best = max(pool, key=lambda r: r["score"])
    tied = [r for r in pool if best["score"] - r["score"] <= Z * math.hypot(best["se"] or 0, r["se"] or 0)]
    priced = sorted((r for r in tied if r["price"] is not None), key=lambda r: (r["price"], -r["score"]))
    unpriced = [r for r in tied if r["price"] is None]
    return best, (priced[0] if priced else None), priced, unpriced


def show(r, source):
    score = f"{r['score']:.0f} Elo" if source == "arena" else f"{100 * r['score']:.1f}%"
    se = "" if r["se"] is None else (f" +/-{Z * r['se']:.0f}" if source == "arena" else f" +/-{100 * Z * r['se']:.1f}")
    price = "price unknown" if r["price"] is None else f"${r['price']:.2f}/M tokens"
    return f"{r['model']}  {score}{se}  {price}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("benchmark", nargs="?", help="benchmark name, or a part of it")
    ap.add_argument("--list", nargs="?", const="", metavar="FILTER", help="list benchmarks")
    ap.add_argument("--open", action="store_true", help="only open-weight models")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(errors="replace")

    scores, prices = load()
    benchmarks = {}
    for r in scores:
        b = benchmarks.setdefault((r["source"], r["benchmark"]), {"n": 0, "date": ""})
        b["n"] += 1
        b["date"] = max(b["date"], r["date"])

    if args.list is not None:
        for (src, name), b in sorted(benchmarks.items()):
            if args.list.lower() in name.lower():
                print(f"{name}  [{src}, {b['n']} models, newest score {b['date']}]")
        return 0
    if not args.benchmark:
        ap.error("give a benchmark name or use --list")

    names = [k for k in benchmarks if k[1] == args.benchmark] or [
        k for k in benchmarks if args.benchmark.lower() in k[1].lower()
    ]
    if len(names) != 1:
        print("No single benchmark matches. Candidates:" if names else "Unknown benchmark. Try --list.")
        for src, name in names:
            print(f"  {name}")
        return 1
    source, name = names[0]

    best, rec, priced, unpriced = pick([r for r in scores if r["benchmark"] == name], prices, args.open)
    if best is None:
        print("No open-weight model with a known price in this benchmark.")
        return 1
    fetched = (DATA / "last_update.txt").read_text().strip()
    print(f"Benchmark: {name} ({source}), newest score {benchmarks[(source, name)]['date']}, data fetched {fetched}")
    print(f"{'Best (open only):' if args.open else 'Best:':<18}{show(best, source)}")
    if rec is None:
        print(f"{'Recommended:':<18}none (no priced model is statistically tied with the best)")
    else:
        extra = ""
        if best["price"] and rec is not best and rec["price"] < best["price"]:
            extra = f"  <- {best['price'] / max(rec['price'], 0.01):.1f}x cheaper than the best"
        print(f"{'Recommended:':<18}{show(rec, source)}{extra}")
    others = [r for r in priced if r is not rec and r is not best]
    if others:
        print("Also tied with the best, cheapest first:")
        for r in others[:7]:
            print(f"  {show(r, source)}")
    if unpriced:
        print("Tied but no price found (not considered): " + ", ".join(r["model"] for r in unpriced[:8]))
    print("Tied = scores within 95% confidence of the best.")
    print(
        "Price = median listed price on models.dev, 3:1 input:output blend. Per token only: reasoning modes use more tokens."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
