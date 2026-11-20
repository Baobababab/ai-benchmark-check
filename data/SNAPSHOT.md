# Model data snapshot

Written by `fetch.py` on 2026-11-20. Do not edit by hand. Newest LMArena score: 2026-11-19. Newest Epoch result: 2026-11-17.

How to read it:
- LMArena scores are human preference (Elo). They do not measure correctness.
- Epoch scores are correctness on benchmarks (%). ECI is Epoch's own index that combines many of them.
- Price = median listed price on models.dev, 3 input tokens per output token, per token only. Reasoning modes (High, Max) use more tokens, so real costs can be higher.
- Each model appears once, with its best variant. A model released in the last days can be missing from LMArena for a while, and the LMArena website marks very new models as 'Preliminary' (few votes), a flag this data lacks.
- Not covered: agentic coding, speed, latency, long-context accuracy, image and video generation prices.

## Strongest models overall: Epoch Capabilities Index (ECI), top 15

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | GPT-6.2 Astra | 174.2 ECI +/-4.1 | OpenAI | 16.00 |  |
| 2 | Claude Fable 5.2 | 173.5 ECI +/-3.6 | Anthropic | 16.00 |  |
| 3 | Gemini 4 Carbon | 169.8 ECI +/-3.4 | Google DeepMind | 4.00 |  |
| 4 | GPT-6 Astra | 169.2 ECI +/-3.1 | OpenAI | 20.00 |  |
| 5 | Claude Opus 5.5 | 168.7 ECI +/-3.0 | Anthropic | 8.00 |  |
| 6 | GPT-6.1 Sol | 168.6 ECI +/-3.1 | OpenAI | 4.00 |  |
| 7 | GPT-6.1 Terra | 167.7 ECI +/-3.1 | OpenAI | 2.00 |  |
| 8 | Claude Fable 5.1 | 167.1 ECI +/-2.8 | Anthropic | 20.00 |  |
| 9 | Claude Sonnet 5.5 | 166.6 ECI +/-2.9 | Anthropic | 4.00 |  |
| 10 | Gemini 4 Argon | 166.6 ECI +/-2.8 | Google DeepMind | 4.00 |  |
| 11 | Claude Opus 5 | 164.7 ECI +/-2.7 | Anthropic | 10.00 |  |
| 12 | Claude Fable 5 | 164.2 ECI +/-2.5 | Anthropic | 20.00 |  |
| 13 | GPT-6 Sol | 163.8 ECI +/-2.6 | OpenAI | 4.00 |  |
| 14 | GPT-5.6 Sol | 163.1 ECI +/-2.4 | OpenAI | 8.00 |  |
| 15 | GPT-5.5 Pro | 162.8 ECI +/-2.8 | OpenAI | 67.50 |  |

## Newest models (released in the last 60 days, date from models.dev)

30 models qualify, the 20 newest are shown.

| Released | Model | Lab | Price $/M | On LMArena | In ECI | Note |
|---|---|---|---|---|---|---|
| 2026-11-18 | Gemini 4 Neon (High) | Google DeepMind | 6.00 | yes | no |  |
| 2026-11-17 | GPT-6.2 Sol (Max) | OpenAI | 4.00 | yes | no |  |
| 2026-11-17 | GPT-6.2 Astra | OpenAI | 16.00 | yes | yes |  |
| 2026-11-16 | Qwen4-Max (xHigh) | Alibaba | 2.25 | yes | no |  |
| 2026-11-12 | Gemini 4 Hydrogen (High) | Google DeepMind | 3.00 | yes | no |  |
| 2026-11-10 | Gemini 4 Carbon | Google DeepMind | 4.00 | yes | yes |  |
| 2026-11-09 | Muse Ember (Max) | Meta AI | 0.20 | yes | no |  |
| 2026-11-09 | Claude Fable 5.2 | Anthropic | 16.00 | yes | yes |  |
| 2026-11-05 | Inkling 2 Small | Thinking Machines | 0.47 | yes | no |  |
| 2026-11-04 | Hy4 | Tencent | 1.25 | yes | no |  |
| 2026-10-26 | GPT-6.1 Terra | OpenAI | 2.00 | yes | yes |  |
| 2026-10-23 | Kimi K3.1 Pro | Moonshot | 4.00 | yes | yes |  |
| 2026-10-19 | MiniMax-M3.1-Flash | MiniMax | 0.26 | yes | no |  |
| 2026-10-17 | DeepSeek V4.1 Flash 1017 | DeepSeek | 0.52 | no | yes |  |
| 2026-10-15 | NVIDIA-Nemotron-3.5-Super-VL-120B-A12B (NVFP4) | Nvidia | 0.28 | yes | no |  |
| 2026-10-15 | Muse Spark Open | Meta AI | 2.00 | yes | yes |  |
| 2026-10-13 | Gemini 4 Argon | Google DeepMind | 4.00 | yes | yes |  |
| 2026-10-12 | Muse Wonder | Meta AI | 8.00 | yes | yes |  |
| 2026-10-07 | Claude Haiku 5.5 | Anthropic | 0.20 | yes | yes |  |
| 2026-10-06 | Mistral Large 4 | Mistral AI | 1.05 | yes | yes |  |

