"""
Sensitivity grid: CDR x CPR -> tranche outcomes.

    python src/sensitivity.py

Output: ../outputs/sensitivity_grid.csv
Each cell runs the full deal through the Hastructure engine.
Recovery held at 35%, lag 4 months.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auto_abs_deal import auto_abs_deal  # noqa: E402
from run_scenarios import wal_years  # noqa: E402

from absbox import API, EnginePath  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

CDRS = [0.005, 0.015, 0.03, 0.05]
CPRS = [0.03, 0.08, 0.15]


def main():
    api = API(EnginePath.LOCAL, check=False, lang="english")
    rows = []
    for cdr in CDRS:
        for cpr in CPRS:
            assump = ("Pool", ("Installment", {"CDR": cdr}, {"CPR": cpr},
                               {"Rate": 0.35, "Lag": 4}, None), None, None)
            r = api.run(auto_abs_deal, poolAssump=assump, read=True)
            row = {"CDR": cdr, "CPR": cpr}
            for tranche, origin in [("A", 85e6), ("B", 10e6), ("E", 5e6)]:
                flow = r["bonds"][tranche]
                prin = float(flow["principal"].fillna(0).sum())
                cash = prin + float(flow["interest"].fillna(0).sum())
                row[f"{tranche}_loss"] = round(origin - prin, 2)
                row[f"{tranche}_cash"] = round(cash, 2)
                row[f"{tranche}_WAL"] = round(wal_years(flow), 3)
            rows.append(row)
            print(f"CDR={cdr} CPR={cpr} done")
    grid = pd.DataFrame(rows)
    grid.to_csv(os.path.join(OUT, "sensitivity_grid.csv"), index=False)
    print(grid.to_string(index=False))


if __name__ == "__main__":
    main()
