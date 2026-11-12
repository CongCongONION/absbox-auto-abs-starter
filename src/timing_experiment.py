"""
P2 — Controlled experiment: same lifetime CNL, different default TIMING.

Question (the one rating analysts actually ask): if two pools both lose
8% over their life, does it matter WHEN the defaults happen?

Design: v2 deal, uniform assumptions across segments (CPR 8%, recovery
35%, lag 4). The default assumption is a monthly CDR vector
({"CDR": [..]} — engine-verified semantics: annualized CDR per month,
applied in order). Three timing shapes, each calibrated by bisection
on a scale factor so that lifetime CNL = $8.00mm in every case:

  flat          constant CDR
  front_loaded  defaults concentrated in months 1-12
  back_loaded   defaults concentrated in months 25-48

Plus a fourth run: flat shape with recovery lag stretched 4 -> 12
months (same defaults; recoveries arrive later).

    python src/timing_experiment.py  ->  ../outputs/timing_experiment.md
"""

import os
import pandas as pd
from absbox import API
from auto_abs_deal import build_deal, SEGMENTS
from pricing import xirr

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
TARGET_CNL = 8_000_000.0
MONTHS = 66


def shape(name):
    if name == "flat":
        return [1.0] * MONTHS
    if name == "front_loaded":
        return [1.0] * 12 + [0.35] * 12 + [0.12] * (MONTHS - 24)
    if name == "back_loaded":
        return [0.12] * 24 + [1.0] * 24 + [0.35] * (MONTHS - 48)
    raise ValueError(name)


def assump(vec, lag=4):
    perf = ("Mortgage", {"CDR": vec}, {"CPR": 0.08},
            {"Rate": 0.35, "Lag": lag}, None)
    return ("ByPoolId", {name: ("Pool", perf, None, None)
                         for name, *_ in SEGMENTS})


def run(api, deal, vec, lag=4):
    r = api.run(deal, poolAssump=assump(vec, lag), read=True,
                showWarning=False)
    cnl = sum(float(f["CumLoss"].iloc[-1]) for f in r["pool"]["flow"].values())
    return r, cnl


def calibrate(api, deal, name, lag=4):
    base = shape(name)
    lo, hi = 0.01, 0.60
    for _ in range(14):
        mid = (lo + hi) / 2
        _, cnl = run(api, deal, [mid * w for w in base], lag)
        if cnl < TARGET_CNL:
            lo = mid
        else:
            hi = mid
    s = (lo + hi) / 2
    r, cnl = run(api, deal, [s * w for w in base], lag)
    return s, r, cnl


def summarize(name, s, r, cnl, lag):
    pool_frames = list(r["pool"]["flow"].values())
    defaults_first12 = sum(float(f["Default"].iloc[:13].sum())
                           for f in pool_frames)
    defaults_total = sum(float(f["Default"].sum()) for f in pool_frames)
    row = {"variant": name, "cdr_scale": round(s, 4), "lag": lag,
           "cnl": round(cnl, 0),
           "defaults_in_first_12m_pct": round(100 * defaults_first12
                                              / defaults_total, 1)}
    for tr, par in PAR.items():
        f = r["bonds"][tr]
        row[f"{tr}_prin_loss"] = round(par - float(f["principal"]
                                                   .fillna(0).sum()), 0)
        row[f"{tr}_cash"] = round(float(f["cash"].fillna(0).sum()), 0)
    e = r["bonds"]["E"].reset_index().rename(columns={"index": "date"})
    row["E_xirr_pct"] = round(100 * xirr(e["date"], e["cash"], PAR["E"]), 2)
    return row


def main():
    api = API("http://localhost:8081", "english")
    deal = build_deal()
    rows = []
    for name in ["flat", "front_loaded", "back_loaded"]:
        s, r, cnl = calibrate(api, deal, name)
        rows.append(summarize(name, s, r, cnl, 4))
        print(rows[-1])
    # recovery-delay variant: flat shape & scale, lag 12
    s_flat = rows[0]["cdr_scale"]
    r, cnl = run(api, deal, [s_flat * w for w in shape("flat")], lag=12)
    rows.append(summarize("flat_recov_lag12", s_flat, r, cnl, 12))
    print(rows[-1])
    df = pd.DataFrame(rows)
    lines = ["# P2 — Same lifetime CNL, different default timing", "",
             "All variants calibrated to CNL ≈ $8.00mm (v2 deal, uniform "
             "CPR 8% / recovery 35%):", "",
             df.to_markdown(index=False), "",
             "Reading: identical lifetime losses do NOT produce identical "
             "tranche outcomes — when defaults land determines how much "
             "excess spread has accumulated to absorb them and how long "
             "the senior notes stay outstanding.",
             "The lag-12 variant has identical defaults; its slightly "
             "higher measured CNL is recoveries on late defaults arriving "
             "after the final distribution date."]
    with open(os.path.join(OUT, "timing_experiment.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
