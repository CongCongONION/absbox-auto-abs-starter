"""
Auto ABS deal definition — v2 (revised 2026-11-11).

Changes vs v1 (see git history):
  1. Collateral is now modelled as level-payment amortizing loans
     (AbsBox `Mortgage` asset with type "Level": interest accrues on the
     OUTSTANDING balance and the loan amortizes monthly), replacing the
     v1 `Installment` rep lines whose feeRate was a flat monthly fee on
     the ORIGINAL balance. AbsBox has no dedicated amortizing auto-loan
     asset class; Mortgage/Level is the engine's amortizing loan and is
     the treatment the AbsBox maintainer recommends for auto loans.
  2. Dates are aligned: every segment is originated ON the cutoff date
     (2025-12-01), so originTerm == remainTerm and currentBalance ==
     originBalance, and the pool starts at exactly $100mm at closing.
     In v1 the segments were "born seasoned" (remainTerm < originTerm,
     a July origin date against a December cutoff), which made the
     first pool-flow row drop $4.86mm that the flow columns could not
     explain. v2 reconciles to the cent (see src/reconciliation.py).
  3. Performance assumptions are segment-specific: the pool is split
     into three named sub-pools (prime / nearprime / subprime) and each
     gets its own CDR/CPR/recovery/lag via a "ByPoolId" assumption.
     (The "ByIndex" assumption form is not accepted by engine 0.50.2 —
     verified empirically; ByPoolId is the working route.)

Structure (unchanged from v1):
    Pool $100mm | A $85mm @5.00% | B $10mm @7.50% | E $5mm equity
    Fees: servicer fixed $25,000 + pool-balance fee 1.00% p.a.
    Waterfall: fees -> A int -> B int -> A/B/E principal (sequential)
               -> residual to E
"""

from absbox import Generic

CUTOFF = "2025-12-01"
CLOSING = "2026-01-15"

# name, balance, APR (fixed, on outstanding balance), term (months)
SEGMENTS = [
    ("prime",     50_000_000, 0.065, 60),
    ("nearprime", 30_000_000, 0.105, 60),
    ("subprime",  20_000_000, 0.170, 48),
]

# Per-segment assumptions per scenario: CDR, CPR (annual), recovery rate,
# recovery lag (months)
SEGMENT_ASSUMPS = {
    "base": {
        "prime":     (0.006, 0.10, 0.45, 3),
        "nearprime": (0.018, 0.09, 0.38, 4),
        "subprime":  (0.045, 0.07, 0.28, 5),
    },
    "optimistic": {
        "prime":     (0.003, 0.13, 0.55, 2),
        "nearprime": (0.009, 0.11, 0.48, 3),
        "subprime":  (0.022, 0.09, 0.35, 4),
    },
    "stress": {
        "prime":     (0.018, 0.06, 0.32, 5),
        "nearprime": (0.050, 0.05, 0.27, 6),
        "subprime":  (0.110, 0.04, 0.20, 8),
    },
}


def _asset(balance, apr, term):
    return ["Mortgage",
            {"originBalance": balance, "originRate": ["fix", apr],
             "originTerm": term, "freq": "Monthly", "type": "Level",
             "originDate": CUTOFF},
            {"currentBalance": balance, "currentRate": apr,
             "remainTerm": term, "status": "current"}]


def _perf(cdr, cpr, rec, lag):
    return ("Mortgage", {"CDR": cdr}, {"CPR": cpr},
            {"Rate": rec, "Lag": lag}, None)


def segment_assump(scenario: str):
    """ByPoolId assumption: one (CDR/CPR/recovery/lag) set per sub-pool."""
    return ("ByPoolId", {
        name: ("Pool", _perf(*SEGMENT_ASSUMPS[scenario][name]), None, None)
        for name, *_rest in SEGMENTS})


def uniform_assump(cdr, cpr, rec=0.35, lag=4):
    """Same assumption for every sub-pool — used by the sensitivity grid
    so the v2 grid stays comparable to the v1 grid."""
    return ("ByPoolId", {
        name: ("Pool", _perf(cdr, cpr, rec, lag), None, None)
        for name, *_rest in SEGMENTS})


def build_deal():
    return Generic(
        "AutoABS-Starter-v2",
        {"cutoff": CUTOFF, "closing": CLOSING, "firstPay": "2026-02-25",
         "payFreq": ["DayOfMonth", 25], "poolFreq": "MonthEnd",
         "stated": "2031-06-01"},
        {name: {"assets": [_asset(bal, apr, term)]}
         for name, bal, apr, term in SEGMENTS},
        (("acc01", {"balance": 0}),),
        (("A", {"balance": 85_000_000, "rate": 0.05,
                "originBalance": 85_000_000, "originRate": 0.05,
                "startDate": CLOSING, "rateType": {"Fixed": 0.05},
                "bondType": {"Sequential": None}}),
         ("B", {"balance": 10_000_000, "rate": 0.075,
                "originBalance": 10_000_000, "originRate": 0.075,
                "startDate": CLOSING, "rateType": {"Fixed": 0.075},
                "bondType": {"Sequential": None}}),
         ("E", {"balance": 5_000_000, "rate": 0.0,
                "originBalance": 5_000_000, "originRate": 0.0,
                "startDate": CLOSING, "rateType": {"Fixed": 0.0},
                "bondType": {"Equity": None}})),
        (("servicerFee", {"type": {"fixFee": 25_000}, "feeStart": CLOSING}),
         ("poolFee", {"type": {"annualPctFee": [("poolBalance",), 0.01]},
                      "feeStart": CLOSING})),
        {"amortizing": [
            ["payFee", "acc01", ["servicerFee", "poolFee"]],
            ["accrueAndPayInt", "acc01", ["A"]],
            ["accrueAndPayInt", "acc01", ["B"]],
            ["payPrinBySeq", "acc01", ["A", "B", "E"]],
            ["payIntResidual", "acc01", "E"],
        ]},
        [[["prime", "nearprime", "subprime"], "CollectedCash", "acc01"]],
        None, None, None, None,
        ("PreClosing", "Amortizing"),
    )
