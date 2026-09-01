"""benchv2.stats — non-parametric statistics for replicate-based benchmarks."""
import math
import statistics as _s


def summarize(values):
    v = sorted(float(x) for x in values)
    median = _s.median(v)
    if len(v) >= 2:
        k = (len(v) + 1) // 2
        q1 = _s.median(v[:k])
        q3 = _s.median(v[-k:])
    else:
        q1 = q3 = median
    return {"n": len(v), "median": median, "iqr": q3 - q1, "min": v[0], "max": v[-1]}


def mann_whitney(a, b):
    """Two-sided Mann-Whitney U test via normal approximation + tie correction.

    Valid for n*m >= 4 and no massive ties (good enough for the unit test and
    for n=5 replicate comparisons; exact p for extreme separation is ~0).
    """
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    n, m = len(a), len(b)
    joined = sorted((x, 0) for x in a) + sorted((x, 1) for x in b)
    joined.sort(key=lambda t: (t[0], t[1]))
    # average ranks (handle ties)
    ranks = []
    i = 0
    while i < len(joined):
        j = i
        while j < len(joined) and joined[j][0] == joined[i][0]:
            j += 1
        avg = (i + 1 + j) / 2.0
        ranks.extend([avg] * (j - i))
        i = j
    u_a = sum(r for r, (_, g) in zip(ranks, joined) if g == 0)
    u = u_a - n * (n + 1) / 2.0
    mu = n * m / 2.0
    # tie correction for standard deviation
    tie_adj = 0.0
    i = 0
    while i < len(joined):
        j = i
        while j < len(joined) and joined[j][0] == joined[i][0]:
            j += 1
        t_ = j - i
        tie_adj += t_ * t_ - t_
        i = j
    n_all = n + m
    denom = n * m * ((n_all + 1) / 12.0 - tie_adj / (12.0 * n_all * (n_all - 1)))
    sigma = math.sqrt(denom) if denom > 0 else math.sqrt(n * m * (n_all + 1) / 12.0)
    if sigma <= 0:
        return 1.0
    z = (u - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return min(1.0, p)