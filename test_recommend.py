"""Offline checks for the recommendation logic and the data parser. Run: python -m unittest"""

import contextlib
import io
import unittest
import zipfile
from datetime import date

from fetch import check, epoch, epoch_meta, models
from recommend import key, main, pick, snapshot

PRICES = {  # key -> model row, as read from data/models.csv
    "bigmodel": {"input": "10", "output": "30", "open_weights": "False"},  # blended $15
    "midmodel": {"input": "1", "output": "3", "open_weights": "False"},  # blended $1.5
    "openmodel": {"input": "0.2", "output": "0.6", "open_weights": "True"},  # blended $0.3
    "weakmodel": {"input": "0.1", "output": "0.1", "open_weights": "True"},  # cheap but clearly worse
}


def row(model, score, se):
    return {"model": model, "score": score, "se": se}


ROWS = [
    row("BigModel", 1500, 5),  # best
    row("MidModel (High)", 1495, 5),  # within noise of the best, 10x cheaper
    row("OpenModel", 1493, 5),  # within noise, cheapest tied model
    row("WeakModel", 1400, 5),  # cheaper still, but clearly worse: not tied
    row("MysteryModel", 1499, 5),  # tied but no price
]


class KeyTest(unittest.TestCase):
    def test_same_model_different_spellings(self):
        names = ["Claude Fable 5.2 (Max)", "claude-fable-5-2_max", "claude-fable-5-2", "anthropic/claude-fable-5.2"]
        self.assertEqual({key(n) for n in names}, {"claudefable52"})

    def test_date_stamp_and_name_part_max(self):
        self.assertEqual(key("gpt-5.4-2026-03-05_xhigh"), key("gpt-5.4"))
        self.assertNotEqual(key("Qwen 3.8 Max"), key("Qwen 3.8"))  # 'Max' in a name is not an effort tag

    def test_epoch_effort_tags_none_and_promax(self):
        self.assertEqual(key("gpt-6-astra_none"), key("GPT-6 Astra (Max)"))
        self.assertEqual(key("gpt-6-astra_promax"), key("GPT-6 Astra (Max)"))


class PickTest(unittest.TestCase):
    def test_recommends_cheapest_tied_model(self):
        best, rec, priced, unpriced = pick(ROWS, PRICES)
        self.assertEqual(best["model"], "BigModel")
        self.assertEqual(rec["model"], "OpenModel")
        self.assertEqual([r["model"] for r in priced], ["OpenModel", "MidModel (High)", "BigModel"])
        self.assertEqual([r["model"] for r in unpriced], ["MysteryModel"])

    def test_open_only_ignores_closed_models(self):
        best, rec, _, _ = pick(ROWS, PRICES, open_only=True)
        self.assertEqual((best["model"], rec["model"]), ("OpenModel", "OpenModel"))

    def test_no_uncertainty_means_only_exact_ties(self):
        rows = [row("BigModel", 90, None), row("MidModel", 89, None)]
        _, rec, _, _ = pick(rows, PRICES)
        self.assertEqual(rec["model"], "BigModel")

    def test_one_row_per_model(self):
        rows = [row("MidModel (High)", 1490, 5), row("MidModel (Low)", 1480, 5), row("MidModel", 1485, 5)]
        best, _, priced, _ = pick(rows, PRICES)
        self.assertEqual((best["score"], len(priced)), (1490, 1))  # the variants collapse into the best one

    def test_equal_top_scores_do_not_depend_on_order(self):
        rows = [row("BigModel", 100, 0), row("MidModel", 100, 0)]
        for rows_in_order in (rows, rows[::-1]):
            self.assertEqual(pick(rows_in_order, PRICES)[0]["model"], "MidModel")  # the cheaper one

    def test_zero_uncertainty_uses_the_typical_one(self):
        rows = [row("BigModel", 100, 0), row("MidModel", 99, 0), row("OpenModel", 80, 5)]
        _, rec, priced, _ = pick(rows, PRICES)
        self.assertEqual(rec["model"], "MidModel")  # 1 point apart is noise, not a difference
        self.assertNotIn("OpenModel", [r["model"] for r in priced])


