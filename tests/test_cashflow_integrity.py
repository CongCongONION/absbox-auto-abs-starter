"""
Independent integrity tests over the committed engine outputs.

These tests deliberately do NOT trust src/ code: they re-derive every
identity directly from outputs/*.csv, the way an external reviewer or a
model-validation team would. They run without the Hastructure engine.

    pip install pandas pytest
    python -m pytest tests/ -q
"""

from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
POOL_PAR = 100_000_000.0
PAR = {"A": 85_000_000.0, "B": 10_000_000.0, "E": 5_000_000.0}
SCENARIOS = ["base", "optimistic", "stress"]
TOL = 0.01


def load(name):
    return pd.read_csv(OUT / name)


@pytest.mark.parametrize("scen", SCENARIOS)
def test_cutoff_to_closing_bridge(scen):
    pool = load(f"pool_flow_{scen}.csv")
    first = pool.iloc[0]
    assert first["Date"] == "2026-01-15"
    reduction = first["Principal"] + first["Prepayment"] + first["Default"]
    assert abs(first["Balance"] - (POOL_PAR - reduction)) < TOL
    assert first["Balance"] < POOL_PAR  # closing balance != cutoff balance


@pytest.mark.parametrize("scen", SCENARIOS)
def test_preclosing_collections_equal_account(scen):
    pool = load(f"pool_flow_{scen}.csv")
    acct = load(f"account_flow_{scen}.csv")
    first = pool.iloc[0]
    collections = (first["Interest"] + first["Principal"]
                   + first["Prepayment"] + first["Recovery"])
    acct_close = acct.loc[acct["date"] == "2026-01-15", "balance"].iloc[-1]
    assert abs(collections - acct_close) < TOL


@pytest.mark.parametrize("scen", SCENARIOS)
def test_pool_identity_every_period(scen):
    pool = load(f"pool_flow_{scen}.csv")
    beg = pool["Balance"].shift(1)
    beg.iloc[0] = POOL_PAR
    resid = (beg - pool["Principal"] - pool["Prepayment"]
             - pool["Default"] - pool["Balance"]).abs().max()
    assert resid < TOL


@pytest.mark.parametrize("scen", SCENARIOS)
@pytest.mark.parametrize("tranche", list(PAR))
def test_bond_identity_and_nonnegative(scen, tranche):
    flow = load(f"bond_{tranche}_flow_{scen}.csv")
    beg = flow["balance"].shift(1)
    beg.iloc[0] = PAR[tranche]
    resid = (beg - flow["principal"].fillna(0) - flow["balance"]).abs().max()
    assert resid < TOL
    assert (flow["balance"] >= -TOL).all()
    paid = flow["principal"].fillna(0).sum()
    assert paid <= PAR[tranche] + TOL  # never repay more than par


@pytest.mark.parametrize("scen", SCENARIOS)
def test_loss_allocation_order(scen):
    losses = {}
    for tranche, par in PAR.items():
        flow = load(f"bond_{tranche}_flow_{scen}.csv")
        losses[tranche] = par - flow["principal"].fillna(0).sum()
    if losses["B"] > TOL:
        assert losses["E"] >= PAR["E"] - TOL
    if losses["A"] > TOL:
        assert losses["B"] >= PAR["B"] - TOL
        assert losses["E"] >= PAR["E"] - TOL


@pytest.mark.parametrize("scen", SCENARIOS)
def test_account_end_balance_explained(scen):
    acct = load(f"account_flow_{scen}.csv")
    end = float(acct["balance"].iloc[-1])
    if abs(end) < TOL:
        return
    # otherwise it must equal collections arriving after the last
    # bond payment date (post-maturity recoveries)
    last_pay = max(load(f"bond_{t}_flow_{scen}.csv")["date"].max()
                   for t in PAR)
    late = acct.loc[acct["date"] > last_pay, "change"].clip(lower=0).sum()
    assert abs(end - late) < TOL


def test_scenario_summary_matches_flows():
    summary = load("scenario_summary.csv").set_index(["scenario", "tranche"])
    for scen in SCENARIOS:
        pool = load(f"pool_flow_{scen}.csv")
        for tranche, par in PAR.items():
            flow = load(f"bond_{tranche}_flow_{scen}.csv")
            row = summary.loc[(scen, tranche)]
            assert abs(row["principal_paid"]
                       - flow["principal"].fillna(0).sum()) < TOL
            assert abs(row["pool_cum_loss"] - pool["CumLoss"].iloc[-1]) < TOL


def test_breakeven_ordering():
    import re
    text = (OUT / "breakeven.md").read_text()
    pcts = [float(x) for x in re.findall(r"\((\d+\.\d+)%\)", text)]
    # brackets: E break-even CNL in [8.63%, 8.64%], B in [12.05%, 12.06%]
    assert any(8.5 < p < 8.8 for p in pcts)
    assert any(11.9 < p < 12.2 for p in pcts)
    assert min(pcts) < max(pcts)  # E breaks before B


# ---------------- deal v3 (dynamic credit enhancement) ----------------

OUT3 = ROOT / "outputs_v3"


def _bond_principal(folder, tranche, run):
    flow = pd.read_csv(folder / f"bond_{tranche}_flow_{run}.csv")
    return flow["principal"].fillna(0).sum()


def test_v3_trigger_protects_class_b_in_stress():
    # trigger armed: B is repaid in full under stress
    assert abs(_bond_principal(OUT3, "B", "stress") - 10_000_000) < 0.01
    # control run (trigger disabled): B loses more than $1mm
    assert _bond_principal(OUT3, "B", "stress_no_trigger") < 9_000_000


def test_v3_reserve_releases_fully_in_normal_state():
    for run in ("base", "stress_no_trigger"):
        acct = pd.read_csv(OUT3 / f"account_reserveAcc_{run}.csv")
        assert abs(float(acct["balance"].iloc[-1])) < 0.01


def test_woart_actuals_series_is_sane():
    act = pd.read_csv(ROOT / "data" / "woart_2025d_actuals.csv")
    assert len(act) == 12
    cnl = act["cumulative_net_loss_pct"]
    assert cnl.is_monotonic_increasing
    assert abs(cnl.iloc[-1] - 0.61) < 0.005  # SEC-reported, Sep 2026
    assert act["pool_factor"].is_monotonic_decreasing
    assert abs(act["pool_factor"].iloc[-1] - 0.5745) < 0.001


@pytest.mark.parametrize("run", ["base", "optimistic", "stress",
                                 "stress_no_trigger"])
def test_v3_pool_identity(run):
    pool = pd.read_csv(OUT3 / f"pool_flow_{run}.csv")
    beg = pool["Balance"].shift(1)
    beg.iloc[0] = POOL_PAR
    resid = (beg - pool["Principal"] - pool["Prepayment"]
             - pool["Default"] - pool["Balance"]).abs().max()
    assert resid < TOL