## Best model of each lab (by ECI, top 12 labs)

| Lab | Model | ECI | Price $/M |
|---|---|---|---|
| OpenAI | GPT-6.2 Astra | 174.2 ECI +/-4.1 | 16.00 |
| Anthropic | Claude Fable 5.2 | 173.5 ECI +/-3.6 | 16.00 |
| Google DeepMind | Gemini 4 Carbon | 169.8 ECI +/-3.4 | 4.00 |
| Meta AI | Muse Wonder | 161.7 ECI +/-2.5 | 8.00 |
| Moonshot | Kimi K3.1 Pro | 161.4 ECI +/-2.5 | 4.00 |
| DeepSeek | DeepSeek V4.1 Flash 1017 | 159.4 ECI +/-2.4 | 0.52 |
| xAI | Grok 4.6 | 157.8 ECI +/-2.1 | 3.00 |
| Alibaba | Qwen 3.8 Max | 157.6 ECI +/-2.2 | 3.00 |
| Z.ai (Zhipu AI) | GLM-5.3 | 157.1 ECI +/-2.1 | 2.15 |
| Mistral AI | Mistral Large 4 | 154.6 ECI +/-2.8 | 1.05 |
| Reflection | Beam 1.0 | 150.9 ECI +/-2.2 | 0.75 |
| Thinking Machines | Inkling-Small | 150.8 ECI +/-1.8 | 0.68 |

## Key benchmarks, top 5 each

### Writing and chat (human preference): `text_style_control/overall`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Gemini 4 Carbon (High) | 1527 Elo +/-10 | Google DeepMind | 4.00 |  |
| 2 | Gemini 4 Argon (High) | 1520 Elo +/-5 | Google DeepMind | 4.00 |  |
| 3 | Gemini 4 Neon (High) | 1513 Elo +/-9 | Google DeepMind | 6.00 |  |
| 4 | Muse Wonder (Max) | 1511 Elo +/-6 | Meta AI | 8.00 |  |
| 5 | Claude Opus 5.5 (High) | 1506 Elo +/-6 | Anthropic | 8.00 |  |

### Coding (human preference): `text_style_control/coding`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Gemini 4 Carbon (High) | 1568 Elo +/-19 | Google DeepMind | 4.00 |  |
| 2 | Gemini 4 Neon (High) | 1559 Elo +/-17 | Google DeepMind | 6.00 |  |
| 3 | Gemini 4 Argon (High) | 1552 Elo +/-9 | Google DeepMind | 4.00 |  |
| 4 | Claude Fable 5 (High) | 1551 Elo +/-6 | Anthropic | 20.00 |  |
| 5 | Claude Opus 4.7 (High) | 1551 Elo +/-6 | Anthropic | 10.00 |  |

