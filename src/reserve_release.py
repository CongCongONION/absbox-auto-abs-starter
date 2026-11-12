"""
Quantify the one loose end of deal v3: the reserve balance that stays
in reserveAcc at stated maturity in the Accelerated state.

Observed engine behaviour (documented in the README): once the deal
accelerates, the reserve target stops stepping down, so in v3 stress
$631,111.45 remains in the reserve account at the final distribution
date. In a real deal that cash is released at legal final maturity —
to the residual holder, after all notes are repaid. This script
measures what that treatment is worth: Class E cash flows from
outputs_v3 with and without a terminal release of the reserve
remainder on the final payment date. Classes A and B are fully repaid
in both treatments, so they are unaffected.

    python src/reserve_release.py -> ../reports/reserve_release_analysis.md
"""

import os
import pandas as pd
from pricing import xirr

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
E_PAR_V3 = 6_000_000.0


def main():
    flow = pd.read_csv(os.path.join(
        BASE, "outputs_v3", "bond_E_flow_stress.csv"))
    reserve = pd.read_csv(os.path.join(
        BASE, "outputs_v3", "account_reserveAcc_stress.csv"))
    remainder = float(reserve["balance"].iloc[-1])
    final_date = flow["date"].iloc[-1]
    as_modelled = xirr(flow["date"], flow["cash"], E_PAR_V3)
    adj = flow.copy()
    adj.loc[adj.index[-1], "cash"] = adj.loc[adj.index[-1], "cash"] + remainder
    released = xirr(adj["date"], adj["cash"], E_PAR_V3)
    total = float(flow["cash"].fillna(0).sum())
    lines = [
        "# Reserve remainder at maturity — release analysis (v3, stress)",
        "",
        f"In the v3 stress run the CNL trigger fires (2027-02-28) and "
        f"the reserve target stops stepping down in the Accelerated "
        f"state, leaving **${remainder:,.2f}** in the reserve account "
        f"at the final distribution date ({final_date}). The v3 outputs "
        f"conservatively leave it there. In an actual transaction the "
        f"reserve remainder is released at legal final maturity to the "
        f"residual holder once the notes are repaid — and in this run "
        f"Classes A and B are repaid in full, so the release belongs "
        f"entirely to Class E:",
        "",
        "| Class E (v3 stress) | As modelled | With legal-final release |",
        "|---|---:|---:|",
        f"| Total cash | ${total:,.2f} | ${total + remainder:,.2f} |",
        f"| XIRR (on $6.0mm par) | {100 * as_modelled:.2f}% | "
        f"{100 * released:.2f}% |",
        "",
        f"Effect: +${remainder:,.2f} of cash "
        f"(+{100 * remainder / total:.1f}% of E's total distributions) "
        f"and +{100 * (released - as_modelled):.2f} pts of XIRR. No "
        f"effect on Classes A or B, on the trigger date, or on any "
        f"break-even result. The as-modelled (conservative) treatment "
        f"is retained in all headline outputs; this note exists so the "
        f"size of the simplification is on the record.",
    ]
    with open(os.path.join(BASE, "reports", "reserve_release_analysis.md"),
              "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(lines[3])
    print(f"E XIRR {100 * as_modelled:.2f}% -> {100 * released:.2f}%")


if __name__ == "__main__":
    main()
