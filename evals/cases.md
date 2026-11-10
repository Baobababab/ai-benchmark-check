# Skill checks

Five questions to ask the `model-advisor` skill in a fresh Claude Code session opened in this
folder. They are manual: the answer is written by a language model, so each case lists what a
correct answer must contain, not an exact text. Check the numbers against `data/SNAPSHOT.md` or
`python recommend.py <benchmark> --top 10`.

Record the date, the data date (`data/last_update.txt`) and the result of each run in the table at the end.

## Cases

| # | Question | A correct answer | A wrong answer |
|---|---|---|---|
| 1 | "Which model is the strongest overall right now?" | Uses the ECI. Names the top model with its score and says it is a combination of Epoch benchmarks. Mentions that models near the top are statistically close. | Picks the top of an LMArena preference ranking and calls it the strongest overall. |
| 2 | "Give me an overview of the main labs and their best models." | One model per lab with lab name, score and price, taken from the snapshot. Says where the lab comes from (Epoch metadata, or LMArena when Epoch does not know the model). | Labs guessed from model names, or labs missing from the data presented as if they were not important. |
| 3 | "Compare GPT-6 Astra and GPT-6.1 Sol." | Uses the ECI plus at least one benchmark where both appear. Says if they are tied. Quotes the price of each. | States a winner when the scores are inside each other's margin of error. |
| 4 | "Cheapest open-weight model that is good for Italian text?" | Uses `text_style_control/non_english` (there is no Italian benchmark) with `--open`, says why, and quotes the price. | Invents an Italian benchmark, or ignores `--open`. |
| 5 | "Which model is best for agentic coding with SWE-bench?" | Says the data has no agentic coding benchmark and names the closest one (`text_style_control/coding`) with its caveat. | Gives a ranking as if it measured agentic coding. |

## Runs

| Date | Data date | Passed | Notes |
|---|---|---|---|
| 2026-11-10 | 2026-11-10 | 5 of 5 | Run by a Claude subagent that read `SKILL.md` and answered the five questions, not by an interactive session. I checked its ranks and prices against `recommend.py`: they match. It said it could not find Astra's release date, because the snapshot only lists releases of the last 60 days, and `--list` printed nothing when no benchmark matched. Both fixed afterwards: `--model` and a "no match" message. Not re-run since: the skill and the script changed after this run. |
