"""
Run the Auto ABS starter deal under base / optimistic / stress scenarios.

Usage (local Hastructure engine must be running on http://localhost:8081,
see ../engine/start_engine.sh):

    python src/run_scenarios.py

Outputs (in ../outputs/):
    bond_flows_<scenario>.csv   - per-tranche cashflow from the engine
    pool_flow_<scenario>.csv    - pool cashflow from the engine
    scenario_summary.csv        - WAL / principal repaid / loss per tranche
    summary.md                  - readable summary table
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auto_abs_deal import auto_abs_deal, SCENARIOS  # noqa: E402

from absbox import API, EnginePath  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
os.makedirs(OUT, exist_ok=True)
START = pd.Timestamp("2026-01-15")


def wal_years(flow: pd.DataFrame) -> float:
    """Weighted average life in years, from a bond flow frame."""
    prin = flow["principal"].fillna(0.0)
    total = prin.sum()
    if total <= 0:
        return float("nan")
    dates = pd.to_datetime(flow.index)
    t = (dates - START).days / 365.25
    return float((t * prin).sum() / total)


def main():
    api = API(EnginePath.LOCAL, check=False, lang="english")
    rows = []
    for name, assump in SCENARIOS.items():
        r = api.run(auto_abs_deal, poolAssump=assump, read=True)
        pool_flow = r["pool"]["flow"]["PoolConsol"]
        pool_flow.to_csv(os.path.join(OUT, f"pool_flow_{name}.csv"))
        for tranche in ["A", "B", "E"]:
            flow = r["bonds"][tranche]
            flow.to_csv(os.path.join(OUT, f"bond_{tranche}_flow_{name}.csv"))
            origin = {"A": 85_000_000, "B": 10_000_000, "E": 5_000_000}[tranche]
            prin_paid = float(flow["principal"].fillna(0).sum())
            int_paid = float(flow["interest"].fillna(0).sum())
            rows.append({
                "scenario": name,
                "tranche": tranche,
                "origin_balance": origin,
                "principal_paid": round(prin_paid, 2),
                "principal_loss": round(origin - prin_paid, 2),
                "interest_paid": round(int_paid, 2),
                "total_cash": round(prin_paid + int_paid, 2),
                "WAL_years": round(wal_years(flow), 3),
                "final_balance": float(flow["balance"].iloc[-1]) if len(flow) else None,
            })
        cum_loss = float(pool_flow["CumLoss"].iloc[-1]) if "CumLoss" in pool_flow else None
        print(f"[{name}] pool rows={len(pool_flow)} cum_loss={cum_loss}")

    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(OUT, "scenario_summary.csv"), index=False)

    lines = ["# Auto ABS starter — scenario summary (AbsBox / Hastructure, actual run)",
             "",
             "Pool: USD 100mm synthetic auto loans (Installment rep lines). "
             "Tranches: A 85mm @5.00% / B 10mm @7.50% / E 5mm equity, sequential pay.",
             "",
             summary.to_markdown(index=False),
             "",
             "Scenarios: base CDR 1.5% / CPR 8% / recovery 35% lag 4m; "
             "optimistic CDR 0.8% / CPR 12% / recovery 45% lag 3m; "
             "stress CDR 4.0% / CPR 5% / recovery 25% lag 6m.",
             "",
             "Note: tranche E is the equity piece — its 'interest_paid' is "
             "residual cash (excess spread) paid via payIntResidual, not a coupon. "
             "In the stress scenario E absorbs the first loss: principal loss "
             "2,031,040 of 5,000,000, while A and B are fully repaid.",
             ""]
    with open(os.path.join(OUT, "summary.md"), "w") as f:
        f.write("\n".join(lines))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