### Hard prompts (human preference): `text_style_control/hard_prompts`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Gemini 4 Carbon (High) | 1547 Elo +/-12 | Google DeepMind | 4.00 |  |
| 2 | Gemini 4 Argon (High) | 1544 Elo +/-6 | Google DeepMind | 4.00 |  |
| 3 | Gemini 4 Neon (High) | 1542 Elo +/-11 | Google DeepMind | 6.00 |  |
| 4 | Muse Wonder (Max) | 1531 Elo +/-7 | Meta AI | 8.00 |  |
| 5 | Claude Opus 4.6 (High) | 1530 Elo +/-4 | Anthropic | 10.00 |  |

### Following instructions (human preference): `text_style_control/instruction_following`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Gemini 4 Argon (High) | 1526 Elo +/-7 | Google DeepMind | 4.00 |  |
| 2 | Gemini 4 Carbon (High) | 1525 Elo +/-16 | Google DeepMind | 4.00 |  |
| 3 | Gemini 4 Neon (High) | 1518 Elo +/-14 | Google DeepMind | 6.00 |  |
| 4 | Claude Opus 5.5 (High) | 1516 Elo +/-9 | Anthropic | 8.00 |  |
| 5 | Claude Opus 4.6 (High) | 1511 Elo +/-5 | Anthropic | 10.00 |  |

### Web UI (human preference): `webdev/webdev-react`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.2 (xHigh) | 1886 Elo +/-22 | Anthropic | 16.00 |  |
| 2 | Claude Opus 5.5 (Max) | 1871 Elo +/-14 | Anthropic | 8.00 |  |
| 3 | Claude Sonnet 5.5 (xHigh) | 1819 Elo +/-12 | Anthropic | 4.00 |  |
| 4 | Gemini 4 Carbon (High) | 1793 Elo +/-18 | Google DeepMind | 4.00 |  |
| 5 | Gemini 4 Neon (High) | 1787 Elo +/-17 | Google DeepMind | 6.00 |  |

### Reading images (human preference): `vision_style_control/ocr`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.2 (Max) | 1327 Elo +/-22 | Anthropic | 16.00 |  |
| 2 | Claude Fable 5 (High) | 1326 Elo +/-7 | Anthropic | 20.00 |  |
| 3 | Gemini 3.8 Flash (High) | 1315 Elo +/-8 | Google DeepMind | 1.50 |  |
| 4 | Claude Opus 4.7 | 1314 Elo +/-6 | Anthropic | 10.00 |  |
| 5 | Qwen3.8-Max | 1313 Elo +/-8 | Alibaba | 3.00 |  |

### Web search answers (human preference): `search/overall`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Amazon-Web-Search-Agent | 1266 Elo +/-15 | Amazon | n/a |  |
| 2 | Qwen3.8-Max | 1261 Elo +/-11 | Alibaba | 3.00 |  |
| 3 | GPT-5.6 Sol (xHigh) | 1256 Elo +/-6 | OpenAI | 8.00 |  |
| 4 | Claude Opus 4.6 (Search) | 1252 Elo +/-5 | Anthropic | 10.00 |  |
| 5 | GPT-5.5 (Search) | 1246 Elo +/-5 | OpenAI | 11.25 |  |

### Document questions (human preference): `document/overall`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.1 (Max) | 1515 Elo +/-15 | Anthropic | 20.00 |  |
| 2 | Claude Opus 5 (High) | 1509 Elo +/-6 | Anthropic | 10.00 |  |
| 3 | Claude Opus 4.6 (High) | 1508 Elo +/-6 | Anthropic | 10.00 |  |
| 4 | Claude Fable 5 (High) | 1497 Elo +/-7 | Anthropic | 20.00 |  |
| 5 | Claude Opus 4.7 (High) | 1496 Elo +/-6 | Anthropic | 10.00 |  |

### Science questions (correctness): `gpqa_diamond`

Near the ceiling: the top models are hard to tell apart on this benchmark.

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | GPT-6.2 Astra (max) | 96.8% +/-2.4 | OpenAI | 16.00 |  |
| 2 | Gemini 4 Hydrogen (High) (xhigh) | 96.8% +/-2.3 | Google DeepMind | 3.00 |  |
| 3 | Gemini 4 Carbon (high) | 96.5% +/-2.4 | Google DeepMind | 4.00 |  |
| 4 | Gemini 4 Argon (high) | 96.4% +/-2.3 | Google DeepMind | 4.00 |  |
| 5 | claude-fable-5-2-fallback_max | 96.0% +/-2.6 | - | n/a |  |

