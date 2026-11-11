"""
Bond yield (IRR at par) for each tranche / scenario.

Reads the engine-generated bond cashflow CSVs in ../outputs/ and solves
for the monthly internal rate of return of buying the tranche at par
(origin balance) at closing (2026-01-15) and holding it to maturity:

    -par + sum_t  cash_t / (1 + r_m)^t  = 0      (t = payment number, monthly)

Reports the effective annual yield (1 + r_m)^12 - 1.
For the equity tranche E, `cash` includes residual (excess-spread)
distributions, so its yield is the equity IRR, not a coupon yield.

    python src/pricing.py     ->  ../outputs/yield_summary.csv
"""

import os
import pandas as pd
from scipy.optimize import brentq

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
SCENARIOS = ["base", "optimistic", "stress"]


def yield_at_par(cash: pd.Series, par: float):
    cf = cash.fillna(0.0).to_numpy()
    t = range(1, len(cf) + 1)

    def npv(r):
        return -par + sum(c / (1 + r) ** i for c, i in zip(cf, t))

    try:
        r_m = brentq(npv, -0.9999, 5.0, maxiter=500)
        return (1 + r_m) ** 12 - 1, r_m * 12
    except ValueError:
        return float("nan"), float("nan")


def main():
    rows = []
    for scen in SCENARIOS:
        for tranche, par in PAR.items():
            flow = pd.read_csv(os.path.join(BASE, f"bond_{tranche}_flow_{scen}.csv"))
            y_eff, y_nom = yield_at_par(flow["cash"], par)
            rows.append({
                "scenario": scen,
                "tranche": tranche,
                "par": par,
                "total_cash": round(float(flow["cash"].fillna(0).sum()), 2),
                "yield_effective_annual_pct": round(100 * y_eff, 3),
                "yield_nominal_annual_pct": round(100 * y_nom, 3),
            })
            print(scen, tranche, f"eff yield = {100 * y_eff:.3f}%")
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(BASE, "yield_summary.csv"), index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
