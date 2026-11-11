"""
Sensitivity grid: uniform CDR x CPR -> tranche outcomes.

    python src/sensitivity.py

Output: ../outputs/sensitivity_grid.csv
Each cell runs the full deal through the Hastructure engine.
Uniform pool-level assumptions (recovery 35%, lag 4 months) are used so
the grid stays comparable across cells and with the v1 grid; the three
headline scenarios in run_scenarios.py use segment-level assumptions.
"""

import os
import pandas as pd
from absbox import API
from auto_abs_deal import build_deal, uniform_assump

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}


def main():
    api = API("http://localhost:8081", "english")
    deal = build_deal()
    rows = []
    for cdr in [0.005, 0.015, 0.03, 0.05]:
        for cpr in [0.03, 0.08, 0.15]:
            r = api.run(deal, poolAssump=uniform_assump(cdr, cpr),
                        read=True, showWarning=False)
            pool_loss = sum(float(f["CumLoss"].iloc[-1])
                            for f in r["pool"]["flow"].values())
            row = {"cdr": cdr, "cpr": cpr,
                   "pool_cum_loss": round(pool_loss, 2)}
            for tranche, par in PAR.items():
                flow = r["bonds"][tranche]
                paid = float(flow["principal"].fillna(0).sum())
                row[f"{tranche}_principal_loss"] = round(par - paid, 2)
                row[f"{tranche}_interest"] = round(
                    float(flow["interest"].fillna(0).sum()), 2)
            rows.append(row)
            print(row)
    grid = pd.DataFrame(rows)
    grid.to_csv(os.path.join(OUT, "sensitivity_grid.csv"), index=False)
    print("\nWrote", os.path.join(OUT, "sensitivity_grid.csv"))


if __name__ == "__main__":
    main()
