"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    tp = sum(1 for h, j in zip(human, judge) if h == POS and j == POS)
    fp = sum(1 for h, j in zip(human, judge) if h != POS and j == POS)
    fn = sum(1 for h, j in zip(human, judge) if h == POS and j != POS)
    tn = sum(1 for h, j in zip(human, judge) if h != POS and j != POS)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    # precision = tp/(tp+fp), recall = tp/(tp+fn); return 0.0 when the denominator is 0
    c = confusion(human, judge)
    precision = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) > 0 else 0.0
    recall = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) > 0 else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    n = len(human)
    if n == 0:
        raise ValueError("empty sequences")
    c = confusion(human, judge)
    p_o = (c["tp"] + c["tn"]) / n
    p_pos = ((c["tp"] + c["fp"]) / n) * ((c["tp"] + c["fn"]) / n)
    p_neg = ((c["tn"] + c["fn"]) / n) * ((c["tn"] + c["fp"]) / n)
    p_e = p_pos + p_neg
    if p_e == 1.0:
        raise ValueError("p_e == 1: constant judge has no signal")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    # (p_obs + spec - 1) / (sens + spec - 1)
    denom = sensitivity + specificity - 1
    if denom == 0:
        return max(0.0, min(1.0, observed_rate))
    corrected = (observed_rate + specificity - 1) / denom
    return max(0.0, min(1.0, corrected))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy import stats as scipy_stats

    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    if np.array_equal(a_arr, b_arr):
        return (0.0, 0.0, 0.0)
    diff = float(np.mean(a_arr) - np.mean(b_arr))

    def stat(x, y):
        return np.mean(x - y)

    res = scipy_stats.bootstrap(
        (a_arr, b_arr),
        statistic=stat,
        paired=True,
        n_resamples=n_resamples,
        method="percentile",
        random_state=np.random.default_rng(rng),
        confidence_level=confidence,
    )
    lo = float(res.confidence_interval.low)
    hi = float(res.confidence_interval.high)
    return diff, lo, hi


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    from math import comb
    if k > n:
        raise ValueError(f"k={k} > n={n}")
    if c == 0:
        return 0.0
    cn_k = comb(n, k)
    if cn_k == 0:
        return 1.0
    return 1.0 - comb(n - c, k) / cn_k


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    from math import comb
    if k > n:
        raise ValueError(f"k={k} > n={n}")
    cn_k = comb(n, k)
    if cn_k == 0:
        return 0.0
    return comb(c, k) / cn_k
