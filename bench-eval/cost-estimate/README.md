# Cost estimate — model mixes at OpenRouter list prices (2026-09-06)

Programmatic evidence, no model runs: prices from OpenRouter model pages;
token volumes from real sessions (`bench-v2-out/smoke/sessions/`, hard-greenfield
SSE: arm A framework, arm B bare, plus a 1-turn preflight). Repro:
`py bench-eval/cost-estimate/estimate.py` (outputs `estimate-results.json`).

## Prices ($/1M tokens, OpenRouter, 2026-09-06)

| Model | Input | Output | Cache read | Notes |
|---|---|---|---|---|
| `z-ai/glm-5.3-flash` | 0.15 | 0.50 | 0.03 | 50% ZAI promo → 0.075/0.25 through 2026-09-09 |
| `z-ai/glm-5.3` | 1.17 | 3.96 | 0.234 | reasoning always on |
| `meta/muse-spark-1.3` | 1.25 | 4.25 | 0.15 | single provider (Meta) |
| `anthropic/claude-sonnet-5` | 2.00 | 10.00 | 0.20 | |
| `deepseek/deepseek-v4-flash-0731` | 0.045 | 0.09 | 0.009 | |
| `google/gemini-3.8-flash` | 0.75 | 3.75 | 0.075 | cache-write $0.04167 (1/18× input — cache-friendly); 50% promo → 0.375/1.875 |

Cache-write assumed 1.25× input (OpenRouter convention).

## Real token profiles (one hard-greenfield session)

| Profile | Turns | Input | Cache read | Output | List cost (all-flash) | fcc-server reported | **fcc inflation** |
|---|---|---|---|---|---|---|---|
| A (framework) | 86 | 281K | 3,986K | 67K | **$0.195** | $6.30 | **32×** |
| B (bare) | 59 | 118K | 2,484K | 40K | **$0.112** | $2.84 | **25×** |
| 1-turn preflight | 1 | 31K | 0.7K | 15 | $0.0046 | $0.153 | 33× |

**The fcc-server's reported costs are ~25–33× OpenRouter list** — its cost basis is
inflated/unverified (the GAP-ANALYSIS flag, now quantified). All earlier
"cost" figures quoted from fcc session JSONs ($2.84 / $6.30; the ~$90–100 full-suite
estimate) are on that basis; the **real OpenRouter cost of the same sessions was
~$0.11–0.20 each** and a 20-session N=5 full suite ≈ **$3** at list prices (≈$1.5
with the flash promo).

## Configurations — estimated $/session (fixed token volume, subagent share 30%)

| Config | A-arm session | B-arm session | vs all-flash |
|---|---|---|---|
| all glm-5.3-flash (list) | $0.195 | $0.112 | 1.0× |
| all glm-5.3-flash (50% promo) | $0.098 | $0.056 | 0.5× |
| all claude-sonnet-5 | $2.03 | $1.14 | 10.4× |
| main glm-5.3 + subs glm-flash | $1.13 | $0.65 | 5.8× |
| main glm-5.3 + subs deepseek-v4-flash | $1.08 | $0.63 | 5.6× |
| main muse-spark-1.3 + subs glm-flash | $0.92 | $0.52 | 4.7× |
| main muse-spark-1.3 + subs deepseek-v4-flash | $0.88 | $0.49 | 4.5× |
| all gemini-3.8-flash (list / promo) | $0.76 / $0.38 | $0.43 / $0.21 | 3.9× / 1.95× |
| main glm-5.3 + subs gemini-flash | $1.30 | $0.74 | 6.6× |
| main muse-spark-1.3 + subs gemini-flash | $1.09 | $0.61 | 5.6× |
| main gemini-flash + subs glm-flash | $0.59 | $0.33 | 3.0× |
| main gemini-flash + subs deepseek-v4-flash | $0.55 | $0.31 | 2.8× |

Sensitivity (subagent share 20/30/40%): main-tier mixes vary ±15%; all-flash and
all-sonnet are insensitive (single model). DeepSeek vs flash as subagent: ~4% apart.

## Interpretation

- All-flash is 5–10× cheaper than any top-tier main + cheap-sub mix at the same
  token volume; the 50% flash promo halves it.
- Gemini 3.8 Flash slots between: ~4× all-flash standalone (2× with its promo),
  and as a **main** with cheap subs it is the cheapest non-flash-leading team
  (~3× all-flash); as a **subagent** it costs more than flash/deepseek subs but
  less than raising the main's share. Its 1/18× cache-write makes it
  disproportionately cheap in long, cache-heavy sessions (our profiles are
  90%+ cache-read).
- The subagent model choice is nearly irrelevant to cost (flash vs deepseek ≈ 4%)
  because the main agent dominates spend in mixed configs.
- This is **price at fixed work** — real behavior differs (a stronger main model
  may need fewer turns; weaker models may stall or rework). Measuring that
  behavior difference is the benchmark's job; this table prices the workload.
- Cost is not the differentiator the benchmarks should optimize: even the
  priciest config is ~$2/session at this task size.
