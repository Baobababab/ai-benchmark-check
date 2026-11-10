"""Download the three data sources into data/. Stops with an error if a source looks broken.

    python fetch.py

Sources (licenses in DATA_LICENSES.md):
  LMArena     human preference scores      HuggingFace lmarena-ai/leaderboard-dataset
  Epoch AI    correctness benchmarks       epoch.ai/data/benchmark_data.zip (Epoch's own runs only)
  models.dev  prices, open-weight flag     models.dev/api.json
"""
import csv
import io
import json
import statistics
import sys
import urllib.request
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pyarrow.parquet as pq

from recommend import key

DATA = Path(__file__).parent / "data"
UA = {"User-Agent": "ai-benchmark-check (https://github.com/Baobababab/ai-benchmark-check)"}
ARENA = "https://datasets-server.huggingface.co/parquet?dataset=lmarena-ai/leaderboard-dataset"
EPOCH = "https://epoch.ai/data/benchmark_data.zip"
MODELS_DEV = "https://models.dev/api.json"
ARENA_CONFIGS = {"text_style_control", "vision_style_control", "webdev", "search", "document"}
TOP = 100  # keep the best 100 models per benchmark: enough to find ties, keeps the files small
MAX_AGE = timedelta(days=60)  # newest score older than this means the source stopped updating
SCORE_FIELDS = ["source", "benchmark", "model", "score", "se", "date"]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def arena():
    out = []
    for f in json.loads(get(ARENA))["parquet_files"]:
        if f["split"] != "latest" or f["config"] not in ARENA_CONFIGS:
            continue
        rows = pq.read_table(io.BytesIO(get(f["url"]))).to_pylist()
        for cat in {r["category"] for r in rows}:
            top = sorted((r for r in rows if r["category"] == cat), key=lambda r: -r["rating"])[:TOP]
            for r in top:
                lo, hi = r["rating_lower"], r["rating_upper"]
                se = (hi - lo) / (2 * 1.96) if lo is not None and hi is not None else ""
                out.append(dict(source="arena", benchmark=f"{f['config']}/{cat}", model=r["model_name"],
                                score=r["rating"], se=se, date=str(r["leaderboard_publish_date"])[:10]))
    return out


def epoch():
    z = zipfile.ZipFile(io.BytesIO(get(EPOCH)))
    out = []
    meta = csv.DictReader(io.TextIOWrapper(z.open("benchmark_metadata.csv"), encoding="utf-8"))
    for m in meta:
        # Only Epoch's own runs are CC BY. Files ending in _external keep their original license.
        if not m["source_file"] or m["source_file"].endswith("_external.csv") or m["superseded_by"]:
            continue
        latest = {}  # newest run per model
        for r in csv.DictReader(io.TextIOWrapper(z.open(m["source_file"]), encoding="utf-8")):
            if r["mean_score"] and (r["Model version"] not in latest or r["Started at"] > latest[r["Model version"]]["Started at"]):
                latest[r["Model version"]] = r
        for r in latest.values():
            out.append(dict(source="epoch", benchmark=m["source_file"].removesuffix(".csv"), model=r["Model version"],
                            score=r["mean_score"], se=r["stderr"], date=r["Started at"][:10]))
    return out


def prices():
    by_key = {}
    for provider, p in json.loads(get(MODELS_DEV)).items():
        for model_id, m in p["models"].items():
            c = m.get("cost") or {}
            if (c.get("input") or 0) > 0 and (c.get("output") or 0) > 0:  # 0 = free plan, not a price
                by_key.setdefault(key(model_id), []).append((provider, c["input"], c["output"], m))
    out = []
    for k, offers in by_key.items():
        offers.sort(key=lambda o: (o[1] + o[2], o[0]))  # equal prices: order by provider name, so every run picks the same offer
        _, inp, outp, m = offers[len(offers) // 2]  # median offer: hosts of open models vary a lot
        out.append(dict(key=k, input=inp, output=outp, open_weights=bool(m.get("open_weights"))))
    return out


def drop_stale(scores):
    """Remove benchmarks nobody has updated for 4 months: their ranking is out of date."""
    newest = {}
    for r in scores:
        newest[r["benchmark"]] = max(newest.get(r["benchmark"], ""), r["date"])
    limit = (date.today() - timedelta(days=120)).isoformat()
    return [r for r in scores if newest[r["benchmark"]] >= limit]


def write(name, fields, rows):
    with open(DATA / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")  # same bytes on Windows and Linux
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: [str(r[k]) for k in fields[:3]]))


def check(scores, price_rows):
    """Fail loudly instead of committing broken or stale data."""
    for source, minimum in (("arena", 1000), ("epoch", 300)):
        n = sum(r["source"] == source for r in scores)
        newest = max((r["date"] for r in scores if r["source"] == source), default="")
        if n < minimum:
            sys.exit(f"ERROR: {source} returned {n} rows (expected >= {minimum}). Did the source change?")
        if datetime.strptime(newest, "%Y-%m-%d").date() < date.today() - MAX_AGE:
            sys.exit(f"ERROR: newest {source} score is from {newest}. Did the source stop updating?")
    if len(price_rows) < 500:
        sys.exit(f"ERROR: models.dev returned only {len(price_rows)} priced models.")
    priced = {r["key"] for r in price_rows}
    top = [r["model"] for r in scores if r["benchmark"] == "text_style_control/overall"][:20]
    found = sum(key(m) in priced for m in top)
    if found < 14:
        sys.exit(f"ERROR: only {found}/20 top Arena models have a price. Name matching may be broken.")


if __name__ == "__main__":
    scores = drop_stale(arena() + epoch())
    price_rows = prices()
    check(scores, price_rows)
    DATA.mkdir(exist_ok=True)
    write("scores.csv", SCORE_FIELDS, scores)
    write("prices.csv", ["key", "input", "output", "open_weights"], price_rows)
    (DATA / "last_update.txt").write_text(date.today().isoformat() + "\n")
    print(f"OK: {len(scores)} scores, {len(price_rows)} priced models")
