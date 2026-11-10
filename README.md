# AI Benchmark Check

Answers questions about current AI models from open leaderboards and public prices: which model is strongest, which to use for a task, and the **cheapest model that is statistically as good as the best one**.

**Status:** small personal project. Tested on Python 3.12, on Windows and on Linux (GitHub Actions).

## Example

"Which model should read my scanned invoices?" is a question about OCR, so:

```text
$ python recommend.py vision_style_control/ocr
Benchmark: vision_style_control/ocr (arena), newest score 2026-11-09, data fetched 2026-11-10
Best:             Claude Fable 5 (High)  1327 Elo +/-7  $20.00/M tokens
Recommended:      Gemini 3.8 Flash (High)  1315 Elo +/-9  $1.50/M tokens  <- 13.3x cheaper than the best
Tied = scores within 95% confidence of the best.
Price = median listed price on models.dev, 3:1 input:output blend. Per token only: reasoning modes use more tokens.
```

"Which model is the strongest overall?" uses the Epoch Capabilities Index:

```text
$ python recommend.py eci --top 5
Benchmark: eci (epoch), newest score 2026-11-09, data fetched 2026-11-10
  1. Claude Fable 5.2  174.2 ECI +/-4.3  $16.00/M tokens  Anthropic
  2. GPT-6 Astra  169.2 ECI +/-3.2  $20.00/M tokens  OpenAI
  3. GPT-6.1 Sol  168.9 ECI +/-3.2  $4.00/M tokens  OpenAI
  4. Claude Opus 5.5  168.7 ECI +/-3.1  $8.00/M tokens  Anthropic
  5. GPT-6.1 Terra  168.1 ECI +/-3.2  $2.00/M tokens  OpenAI
```

This is a snapshot from 10 November 2026. The data changes every day.
[`data/SNAPSHOT.md`](data/SNAPSHOT.md) is a one-page overview of the current data: strongest models, newest releases, best model of each lab, top 5 of the key benchmarks.

## Quickstart

You need Python 3.12 or newer. No API key, no account.

1. Get the code: `git clone https://github.com/Baobababab/ai-benchmark-check.git`
   (no Git? On the GitHub page use **Code → Download ZIP** and unzip it).
2. Open a terminal in the folder: `cd ai-benchmark-check`
3. Ask a question:

```bash
python recommend.py --list              # what you can ask about
python recommend.py gpqa_diamond        # cheapest model tied with the best on science questions
python recommend.py coding --open       # open-weight models only
python recommend.py eci --top 10        # the 10 strongest models overall
```

`recommend.py` only reads the files in `data/` and uses the Python standard library, so nothing needs installing.
The benchmark name can be a part of the full name (`coding` finds `text_style_control/coding`).
On some systems the command is `python3` instead of `python`.

### Refresh the data yourself (optional)

The data also updates every day on GitHub. To download it yourself, create an isolated environment first:

```bash
python -m venv .venv
source .venv/bin/activate               # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python fetch.py
```

`fetch.py` writes `data/scores.csv`, `data/models.csv` and `data/SNAPSHOT.md`.

### Use it inside Claude Code

Open this folder in Claude Code and ask anything about models, for example "Which model should I use to summarise legal contracts?" or "Compare the newest models of each lab".
The skill in [`.claude/skills/model-advisor`](.claude/skills/model-advisor/SKILL.md) makes Claude read `data/SNAPSHOT.md`, query the data with `recommend.py` when it needs more detail, and explain the result with the numbers from the data.
[`evals/cases.md`](evals/cases.md) lists five questions to check it with.

## How it works

- **Input:** three open data sources, downloaded by `fetch.py` into `data/`:
  [LMArena](https://arena.ai) (which answers people prefer), [Epoch AI](https://epoch.ai/benchmarks) (which answers are correct: science, maths, puzzles; plus the Epoch Capabilities Index, ECI, one number per model that combines many benchmarks; plus each model's lab and availability) and [models.dev](https://models.dev) (prices, release dates).
- **Processing:** for one benchmark, each model counts once, with its best variant (High, Max...). Two models are *tied* when their score difference is smaller than the statistical noise (95% confidence, using the published uncertainty of each score). Among the models tied with the best, the cheapest wins. Prices are matched to scores by model name.
- **Output:** the best model, the recommended one and the other tied options, with scores and prices. `--top N` shows the ranking instead.

I chose this rule because I can explain it in one sentence and check it by hand.
A GitHub Actions job runs `fetch.py` every day and commits the new data. If a source is empty, stale or its model names no longer match the price list, `fetch.py` stops with an error and the data is not updated. GitHub can disable scheduled workflows after 60 days without repository activity; if the data looks old, start the run by hand from the Actions tab.

## Checks

```bash
python -m unittest
```

Fourteen tests run offline. They check the name matching, the tie rule, the Epoch parser on a small fake data file, that a broken data source stops the update, and that the committed data produces answers. On every push, GitHub Actions also runs the tests and the [Ruff](https://docs.astral.sh/ruff/) style checks (the CI badge above). `fetch.py` has its own sanity checks (row counts, data age, price coverage) that run on every update.

## Limitations and safety

- **Two kinds of quality.** LMArena measures preference, not correctness. Epoch measures correctness, but only on science, maths and puzzles. ECI is Epoch's own combination of its benchmarks.
- **Not covered:** agentic coding (SWE-bench style), speed, image and video generation prices, long-context accuracy. I found no data for these that I may legally redistribute.
- **Prices are rough.** Per token only, the median across providers, assuming 3 input tokens per output token. Reasoning modes (High, Max) use more tokens, so real costs can be higher. Tiered prices (for example above 100,000 tokens), caching and batch discounts are ignored.
- **New models.** A model can be missing from LMArena for days after its release, and the same model can appear under different names in different sources. Models without a matching price show as "price unknown" and are never recommended.
- **Availability.** Epoch marks some models as `Unreleased` or `Limited access`. The output warns about them, but I do not check availability myself.
- **Tied is not equal.** New models have few votes and a wide uncertainty, so they can look tied with the best. The `+/-` shows how sure a score is. A benchmark where the best score is 95% or more is near its ceiling and the output says so.
- **The tie test is simple.** It treats each score as independent and the intervals as symmetric. Scores of different models are measured on the same questions or battles, so a paired test could separate some pairs that this one calls tied.
- **Only the top 100 models** of each LMArena benchmark are kept, so `--open` only sees open-weight models in that list.
- **LMArena not compared with its website.** The data comes from LMArena's published Hugging Face dataset. The website blocks automated browsers, so I could not check the numbers against the leaderboard page. The Epoch figures were checked against Epoch's raw download, and the Anthropic prices against Anthropic's pricing page.
- It does not replace testing a model on your own task. No credentials are used or stored.

## AI-assisted development

I specified the tool, chose the data sources and decided which ones I may legally redistribute. The code was written with an AI coding agent (Claude Code). I reviewed the results and I am responsible for what is published here.

## Sources and attribution

Data: LMArena (CC BY 4.0), Epoch AI (CC BY 4.0), models.dev (MIT). Details, citations and the sources I did not use are in [DATA_LICENSES.md](DATA_LICENSES.md).

## License

Code: MIT, see [LICENSE](LICENSE). The data in `data/` keeps the licenses of its sources.
