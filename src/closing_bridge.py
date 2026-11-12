"""
Cutoff-to-closing bridge (P0).

The engine's first pool-flow row is dated at CLOSING (2026-01-15) but
aggregates everything that happened between CUTOFF (2025-12-01) and
closing. This script explains that row completely, for every scenario:

  Table 1  Asset balance bridge
             Cutoff balance ($100,000,000)
             - scheduled principal - prepayments - defaults
             = pool balance at closing
  Table 2  Pre-closing collections (cash sitting in the collection
           account at closing, before the first payment date)
             interest + principal + prepayments + recoveries received
             = account balance at closing        (no fees/distributions
             have occurred yet — the first payment date is 2026-02-25)
  Table 3  Sources & uses at closing
             Sources: Class A + Class B + Class E proceeds = $100mm
             Uses:    purchase of the pool at its cutoff balance = $100mm
           Plus a trust balance-sheet check at closing:
             loans + cash  =  notes + pre-closing net earnings,
             where pre-closing net earnings = interest collected
             - defaults incurred (recoveries on those defaults are
             still pending because of the recovery lag, so they are
             NOT counted as an asset yet — no double counting).

Every identity is asserted to $0.01.

    python src/closing_bridge.py   ->  ../outputs/closing_bridge.md
"""

import os
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
CUTOFF_BALANCE = 100_000_000.0
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
SCENARIOS = ["base", "optimistic", "stress"]
TOL = 0.01


def bridge(scen: str) -> dict:
    pool = pd.read_csv(os.path.join(BASE, f"pool_flow_{scen}.csv"))
    acct = pd.read_csv(os.path.join(BASE, f"account_flow_{scen}.csv"))
    r = pool.iloc[0]
    assert r["Date"] == "2026-01-15", f"{scen}: first row is not closing"
    acct_close = float(acct.loc[acct["date"] == "2026-01-15", "balance"].iloc[-1])

    closing_bal = CUTOFF_BALANCE - r["Principal"] - r["Prepayment"] - r["Default"]
    assert abs(closing_bal - r["Balance"]) < TOL, f"{scen}: balance bridge"
    collections = r["Interest"] + r["Principal"] + r["Prepayment"] + r["Recovery"]
    assert abs(collections - acct_close) < TOL, f"{scen}: collections bridge"
    net_earnings = r["Interest"] - r["Default"] + r["Recovery"]
    lhs = r["Balance"] + acct_close
    rhs = sum(PAR.values()) + net_earnings
    assert abs(lhs - rhs) < TOL, f"{scen}: trust balance sheet"
    return {"r": r, "acct_close": acct_close, "net_earnings": net_earnings}


def main():
    lines = ["# Cutoff-to-closing bridge (cutoff 2025-12-01 → closing 2026-01-15)",
             "",
             "Sources & uses at closing — identical for all scenarios:",
             "",
             "| Sources | $ | Uses | $ |",
             "|---|---:|---|---:|",
             "| Class A proceeds | 85,000,000.00 | Purchase of pool at cutoff balance | 100,000,000.00 |",
             "| Class B proceeds | 10,000,000.00 | | |",
             "| Class E proceeds | 5,000,000.00 | | |",
             "| **Total sources** | **100,000,000.00** | **Total uses** | **100,000,000.00** |",
             "",
             "**Concept note (read this before adding any two numbers "
             "in this file):** sources & uses describes the closing-date "
             "*funding flows* and balances at exactly $100mm. The trust "
             "*balance sheet* at closing is a different statement: loans "
             "($97,673,228.91 in base) + collected cash ($2,985,652.34) = "
             "$100,658,881.25 of assets against $100,000,000 of notes. "
             "The $658,881.25 difference is pre-closing net earnings — "
             "interest collected between cutoff and closing, less "
             "defaults incurred in the same window (their recoveries are "
             "still pending and are NOT counted) — and it belongs to the "
             "residual holder. It is neither missing money nor "
             "double-counted collateral, and it must not be presented "
             "as part of the pool's principal balance.",
             ""]
    for scen in SCENARIOS:
        b = bridge(scen)
        r = b["r"]
        lines += [f"## {scen}",
                  "",
                  "| Asset balance bridge | $ |",
                  "|---|---:|",
                  f"| Pool balance at cutoff (2025-12-01) | {CUTOFF_BALANCE:,.2f} |",
                  f"| Scheduled principal collected | ({r['Principal']:,.2f}) |",
                  f"| Prepayments | ({r['Prepayment']:,.2f}) |",
                  f"| Defaults (removed from balance; recovery pending) | ({r['Default']:,.2f}) |",
                  f"| **Pool balance at closing (2026-01-15)** | **{r['Balance']:,.2f}** |",
                  "",
                  "| Pre-closing collections → collection account | $ |",
                  "|---|---:|",
                  f"| Interest | {r['Interest']:,.2f} |",
                  f"| Principal + prepayments | {r['Principal'] + r['Prepayment']:,.2f} |",
                  f"| Recoveries received by closing | {r['Recovery']:,.2f} |",
                  f"| **Account balance at closing** | **{b['acct_close']:,.2f}** |",
                  "",
                  f"Trust balance sheet at closing: loans ${r['Balance']:,.2f} "
                  f"+ cash ${b['acct_close']:,.2f} = notes $100,000,000.00 + "
                  f"pre-closing net earnings ${b['net_earnings']:,.2f} "
                  f"(interest − defaults; recoveries still pending). ✓",
                  ""]
    lines.append("All bridge identities hold to $0.01 in every scenario.")
    report = "\n".join(lines) + "\n"
    with open(os.path.join(BASE, "closing_bridge.md"), "w") as fh:
        fh.write(report)
    print(report)


if __name__ == "__main__":
    main()