def fake_epoch_zip():
    files = {
        "benchmark_metadata.csv": "benchmark,source_file,score_column,superseded_by\n"
        "GPQA,gpqa.csv,Best score (across scorers),\n"
        "Other,other_external.csv,mean_score,\n",
        "gpqa.csv": "Model version,mean_score,Best score (across scorers),stderr,Started at\n"
        "m_high,0.5,0.7,0.02,2026-11-01T00:00:00Z\n"
        "m_high,0.4,0.9,0.02,2026-10-01T00:00:00Z\n",
        "other_external.csv": "Model version,mean_score,stderr,Started at\nm,0.1,0.01,2026-11-01T00:00:00Z\n",
        "epoch_capabilities_index/eci_scores.csv": "Display name,eci,eci_ci_low,eci_ci_high,date\n"
        "Big Model,170,166,174,2026-11-09\n",
        "model_metadata.csv": "model_version,model_group,organization,accessibility\n"
        "big-model_high,Big Model,Some Lab,Unreleased\n",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


class ParserTest(unittest.TestCase):
    def test_epoch_zip(self):
        out = epoch(fake_epoch_zip())
        gpqa = [r for r in out if r["benchmark"] == "gpqa"]
        self.assertEqual([(r["model"], r["score"]) for r in gpqa], [("m_high", "0.7")])  # newest run, Epoch's column
        self.assertFalse([r for r in out if "other" in r["benchmark"]])  # external data is skipped
        eci = next(r for r in out if r["benchmark"] == "eci")
        self.assertEqual((eci["model"], eci["score"], round(eci["se"], 2)), ("Big Model", "170", 2.04))

    def test_epoch_meta(self):
        self.assertEqual(epoch_meta(fake_epoch_zip())["bigmodel"], ("Some Lab", "Unreleased"))


class ModelsTest(unittest.TestCase):
    def test_lab_from_lmarena_written_like_epoch(self):
        meta = {"known": ("Meta AI", "API access")}
        orgs = {"known": "meta", "newone": "meta", "stranger": "some-lab", "nolab": ""}
        scores = [{"model": n} for n in ("Known", "NewOne (Max)", "Stranger", "NoLab")]
        labs = {r["key"]: r["lab"] for r in models([], scores, meta, orgs)}
        self.assertEqual(labs, {"known": "Meta AI", "newone": "Meta AI", "stranger": "Some Lab", "nolab": ""})


class CheckTest(unittest.TestCase):
    """fetch.check() must stop the update instead of letting broken data through."""

    def test_empty_source_is_rejected(self):
        scores = [{"source": "arena", "benchmark": "x", "model": "m", "score": 1, "se": 1, "date": "2026-11-09"}]
        with self.assertRaises(SystemExit):
            check(scores, [])


class OutputTest(unittest.TestCase):
    """The committed data must produce answers without errors."""

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(args))
        return code, out.getvalue()

    def test_recommendation_and_top(self):
        code, text = self.run_main("coding")
        self.assertEqual(code, 0)
        self.assertIn("Recommended:", text)
        code, text = self.run_main("eci", "--top", "3")
        self.assertEqual(code, 0)
        self.assertEqual(len([line for line in text.splitlines() if " ECI " in line]), 3)

    def test_one_model_and_unknown_inputs(self):
        code, text = self.run_main("--model", "gpt-6.1-sol")
        self.assertEqual(code, 0)
        self.assertIn("  eci  ", text)
        self.assertEqual(self.run_main("--model", "no-such-model-xyz")[0], 1)
        self.assertEqual(self.run_main("--list", "no-such-benchmark-xyz")[0], 1)

    def test_snapshot_has_every_section(self):
        text = snapshot(date(2026, 11, 10))
        for heading in ("Strongest models overall", "Newest models", "Best model of each lab", "Key benchmarks"):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
