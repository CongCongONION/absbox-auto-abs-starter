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


def bisect_first_loss(api, deal, tranche, lo, hi, tol=0.005):
    """Bracket [lo, hi] (width <= tol) around the smallest multiplier at
    which `tranche` first loses principal: at lo the tranche is whole,
    at hi it has a (small) loss. Returns (lo, hi) or None."""
    if run_at(api, deal, lo)[1][tranche] > 0.01:
        return (lo, lo)
    if run_at(api, deal, hi)[1][tranche] <= 0.01:
        return None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if run_at(api, deal, mid)[1][tranche] > 0.01:
            hi = mid
        else:
            lo = mid
    return (lo, hi)


def main():
    api = API("http://localhost:8081", "english")
    deal = build_deal()
    lines = ["# Break-even CNL (CDR multiplier on base segment CDRs; "
             "CPR / recovery / lag at base)", "",
             "Bisection tolerance 0.005x on the multiplier. Each tranche "
             "reports a BRACKET: at the lower bound the tranche is still "
             "whole, at the upper bound it has its first (small) loss; "
             "the break-even CNL lies between the two CNL values.", ""]
    m_e = bisect_first_loss(api, deal, "E", 1.0, 12.0)
    m_b = bisect_first_loss(api, deal, "B", m_e[0] if m_e else 1.0, 20.0)
    for tranche, bracket in [("E", m_e), ("B", m_b)]:
        if bracket is None:
            lines.append(f"- Class {tranche}: no principal loss found in "
                         "the searched range.")
            continue
        lo, hi = bracket
        cnl_lo, losses_lo = run_at(api, deal, lo)
        cnl_hi, losses_hi = run_at(api, deal, hi)
        lines.append(
            f"- Class {tranche}: break-even CDR multiplier in "
            f"[{lo:.3f}x, {hi:.3f}x]; break-even CNL in "
            f"[${cnl_lo:,.0f} ({cnl_lo / 1e8:.2%}), "
            f"${cnl_hi:,.0f} ({cnl_hi / 1e8:.2%})] of the pool "
            f"(loss at lower bound ${losses_lo[tranche]:,.0f}; "
            f"at upper bound ${losses_hi[tranche]:,.0f})")
        print(lines[-1])
    with open(os.path.join(OUT, "breakeven.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote outputs/breakeven.md")


if __name__ == "__main__":
    main()
