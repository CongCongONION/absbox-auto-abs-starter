"""
Run the Auto ABS deal (v2) under base / optimistic / stress scenarios.

Usage (local Hastructure engine must be running on http://localhost:8081,
see ../engine/start_engine.sh):

    python src/run_scenarios.py

Outputs (in ../outputs/):
    pool_flow_<scenario>.csv, bond_<tranche>_flow_<scenario>.csv,
    account_flow_<scenario>.csv, scenario_summary.csv, summary.md
"""

import os
import pandas as pd
from absbox import API
from auto_abs_deal import build_deal, segment_assump, SEGMENT_ASSUMPS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}


def with_date(flow: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    """Engine read-results carry the date as the index; make it a column."""
    out = flow.copy()
    out.insert(0, col, pd.to_datetime(out.index).strftime("%Y-%m-%d"))
    return out.reset_index(drop=True)


def wal(flow: pd.DataFrame) -> float:
    """Weighted average life (years) from a bond flow frame (date = index)."""
    f = flow[flow["principal"] > 0].copy()
    if f.empty:
        return float("nan")
    dates = pd.to_datetime(f.index)
    yrs = ((dates - pd.Timestamp("2026-01-15")).days / 365.25).to_numpy()
    return float((f["principal"].to_numpy() * yrs).sum()
                 / f["principal"].sum())


def main():
    api = API("http://localhost:8081", "english")
    deal = build_deal()
    rows = []
    md = ["# Auto ABS starter — scenario results (v2, engine run 2026-11-11)",
          "",
          "Segment-level assumptions (CDR/CPR/recovery/lag by segment); "
          "collateral = level-payment amortizing loans, pool opens at "
          "exactly $100,000,000.",
          "",
          "| Scenario | Tranche | Principal paid | Principal loss | "
          "Interest paid | WAL (yrs) |",
          "|---|---|---:|---:|---:|---:|"]
    for scen in ["base", "optimistic", "stress"]:
        r = api.run(deal, poolAssump=segment_assump(scen),
                    read=True, showWarning=False)
        # sub-pool flows -> per-segment CSVs + a consolidated pool flow
        seg_frames = []
        for seg, frame in r["pool"]["flow"].items():
            with_date(frame, "Date").to_csv(
                os.path.join(OUT, f"pool_flow_{scen}_{seg}.csv"), index=False)
            seg_frames.append(frame)
        # consolidate on the union of dates: flow columns sum (missing = 0),
        # Balance sums (a finished segment contributes 0), Cum* sum after
        # forward-filling each segment's cumulative series.
        all_dates = sorted(set().union(*[set(f.index) for f in seg_frames]))
        pool = pd.DataFrame(index=all_dates)
        for col in ["Balance", "Interest", "Principal", "Prepayment",
                    "Default", "Recovery", "Loss"]:
            pool[col] = sum(f[col].reindex(all_dates).fillna(0.0)
                            for f in seg_frames)
        for col in ["CumPrincipal", "CumPrepay", "CumDefault", "CumRecovery",
                    "CumLoss"]:
            pool[col] = sum(f[col].reindex(all_dates).ffill().fillna(0.0)
                            for f in seg_frames)
        pool.index.name = "Date"
        with_date(pool, "Date").to_csv(
            os.path.join(OUT, f"pool_flow_{scen}.csv"), index=False)
        with_date(r["accounts"]["acc01"]).to_csv(
            os.path.join(OUT, f"account_flow_{scen}.csv"), index=False)
        cum_loss = float(pool["CumLoss"].iloc[-1])
        for tranche, par in PAR.items():
            flow = r["bonds"][tranche]
            with_date(flow).to_csv(
                os.path.join(OUT, f"bond_{tranche}_flow_{scen}.csv"),
                index=False)
            paid = float(flow["principal"].fillna(0).sum())
            loss = par - paid
            interest = float(flow["interest"].fillna(0).sum())
            w = wal(flow)
            rows.append({"scenario": scen, "tranche": tranche, "par": par,
                         "principal_paid": round(paid, 2),
                         "principal_loss": round(loss, 2),
                         "interest_paid": round(interest, 2),
                         "wal_years": round(w, 3),
                         "pool_cum_loss": round(cum_loss, 2)})
            md.append(f"| {scen} | {tranche} | {paid:,.2f} | {loss:,.2f} | "
                      f"{interest:,.2f} | {w:.3f} |")
        a = SEGMENT_ASSUMPS[scen]
        md.append("")
        md.append(f"_{scen}: pool cum. net loss ${cum_loss:,.2f}; segment "
                  f"CDR prime {a['prime'][0]:.1%} / near-prime "
                  f"{a['nearprime'][0]:.1%} / subprime {a['subprime'][0]:.1%}._")
    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(OUT, "scenario_summary.csv"), index=False)
    with open(os.path.join(OUT, "summary.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    print(summary.to_string(index=False))
    print("\nWrote outputs to", OUT)


if __name__ == "__main__":
    main()