### Maths (correctness): `frontiermath_tiers_1_3_v2`

Near the ceiling: the top models are hard to tell apart on this benchmark.

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.2 (max) | 95.1% +/-2.5 | Anthropic | 16.00 |  |
| 2 | GPT-6 Astra (max) | 93.7% +/-2.8 | OpenAI | 20.00 |  |
| 3 | GPT-6.1 Sol (max) | 93.7% +/-2.8 | OpenAI | 4.00 |  |
| 4 | GPT-6.2 Astra (max) | 92.6% +/-3.0 | OpenAI | 16.00 |  |
| 5 | Claude Opus 5.5 (max) | 91.2% +/-3.3 | Anthropic | 8.00 |  |

### Competition maths (correctness): `otis_mock_aime_2024_2025`

Near the ceiling: the top models are hard to tell apart on this benchmark.

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.1 (max) | 100.0% | Anthropic | 20.00 |  |
| 2 | Claude Fable 5 (high) | 100.0% | Anthropic | 20.00 |  |
| 3 | Claude Opus 5.5 (max) | 100.0% | Anthropic | 8.00 |  |
| 4 | Claude Sonnet 5.5 (max) | 100.0% | Anthropic | 4.00 |  |
| 5 | Gemini 4 Argon (high) | 100.0% | Google DeepMind | 4.00 |  |

### Factual accuracy (correctness): `simpleqa_verified`

| # | Model | Score | Lab | Price $/M | Note |
|---|---|---|---|---|---|
| 1 | Claude Fable 5.2 (max) | 94.0% +/-1.5 | Anthropic | 16.00 |  |
| 2 | GPT-6.2 Astra (max) | 78.5% +/-2.5 | OpenAI | 16.00 |  |
| 3 | Gemini 4 Carbon (high) | 77.7% +/-2.6 | Google DeepMind | 4.00 |  |
| 4 | Gemini 4 Argon (high) | 76.0% +/-2.6 | Google DeepMind | 4.00 |  |
| 5 | GPT-6 Astra (max) | 75.6% +/-2.7 | OpenAI | 20.00 |  |

## All benchmarks (ask `python recommend.py <name> --top 20` for any of them)

- **arena:** document/overall, search/overall, text_style_control/chinese, text_style_control/coding, text_style_control/creative_writing, text_style_control/english, text_style_control/exclude_ties, text_style_control/expert, text_style_control/french, text_style_control/german, text_style_control/hard_prompts, text_style_control/hard_prompts_english, text_style_control/industry_business_and_management_and_financial_operations, text_style_control/industry_entertainment_and_sports_and_media, text_style_control/industry_legal_and_government, text_style_control/industry_life_and_physical_and_social_science, text_style_control/industry_mathematical, text_style_control/industry_medicine_and_healthcare, text_style_control/industry_software_and_it_services, text_style_control/industry_writing_and_literature_and_language, text_style_control/instruction_following, text_style_control/japanese, text_style_control/korean, text_style_control/longer_query, text_style_control/math, text_style_control/multi_turn, text_style_control/non_english, text_style_control/overall, text_style_control/polish, text_style_control/russian, text_style_control/spanish, vision_style_control/captioning, vision_style_control/chinese, vision_style_control/creative_writing_vision, vision_style_control/diagram, vision_style_control/english, vision_style_control/entity_recognition, vision_style_control/homework, vision_style_control/humor, vision_style_control/ocr, vision_style_control/overall, webdev/image_to_webdev, webdev/overall, webdev/webdev, webdev/webdev-html, webdev/webdev-react
- **epoch:** chess_puzzles, ebr_bench, eci, frontiermath_tier_4_v2, frontiermath_tiers_1_3_v2, furniture_assembly, gpqa_diamond, mirrorcode, mystery_game_puzzles, otis_mock_aime_2024_2025, simpleqa_verified, spireclimb
