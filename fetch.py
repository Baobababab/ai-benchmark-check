"""Download the three data sources into data/. Stops with an error if a source looks broken.

    python fetch.py

Sources (licenses in DATA_LICENSES.md):
  LMArena     human preference scores      HuggingFace lmarena-ai/leaderboard-dataset
  Epoch AI    correctness benchmarks, the Epoch Capabilities Index (ECI), lab and availability of each model
              epoch.ai/data/benchmark_data.zip (Epoch's own runs only)
  models.dev  prices, open-weight flag, release date     models.dev/api.json
"""

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from recommend import Z, key, snapshot

DATA = Path(__file__).parent / "data"
UA = {"User-Agent": "ai-benchmark-check (https://github.com/Baobababab/ai-benchmark-check)"}
ARENA = "https://datasets-server.huggingface.co/parquet?dataset=lmarena-ai/leaderboard-dataset"
EPOCH = "https://epoch.ai/data/benchmark_data.zip"
MODELS_DEV = "https://models.dev/api.json"
ARENA_CONFIGS = {"text_style_control", "vision_style_control", "webdev", "search", "document"}
TOP = 100  # keep the best 100 models per benchmark: enough to find ties, keeps the files small
MAX_AGE = timedelta(days=60)  # newest score older than this means the source stopped updating
SCORE_FIELDS = ["source", "benchmark", "model", "score", "se", "date"]
MODEL_FIELDS = ["key", "input", "output", "open_weights", "released", "lab", "access", "name"]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def arena():
    """LMArena scores, and the lab slug of every model (like 'zai' or 'meta')."""
    import pyarrow.parquet as pq  # only needed here, so tests can import this file without it

    out, orgs = [], {}
    for f in json.loads(get(ARENA))["parquet_files"]:
        if f["split"] != "latest" or f["config"] not in ARENA_CONFIGS:
            continue
        rows = pq.read_table(io.BytesIO(get(f["url"]))).to_pylist()
        for cat in {r["category"] for r in rows}:
            top = sorted((r for r in rows if r["category"] == cat), key=lambda r: -r["rating"])[:TOP]
            for r in top:
                orgs[key(r["model_name"])] = r["organization"]
                lo, hi = r["rating_lower"], r["rating_upper"]
                se = (hi - lo) / (2 * Z) if lo is not None and hi is not None else ""
                out.append(
                    {
                        "source": "arena",
                        "benchmark": f"{f['config']}/{cat}",
                        "model": r["model_name"],
                        "score": r["rating"],
                        "se": se,
                        "date": str(r["leaderboard_publish_date"])[:10],
                    }
                )
    return out, orgs


def epoch(z):
    out = []
    meta = csv.DictReader(io.TextIOWrapper(z.open("benchmark_metadata.csv"), encoding="utf-8"))
    for m in meta:
        # Only Epoch's own runs are CC BY. Files ending in _external keep their original license.
        if not m["source_file"] or m["source_file"].endswith("_external.csv") or m["superseded_by"]:
            continue
        col = m["score_column"] or "mean_score"  # the column Epoch itself reports for this benchmark
        latest = {}  # newest run per model
        for r in csv.DictReader(io.TextIOWrapper(z.open(m["source_file"]), encoding="utf-8")):
            if r[col] and (
                r["Model version"] not in latest or r["Started at"] > latest[r["Model version"]]["Started at"]
            ):
                latest[r["Model version"]] = r
        for r in latest.values():
            out.append(
                {
                    "source": "epoch",
                    "benchmark": m["source_file"].removesuffix(".csv"),
                    "model": r["Model version"],
                    "score": r[col],
                    "se": r["stderr"],
                    "date": r["Started at"][:10],
                }
            )
    # The Epoch Capabilities Index combines many benchmarks into one number per model.
    for r in csv.DictReader(io.TextIOWrapper(z.open("epoch_capabilities_index/eci_scores.csv"), encoding="utf-8")):
        if r["eci"]:
            lo, hi = r["eci_ci_low"], r["eci_ci_high"]
            out.append(
                {
                    "source": "epoch",
                    "benchmark": "eci",
                    "model": r["Display name"],
                    "score": r["eci"],
                    "se": (float(hi) - float(lo)) / (2 * Z) if lo and hi else "",  # assumes a symmetric 95% interval
                    "date": r["date"][:10],
                }
            )
    return out


