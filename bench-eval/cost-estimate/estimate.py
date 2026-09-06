"""Cost estimator — model-mix configurations at OpenRouter list prices.

Programmatic evidence:
- prices: fetched from openrouter.ai model pages 2026-09-06 (see
  openrouter-pricing-2026-09-06.json + pages); cache_write assumed 1.25x prompt
  (OpenRouter convention) unless the provider publishes it.
- token profiles: real sessions from the bench-v2 smoke (B bare / A framework,
  hard-greenfield SSE) + a 1-turn preflight call.

Question: cost of the SAME workload under different model mixes —
  single glm-5.3-flash | single Sonnet-5 |
  main glm-5.3 or muse-spark-1.3, subagents glm-5.3-flash or deepseek-v4-flash-0731.
Fixed token volume per profile; subagent share is a parameter (default 30%,
sensitivity 20%/40%). This is price-at-fixed-work, not a model-behavior claim.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SMOKE = pathlib.Path(r"C:\Users\TracNguyen\Personal\BrainStorm\Research-Hub\asdlc-main-bench\bench-v2-out\smoke\sessions")

# --- prices ($/1M tokens), from OpenRouter pages 2026-09-06 ---
PRICES = {
    "glm-5.3-flash":        {"in": 0.15,  "out": 0.50,  "cache_read": 0.03,  "cache_write": 0.1875},  # write=1.25x
    "glm-5.3-flash-promo":  {"in": 0.075, "out": 0.25,  "cache_read": 0.015, "cache_write": 0.09375}, # 50% ZAI promo thru 2026-09-09
    "glm-5.3":              {"in": 1.17,  "out": 3.96,  "cache_read": 0.234, "cache_write": 1.4625},
    "muse-spark-1.3":       {"in": 1.25,  "out": 4.25,  "cache_read": 0.15,  "cache_write": 1.5625},
    "claude-sonnet-5":      {"in": 2.00,  "out": 10.00, "cache_read": 0.20,  "cache_write": 2.50},
    "deepseek-v4-flash-0731": {"in": 0.045, "out": 0.09, "cache_read": 0.009, "cache_write": 0.05625},
    "gemini-3.8-flash":        {"in": 0.75,  "out": 3.75,  "cache_read": 0.075,  "cache_write": 0.04167},  # Google cache-write = 1/18x input
    "gemini-3.8-flash-promo":  {"in": 0.375, "out": 1.875, "cache_read": 0.0375, "cache_write": 0.02083}, # 50% off
}

# --- Reasoning-effort model (methodology in README §"Reasoning effort") ---
# OpenRouter bills every output token at the completion rate — reasoning effort
# changes OUTPUT VOLUME (thinking tokens), not the rate. `share` = thinking
# tokens emitted per 1 answer token. Defaults are the model's default effort;
# levels cover selectable efforts where documented.
REASONING = {
    "glm-5.3-flash":       {"default": 0.15, "levels": {"low": 0.10, "high": 0.30}},
    "deepseek-v4-flash-0731": {"default": 0.10, "levels": {}},
    "gemini-3.8-flash":    {"default": 0.25, "levels": {"low": 0.15, "high": 0.50}},
    "muse-spark-1.3":      {"default": 0.75, "levels": {"low": 0.40, "high": 1.00}},
    "glm-5.3":             {"default": 1.25, "levels": {"low": 0.40, "medium": 0.70, "high": 0.80, "max": 1.25}},  # reasoning always on, max default
    "claude-sonnet-5":     {"default": 0.80, "levels": {"low": 0.15, "medium": 0.40, "high": 0.80, "max": 1.50, "x-high": 2.50}},  # adaptive thinking
}

def output_multiplier(model: str, effort: str | None = None) -> float:
    """1 + thinking-share → output-token multiplier at the given effort."""
    r = REASONING.get(model, {"default": 0.15, "levels": {}})
    share = r["levels"].get(effort, r["default"]) if effort else r["default"]
    return 1.0 + share

def session_cost(tokens: dict, model: str, effort: str | None = None, share: float | None = None) -> float:
    p = PRICES[model]
    mult = (1.0 + share) if share is not None else output_multiplier(model, effort)
    return (
        tokens["input"] * p["in"]
        + tokens["cache_creation"] * p["cache_write"]
        + tokens["cache_read"] * p["cache_read"]
        + tokens["output"] * mult * p["out"]
    ) / 1e6

def load_profile(path: pathlib.Path):
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    idx = raw.find('{"is_error"')
    j = json.loads(raw[idx:]) if idx >= 0 else json.loads(raw)
    if "usage" not in j and "num_turns" not in j:
        return None  # not a session file (e.g. manifest.json)
    u = j.get("usage") or {}
    return {
        "name": path.stem,
        "turns": j.get("num_turns"),
        "input": u.get("input_tokens") or 0,
        "cache_creation": u.get("cache_creation_input_tokens") or 0,
        "cache_read": u.get("cache_read_input_tokens") or 0,
        "output": u.get("output_tokens") or 0,
        "fcc_reported_cost": j.get("total_cost_usd"),
    }

def main():
    profiles = []
    for f in sorted(SMOKE.glob("*.json")):
        p = load_profile(f)
        if p is not None:
            profiles.append(p)
    # preflight 1-turn profile (constant ~30K in)
    profiles.append({
        "name": "preflight-1turn", "turns": 1,
        "input": 30606, "cache_creation": 0, "cache_read": 704, "output": 15,
        "fcc_reported_cost": 0.1531,
    })

    # configuration matrix: main model / subagent model
    CONFIGS = [
        ("all glm-5.3-flash (list)",        "glm-5.3-flash", "glm-5.3-flash"),
        ("all glm-5.3-flash (50% promo)",   "glm-5.3-flash-promo", "glm-5.3-flash-promo"),
        ("all claude-sonnet-5",             "claude-sonnet-5", "claude-sonnet-5"),
        ("main glm-5.3 + subs glm-flash",   "glm-5.3", "glm-5.3-flash"),
        ("main glm-5.3 + subs deepseek-v4", "glm-5.3", "deepseek-v4-flash-0731"),
        ("main muse-spark-1.3 + subs glm-flash", "muse-spark-1.3", "glm-5.3-flash"),
        ("main muse-spark-1.3 + subs deepseek-v4", "muse-spark-1.3", "deepseek-v4-flash-0731"),
        ("all gemini-3.8-flash (list)",         "gemini-3.8-flash", "gemini-3.8-flash"),
        ("all gemini-3.8-flash (50% promo)",    "gemini-3.8-flash-promo", "gemini-3.8-flash-promo"),
        ("main glm-5.3 + subs gemini-flash",    "glm-5.3", "gemini-3.8-flash"),
        ("main muse-spark + subs gemini-flash", "muse-spark-1.3", "gemini-3.8-flash"),
        ("main gemini-flash + subs glm-flash",  "gemini-3.8-flash", "glm-5.3-flash"),
        ("main gemini-flash + subs deepseek-v4", "gemini-3.8-flash", "deepseek-v4-flash-0731"),
    ]
    SUB_SHARE = 0.30  # default subagent share of tokens; sensitivity 0.20 / 0.40

    print(f"{'profile':26s} {'turns':>5s} {'in_k':>7s} {'out_k':>6s} {'cache_r_k':>9s} {'fcc$':>7s} {'list$ all-flash':>15s} {'ratio fcc/list':>13s}")
    for p in profiles:
        t = {k: p[k] for k in ("input", "cache_creation", "cache_read", "output")}
        list_cost = session_cost(t, "glm-5.3-flash", effort="low")  # flash default ≈ low reasoning
        fcc = p["fcc_reported_cost"]
        print(f"{p['name']:26s} {p['turns']:5d} {p['input']/1000:7.1f} {p['output']/1000:6.1f} {p['cache_read']/1000:9.1f} {fcc:7.2f} {list_cost:15.4f} {fcc/list_cost if list_cost else float('nan'):13.1f}x")

    print("\nEstimated $/session at OpenRouter list prices, DEFAULT reasoning effort (subagent share = 30%):")
    hdr = f"{'config':38s} " + " ".join(f"{p['name'][:14]:>15s}" for p in profiles)
    print(hdr)
    results = {}
    for label, main_m, sub_m in CONFIGS:
        row = []
        for p in profiles:
            t = {k: p[k] for k in ("input", "cache_creation", "cache_read", "output")}
            main_tok = {k: v * (1 - SUB_SHARE) for k, v in t.items()}
            sub_tok = {k: v * SUB_SHARE for k, v in t.items()}
            cost = session_cost(main_tok, main_m) + session_cost(sub_tok, sub_m)
            row.append(cost)
            results.setdefault(label, []).append(cost)
        print(f"{label:38s} " + " ".join(f"{c:15.3f}" for c in row))

    # reasoning-effort scenarios (A-arm profile) — models with documented effort controls
    print("\nReasoning-effort scenarios — A-arm profile, $/session and uplift vs that model's no-reasoning cost:")
    a = profiles[0]
    t = {k: a[k] for k in ("input", "cache_creation", "cache_read", "output")}
    base_flash = session_cost(t, "glm-5.3-flash", effort="low")
    for model, levels in [("claude-sonnet-5", ["low", "medium", "high", "max", "x-high"]),
                          ("glm-5.3", ["low", "medium", "high", "max"]),
                          ("gemini-3.8-flash", ["low", None, "high"]),
                          ("muse-spark-1.3", ["low", None, "high"]),
                          ("glm-5.3-flash", ["low", None, "high"]),
                          ("deepseek-v4-flash-0731", [None])]:
        for eff in levels:
            share = REASONING[model]["levels"].get(eff, REASONING[model]["default"]) if eff else REASONING[model]["default"]
            c = session_cost(t, model, effort=eff)
            c0 = session_cost(t, model, share=0.0)  # true no-reasoning baseline
            label_eff = eff if eff else "default"
            print(f"  {model:24s} {label_eff:7s} share={share:4.2f}  ${c:6.3f}  vs-no-reasoning {c / c0:5.2f}x  vs-all-flash {c / base_flash:5.2f}x")

    out = {"prices": PRICES, "reasoning": REASONING, "profiles": profiles, "configs": results}
    (ROOT / "estimate-results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nsaved:", ROOT / "estimate-results.json")

if __name__ == "__main__":
    main()
