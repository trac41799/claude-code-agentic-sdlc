"""benchv2.score — guardrail conformance + process scoring from session JSON."""
import re


def _git(repo) -> None:
    """noop placeholder for git smoke; real conformance uses changed-file sets."""


def conformance_simple(planned_scopes: dict, changed: set) -> dict:
    """Plan-vs-PR conformance: every changed file must be planned.

    planned_scopes: {task: set of files (or dir prefixes ending with '/')}.
    """
    allowed = set()
    for v in planned_scopes.values():
        allowed |= set(v)

    def ok(f):
        if f in allowed:
            return True
        return any(f.startswith(p) for p in allowed if p.endswith("/"))

    bad = {f for f in changed if not ok(f)}
    return {"conform": not bad, "violations": bad}


def fragile_violations(session_extra: dict) -> int:
    return int(session_extra.get("fragile_violations", 0) or 0)


def process_metrics(session: dict, wall_min: float) -> dict:
    def m(k, d=0):
        return int(session.get(k, d) or 0)
    return {
        "terminal": session.get("terminal_reason"),
        "is_error": bool(session.get("is_error")),
        "errors": len(session.get("errors") or []),
        "turns": m("num_turns"),
        "spawned": (session.get("subagent_stats") or {}).get("spawned", 0),
        "sub_failed": (session.get("subagent_stats") or {}).get("failed", 0),
        "compute_min": round(m("duration_ms") / 60000, 1),
        "wall_min": round(wall_min, 1),
    }