def epoch_meta(z):
    """Lab and availability ('API access', 'Limited access', 'Unreleased'...) of every Epoch model, by key."""
    meta = {}
    for r in csv.DictReader(io.TextIOWrapper(z.open("model_metadata.csv"), encoding="utf-8")):
        lab = r["organization"].split(",")[0]  # some models list several labs: keep the first
        meta.setdefault(key(r["model_group"]), (lab, r["accessibility"]))
    return meta


def prices():
    by_key = {}
    for provider, p in json.loads(get(MODELS_DEV)).items():
        for model_id, m in p["models"].items():
            c = m.get("cost") or {}
            if (c.get("input") or 0) > 0 and (c.get("output") or 0) > 0:  # 0 = free plan, not a price
                by_key.setdefault(key(model_id), []).append((provider, c["input"], c["output"], m))
    out = []
    for k, offers in by_key.items():
        # Equal prices are ordered by provider name, so every run picks the same offer.
        offers.sort(key=lambda o: (o[1] + o[2], o[0]))
        _, inp, outp, m = offers[len(offers) // 2]  # median offer: hosts of open models vary a lot
        dates = (o[3].get("release_date") or "" for o in offers)
        released = min((d for d in dates if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d >= "2015"), default="")
        out.append(
            {"key": k, "input": inp, "output": outp, "open_weights": bool(m.get("open_weights")), "released": released}
        )
    return out


def models(price_rows, scores, meta, orgs):
    """One row per model: price, open-weight flag and release date (models.dev), lab and availability (Epoch).

    A model Epoch does not know gets the lab LMArena gives it, written the way Epoch writes that lab.
    """
    priced = {r["key"]: r for r in price_rows}
    spelling = {}  # LMArena slug -> Epoch's name for the lab, from the models both sources know
    for (slug, lab), _ in Counter((orgs[k], meta[k][0]) for k in orgs if k in meta and orgs[k]).most_common():
        spelling.setdefault(slug, lab)
    display = {}  # proper name of a model: from ECI or LMArena, never a raw Epoch run id
    for r in sorted(scores, key=lambda r: r["benchmark"] != "eci"):
        if r["source"] == "arena" or r["benchmark"] == "eci":
            display.setdefault(key(r["model"]), r["model"])
    out = []
    for k in priced.keys() | {key(r["model"]) for r in scores}:
        p = priced.get(k, {})
        lab, access = meta.get(k, ("", ""))
        slug = orgs.get(k, "")
        lab = lab or (spelling.get(slug) or slug.replace("-", " ").title())
        open_weights = "True" if access.startswith("Open weights") else p.get("open_weights", "")  # Epoch knows too
        out.append(
            {
                "key": k,
                "input": p.get("input", ""),
                "output": p.get("output", ""),
                "open_weights": open_weights,
                "released": p.get("released", ""),
                "lab": lab,
                "access": access,
                "name": display.get(k, ""),
            }
        )
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
    for benchmark in ("text_style_control/overall", "eci"):
        rows = sorted((r for r in scores if r["benchmark"] == benchmark), key=lambda r: -float(r["score"]))
        if len(rows) < 50:
            sys.exit(f"ERROR: {benchmark} has only {len(rows)} rows (expected >= 50).")
        found = sum(key(r["model"]) in priced for r in rows[:20])
        if found < 14:
            sys.exit(f"ERROR: only {found}/20 top {benchmark} models have a price. Name matching may be broken.")


if __name__ == "__main__":
    z = zipfile.ZipFile(io.BytesIO(get(EPOCH)))
    arena_scores, orgs = arena()
    scores = drop_stale(arena_scores + epoch(z))
    price_rows = prices()
    check(scores, price_rows)
    DATA.mkdir(exist_ok=True)
    write("scores.csv", SCORE_FIELDS, scores)
    write("models.csv", MODEL_FIELDS, models(price_rows, scores, epoch_meta(z), orgs))
    (DATA / "last_update.txt").write_text(date.today().isoformat() + "\n", newline="\n")
    (DATA / "SNAPSHOT.md").write_text(snapshot(date.today()), encoding="utf-8", newline="\n")
    print(f"OK: {len(scores)} scores, {len(price_rows)} priced models")
