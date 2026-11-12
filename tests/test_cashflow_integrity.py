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
    text = (OUT / "breakeven.md").read_text()
    assert "8.64%" in text and "12.07%" in text  # E breaks before B
