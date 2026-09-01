"""benchv2.costs — token-volume extraction + verifiable cost-basis tagging."""
import json

KNOWN_BASIS = {"openai", "anthropic", "deepseek", "openrouter_list", "official_pricing"}


def breakdown(session: dict) -> dict:
    u = session.get("usage") or {}
    basis = "unknown"
    for mu in (session.get("modelUsage") or {}).values():
        if isinstance(mu, dict) and mu.get("costBasis"):
            basis = mu["costBasis"]
    out = {
        "in": u.get("input_tokens", 0),
        "out": u.get("output_tokens", 0),
        "cache_read": u.get("cache_read_input_tokens", 0) or u.get("cache_read_input_tokens_actual", 0),
        "basis": basis,
    }
    out["cents_k"] = "unverified" if basis not in KNOWN_BASIS else "provider-priced"
    return out


def sheet(runs: list[dict]) -> list[dict]:
    rows = []
    for r in runs:
        b = r.get("cost_breakdown") or {}
        rows.append({
            "case": r["case"], "arm": r["arm"], "rep": r["rep"],
            "in_tok": b.get("in"), "out_tok": b.get("out"),
            "cache_read": b.get("cache_read"),
            "basis": b.get("basis"), "cents_k": b.get("cents_k"),
            "est_usd_claimed": r.get("cost"),
        })
    return rows