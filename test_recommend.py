"""Offline checks for the recommendation logic. Run: python -m unittest"""
import unittest

from recommend import key, pick

PRICES = {  # key -> price row, as read from data/prices.csv
    "bigmodel": {"input": "10", "output": "30", "open_weights": "False"},       # blended $15
    "midmodel": {"input": "1", "output": "3", "open_weights": "False"},         # blended $1.5
    "openmodel": {"input": "0.2", "output": "0.6", "open_weights": "True"},     # blended $0.3
    "weakmodel": {"input": "0.1", "output": "0.1", "open_weights": "True"},     # cheap but clearly worse
}


def row(model, score, se):
    return {"model": model, "score": score, "se": se}


class KeyTest(unittest.TestCase):
    def test_same_model_different_spellings(self):
        names = ["Claude Fable 5.2 (Max)", "claude-fable-5-2_max", "claude-fable-5-2", "anthropic/claude-fable-5.2"]
        self.assertEqual({key(n) for n in names}, {"claudefable52"})

    def test_date_stamp_and_name_part_max(self):
        self.assertEqual(key("gpt-5.4-2026-03-05_xhigh"), key("gpt-5.4"))
        self.assertNotEqual(key("Qwen 3.8 Max"), key("Qwen 3.8"))  # 'Max' in a name is not an effort tag


class PickTest(unittest.TestCase):
    rows = [
        row("BigModel", 1500, 5),     # best
        row("MidModel (High)", 1495, 5),  # within noise of the best, 10x cheaper
        row("OpenModel", 1493, 5),    # within noise, cheapest tied model
        row("WeakModel", 1400, 5),    # cheaper still, but clearly worse: not tied
        row("MysteryModel", 1499, 5),  # tied but no price
    ]

    def test_recommends_cheapest_tied_model(self):
        best, rec, priced, unpriced = pick(self.rows, PRICES)
        self.assertEqual(best["model"], "BigModel")
        self.assertEqual(rec["model"], "OpenModel")
        self.assertEqual([r["model"] for r in priced], ["OpenModel", "MidModel (High)", "BigModel"])
        self.assertEqual([r["model"] for r in unpriced], ["MysteryModel"])

    def test_open_only_ignores_closed_models(self):
        best, rec, _, _ = pick(self.rows, PRICES, open_only=True)
        self.assertEqual((best["model"], rec["model"]), ("OpenModel", "OpenModel"))

    def test_no_uncertainty_means_only_exact_ties(self):
        rows = [row("BigModel", 90, None), row("MidModel", 89, None)]
        _, rec, _, _ = pick(rows, PRICES)
        self.assertEqual(rec["model"], "BigModel")


if __name__ == "__main__":
    unittest.main()
