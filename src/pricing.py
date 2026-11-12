"""
Tranche yield at par — XIRR on actual cash-flow dates (v2).

Reads the engine-generated bond cashflow CSVs in ../outputs/ and solves
for the XIRR of buying the tranche at par (origin balance) at closing
(2026-01-15) and holding it to maturity, discounting on ACTUAL dates
(year fraction = days/365) instead of assuming equal monthly periods:

    -par + sum_i  cash_i / (1 + r)^((date_i - closing).days / 365)  = 0

For the equity tranche E, `cash` includes residual (excess-spread)
distributions, so its XIRR is the equity IRR, not a coupon yield.

    python src/pricing.py     ->  ../outputs/yield_summary.csv
"""

import os
import pandas as pd
from scipy.optimize import brentq

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
CLOSING = pd.Timestamp("2026-01-15")
SCENARIOS = ["base", "optimistic", "stress"]


def xirr(dates: pd.Series, cash: pd.Series, par: float) -> float:
    t = ((pd.to_datetime(dates) - CLOSING).dt.days / 365.0).to_numpy()
    cf = cash.fillna(0.0).to_numpy()

    def npv(r):
        return -par + float((cf / (1 + r) ** t).sum())

    return brentq(npv, -0.9999, 100.0, maxiter=500)


def main():
    rows = []
    price_rows = []
    for scen in SCENARIOS:
        for tranche, par in PAR.items():
            flow = pd.read_csv(os.path.join(BASE, f"bond_{tranche}_flow_{scen}.csv"))
            y = xirr(flow["date"], flow["cash"], par)
            rows.append({
                "scenario": scen, "tranche": tranche, "par": par,
                "total_cash": round(float(flow["cash"].fillna(0).sum()), 2),
                "xirr_pct": round(100 * y, 3),
            })
            print(scen, tranche, f"XIRR at par = {100 * y:.3f}%")
            # yield at purchase prices 95 / 100 / 105 (% of par)
            for price in (95.0, 100.0, 105.0):
                yp = xirr(flow["date"], flow["cash"], par * price / 100.0)
                price_rows.append({
                    "scenario": scen, "tranche": tranche,
                    "price_pct_of_par": price,
                    "yield_xirr_pct": round(100 * yp, 3),
                })
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(BASE, "yield_summary.csv"), index=False)
    prices = pd.DataFrame(price_rows)
    prices.to_csv(os.path.join(BASE, "price_yield.csv"), index=False)
    print(prices.pivot_table(index=["scenario", "tranche"],
                             columns="price_pct_of_par",
                             values="yield_xirr_pct").to_string())
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
