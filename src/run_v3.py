"""
Run deal v3 (dynamic credit enhancement) and compare against the
trigger-disabled control.

Runs (segment assumptions as in v2):
  base / optimistic / stress          — CNL trigger armed at $4.0mm
  stress_no_trigger                   — same stress, trigger at $99mm
                                        (never fires) = control

Outputs (../outputs_v3/): per-run pool/bond/account flows, the engine
trigger statement, and summary_v3.md with trigger timing, OC range,
WALs, principal losses and equity distribution timing.

    python src/run_v3.py
"""

import os
import pandas as pd
from absbox import API
from deal_v3 import build_deal_v3, CNL_TRIGGER
from auto_abs_deal import segment_assump
from run_scenarios import with_date, wal

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs_v3")
os.makedirs(OUT, exist_ok=True)
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 6_000_000.0}
RUNS = [("base", "base", CNL_TRIGGER),
        ("optimistic", "optimistic", CNL_TRIGGER),
        ("stress", "stress", CNL_TRIGGER),
        ("stress_no_trigger", "stress", 99_000_000.0)]


def _find_trigger_stmt(obj):
    if isinstance(obj, dict):
        if "cnlTrigger" in obj:
            return obj["cnlTrigger"]
        for v in obj.values():
            found = _find_trigger_stmt(v)
            if found is not None:
                return found
    return None


def trigger_date(r):
    stmt = _find_trigger_stmt(r.get("triggers", {}))
    if stmt is None:
        return None
    fired = stmt[stmt["status"] == True]  # noqa: E712
    return str(fired.index[0])[:10] if len(fired) else None


def main():
    api = API("http://localhost:8081", "english")
    lines = ["# Deal v3 — dynamic credit enhancement (reserve + CNL trigger + turbo)",
             "",
             "Reserve target 1.00% of current pool balance (initial $1.0mm, "
             "funded by upsizing E to $6mm). CNL trigger at $4.0mm cumulative "
             "net loss switches the deal to the Accelerated (turbo) waterfall.",
             "",
             "| Run | Trigger fired | A WAL | B prin loss | E prin repaid | "
             "E total cash | E cash before trigger | Reserve min / end | OC min |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for label, scen, thr in RUNS:
        r = api.run(build_deal_v3(cnl_trigger=thr),
                    poolAssump=segment_assump(scen),
                    read=True, showWarning=False)
        tdate = trigger_date(r)
        seg = list(r["pool"]["flow"].values())
        all_dates = sorted(set().union(*[set(f.index) for f in seg]))
        pool = pd.DataFrame(index=all_dates)
        for col in ["Balance", "Interest", "Principal", "Prepayment",
                    "Default", "Recovery", "Loss"]:
            pool[col] = sum(f[col].reindex(all_dates).fillna(0.0)
                            for f in seg)
        pool["CumLoss"] = sum(f["CumLoss"].reindex(all_dates).ffill()
                              .fillna(0.0) for f in seg)
        pool.index.name = "Date"
        with_date(pool, "Date").to_csv(
            os.path.join(OUT, f"pool_flow_{label}.csv"), index=False)
        for acc, frame in r["accounts"].items():
            with_date(frame).to_csv(
                os.path.join(OUT, f"account_{acc}_{label}.csv"), index=False)
        reserve = r["accounts"]["reserveAcc"]["balance"]
        reserve_daily = reserve.groupby(level=0).last()
        res_min = float(reserve_daily[reserve_daily.index > "2026-02-01"].min())
        res_end = float(reserve.iloc[-1])
        stats = {}
        for tr, par in PAR.items():
            flow = r["bonds"][tr]
            with_date(flow).to_csv(
                os.path.join(OUT, f"bond_{tr}_flow_{label}.csv"), index=False)
            stats[tr] = {
                "prin": float(flow["principal"].fillna(0).sum()),
                "cash": float(flow["cash"].fillna(0).sum()),
                "wal": wal(flow),
            }
        e_flow = r["bonds"]["E"]
        if tdate:
            before = float(e_flow.loc[e_flow.index < tdate, "cash"]
                           .fillna(0).sum())
        else:
            before = stats["E"]["cash"]
        # OC series from the just-written CSVs (robust alignment):
        # (pool balance + reserve) / (A + B outstanding) at payment dates.
        pf = pd.read_csv(os.path.join(OUT, f"pool_flow_{label}.csv"))
        af = pd.read_csv(os.path.join(OUT, f"bond_A_flow_{label}.csv"))
        bf = pd.read_csv(os.path.join(OUT, f"bond_B_flow_{label}.csv"))
        rf = pd.read_csv(os.path.join(OUT, f"account_reserveAcc_{label}.csv"))
        ocdf = pd.DataFrame({
            "pool": pf.set_index("Date")["Balance"],
            "ab": af.set_index("date")["balance"] + bf.set_index("date")["balance"],
            "res": rf.groupby("date")["balance"].last()})
        ocdf.index = pd.to_datetime(ocdf.index)
        ocdf = ocdf.sort_index()
        oc = (ocdf["pool"].ffill() + ocdf["res"].ffill()) / ocdf["ab"]
        oc_min = float(oc[ocdf["ab"] > 0].min())
        lines.append(
            f"| {label} | {tdate or '—'} | {stats['A']['wal']:.2f}y | "
            f"${PAR['B'] - stats['B']['prin']:,.0f} | "
            f"${stats['E']['prin']:,.0f} | ${stats['E']['cash']:,.0f} | "
            f"${before:,.0f} | ${res_min:,.0f} / ${res_end:,.0f} | "
            f"{oc_min:.1%} |")
        print(label, "trigger:", tdate, "| B loss:",
              f"{PAR['B'] - stats['B']['prin']:,.0f}", "| E cash:",
              f"{stats['E']['cash']:,.0f}", "| reserve end:", f"{res_end:,.0f}")
    with open(os.path.join(OUT, "summary_v3.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote outputs_v3/summary_v3.md")


if __name__ == "__main__":
    main()
