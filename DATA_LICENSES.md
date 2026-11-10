# Data sources and licenses

The code in this repository is MIT licensed (see [LICENSE](LICENSE)). The files in `data/` are
derived from the three sources below and keep **their** licenses. Terms were read on
10 November 2026; they can change, so check the source before reusing the data elsewhere.

## LMArena: human preference scores

- Source: [lmarena-ai/leaderboard-dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) on Hugging Face, by LMArena (lmarena.ai).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Changes made here: only the `latest` split, only the `text_style_control`, `vision_style_control`,
  `webdev`, `search` and `document` configs, the top 100 models per category, selected columns,
  standard error computed from the published 95% confidence interval.

## Epoch AI: correctness benchmarks

- Source: [Epoch AI benchmark data](https://epoch.ai/benchmarks/use-this-data), `benchmark_data.zip`.
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), for Epoch's own evaluation runs.
  Files ending in `_external.csv` come from other projects, keep their original licenses and are **not** used here.
- Citation: Epoch AI, 'Capabilities & benchmarking'. Published online at epoch.ai. Retrieved from 'https://epoch.ai/benchmarks' [online resource].
- Also used from the same download: the Epoch Capabilities Index (`epoch_capabilities_index/eci_scores.csv`)
  and the lab and availability of each model (`model_metadata.csv`). The ECI is computed by Epoch from many
  benchmarks, some of them from external projects. Epoch distributes it in the same download under the same
  CC BY 4.0 grant and without an external-license marker, so it is treated as Epoch's own data. This reading was
  made on 10 November 2026; if Epoch states otherwise, remove the `eci` rows from `fetch.py`.
- Changes made here: latest run per model, selected columns, the score column named by Epoch's own metadata,
  benchmarks marked as superseded are skipped, standard error of the ECI computed from its published interval.

## models.dev: prices and open-weight flag

- Source: [models.dev](https://models.dev) ([repository](https://github.com/anomalyco/models.dev)).
- License: MIT. Notice required by the license:

```text
MIT License

Copyright (c) 2025 models.dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- Changes made here: one price per model (the median listed price across providers, free plans ignored), the
  earliest release date listed by any provider, selected columns.

## Sources considered and not used

Not used because no license allowing automated download **and** public redistribution was found
on 10 November 2026: Artificial Analysis (free API is "internal use only"; its website terms forbid
scraping), Scale Labs, Vals.ai, Vellum, LiveBench 2.0, Terminal-Bench leaderboard, and the SWE-bench
leaderboard site (non-commercial license). If one of them grants permission, it can be added in `fetch.py`.
