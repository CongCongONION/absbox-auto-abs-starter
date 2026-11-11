"""
Break-even cumulative net loss (Break-even CNL) — rating-style stress test.

Scales the BASE scenario's segment CDRs by a multiplier m (CPR, recovery
and lag held at base) and finds, by bisection, the multiplier at which a
tranche first takes a principal loss:

    m*_E : Class E principal loss first > 0
    m*_B : Class B principal loss first > 0   (searched above m*_E)

The pool cumulative net loss at that multiplier is the tranche's
break-even CNL — the standard way rating agencies express how much
collateral loss a tranche can withstand (cf. S&P presale reports, which
quote break-even / stress CNL levels per tranche).

    python src/breakeven.py   ->  ../outputs/breakeven.md
"""

import os
import pandas as pd
from absbox import API
from auto_abs_deal import build_deal, _perf, SEGMENTS, SEGMENT_ASSUMPS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
BASE = SEGMENT_ASSUMPS["base"]


def scaled_assump(mult: float):
    return ("ByPoolId", {
        name: ("Pool", _perf(min(BASE[name][0] * mult, 0.95),
                             BASE[name][1], BASE[name][2], BASE[name][3]),
               None, None)
        for name, *_ in SEGMENTS})


def run_at(api, deal, mult: float):
    r = api.run(deal, poolAssump=scaled_assump(mult),
                read=True, showWarning=False)
    cum_loss = sum(float(f["CumLoss"].iloc[-1])
                   for f in r["pool"]["flow"].values())
    losses = {tr: par - float(r["bonds"][tr]["principal"].fillna(0).sum())
              for tr, par in PAR.items()}
    return cum_loss, losses


def bisect_first_loss(api, deal, tranche, lo, hi, tol=0.02):
    """Smallest multiplier in [lo, hi] where `tranche` loses principal."""
    if run_at(api, deal, lo)[1][tranche] > 0.01:
        return lo
    if run_at(api, deal, hi)[1][tranche] <= 0.01:
        return None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if run_at(api, deal, mid)[1][tranche] > 0.01:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    api = API("http://localhost:8081", "english")
    deal = build_deal()
    lines = ["# Break-even CNL (CDR multiplier on base segment CDRs; "
             "CPR / recovery / lag at base)", ""]
    results = {}
    m_e = bisect_first_loss(api, deal, "E", 1.0, 12.0)
    results["E"] = m_e
    m_b = bisect_first_loss(api, deal, "B", m_e or 1.0, 20.0) if m_e else None
    results["B"] = m_b
    for tranche, m in results.items():
        if m is None:
            lines.append(f"- Class {tranche}: no principal loss found in "
                         "the searched range.")
            continue
        cnl, losses = run_at(api, deal, m)
        lines.append(f"- Class {tranche} first principal loss at CDR "
                     f"multiplier ≈ {m:.2f}x base "
                     f"(CNL at that point ${cnl:,.0f}, "
                     f"{cnl / 100_000_000:.2%} of the pool; tranche loss "
                     f"${losses[tranche]:,.0f})")
        print(lines[-1])
    with open(os.path.join(OUT, "breakeven.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote outputs/breakeven.md")


if __name__ == "__main__":
    main()
