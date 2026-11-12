"""
Deal v3 — dynamic credit enhancement (P1).

Same collateral and segment assumptions as v2 (src/auto_abs_deal.py),
but the liability structure gains the three mechanisms a real auto ABS
has and v2 lacked:

  1. RESERVE ACCOUNT (reserveAcc): funded at closing at $1,000,000
     (1.00% of the original pool balance), funded by upsizing the
     equity tranche E from $5mm to $6mm (sources $101mm = pool $100mm
     + reserve $1mm). Two mechanical roles, both engine-enforced:
       - interest-shortfall backstop: after interest is paid from the
         collection account, any still-due A/B interest is paid from
         the reserve;
       - excess-spread trap: each period, after interest, available
         cash replenishes the reserve up to its target before any
         principal is paid or any residual reaches equity.
  2. CNL TRIGGER: if cumulative net losses exceed $4,000,000 (4.00% of
     the original pool balance), the deal switches (non-curable) from
     status "Amortizing" to "Accelerated". The condition uses the
     cumPoolNetLoss balance datasource: the cumPoolNetLossRate variant
     is marked deprecated in absbox 0.50.3 and, verified empirically,
     never fires on engine 0.50.2.
  3. TURBO / ACCELERATED waterfall, on a split-proceeds design:
     collections are routed by type — interest proceeds to accInt,
     principal / prepayment / recovery proceeds to accPrin.
       NORMAL state: fees and note interest are paid from interest
       proceeds; notes amortize ONLY from principal proceeds; the
       reserve is trapped from excess interest; whatever interest
       proceeds remain are released to equity MONTHLY (the classic
       excess-spread release). Deleveraging is therefore slow and
       equity is paid early.
       ACCELERATED state (trigger breached): the monthly release
       stops, reserve replenishment stops, and ALL interest proceeds
       are swept into principal payment (turbo) — notes deleverage at
       maximum speed and equity receives nothing until the notes are
       repaid.
     The contrast is the point: with an all-cash sequential waterfall
     (v2) a turbo trigger changes nothing, because principal already
     absorbs every dollar. The trigger only has economic content once
     the normal state releases excess spread — verified empirically:
     the trigger statement shows the CNL trigger firing (e.g. at a
     $2mm test threshold in stress, 2026-06-30), and the two states
     produce materially different tranche outcomes (src/run_v3.py).

An OC series — (pool balance + reserve balance) / (A + B outstanding) —
is computed from the outputs in src/run_v3.py (initial OC = 101/95 =
106.32%; the trigger, not an OC test, is what switches the waterfall).

Syntax notes (all verified against engine 0.50.2 / absbox 0.50.3):
triggers live in the Generic argument after the collection rules,
keyed by evaluation point ("AfterCollect"); waterfall is a dict keyed
by deal status; reserve target uses {"fixReserve": amount}; transfers
use {"reserve": "gap"} / {"reserve": "excess"} limits.
"""

from absbox import Generic
from auto_abs_deal import SEGMENTS, _asset, CLOSING, segment_assump  # noqa: F401

RESERVE_TARGET = 1_000_000.0
CNL_TRIGGER = 4_000_000.0  # cumulative net loss, $ (4.00% of original pool)

_BONDS = (
    ("A", {"balance": 85_000_000, "rate": 0.05,
           "originBalance": 85_000_000, "originRate": 0.05,
           "startDate": CLOSING, "rateType": {"Fixed": 0.05},
           "bondType": {"Sequential": None}}),
    ("B", {"balance": 10_000_000, "rate": 0.075,
           "originBalance": 10_000_000, "originRate": 0.075,
           "startDate": CLOSING, "rateType": {"Fixed": 0.075},
           "bondType": {"Sequential": None}}),
    ("E", {"balance": 6_000_000, "rate": 0.0,
           "originBalance": 6_000_000, "originRate": 0.0,
           "startDate": CLOSING, "rateType": {"Fixed": 0.0},
           "bondType": {"Equity": None}}),
)

_FEES = (
    ("servicerFee", {"type": {"fixFee": 25_000}, "feeStart": CLOSING}),
    ("poolFee", {"type": {"annualPctFee": [("poolBalance",), 0.01]},
                 "feeStart": CLOSING}),
)

_WF_NORMAL = [
    ["payFee", "accInt", ["servicerFee", "poolFee"]],
    ["accrueAndPayInt", "accInt", ["A"]],
    ["accrueAndPayInt", "accInt", ["B"]],
    ["payInt", "reserveAcc", ["A", "B"]],          # reserve backstops interest
    ["transfer", "accInt", "reserveAcc", {"reserve": "gap"}],  # trap excess int
    ["payPrinBySeq", "accPrin", ["A", "B", "E"]],  # notes amortize from prin
    ["transfer", "reserveAcc", "accInt", {"reserve": "excess"}],  # end release
    ["payIntResidual", "accInt", "E"],             # monthly excess-spread release
    ["payIntResidual", "accPrin", "E"],            # sweep prin acct once notes done
]

_WF_ACCELERATED = [
    ["payFee", "accInt", ["servicerFee", "poolFee"]],
    ["accrueAndPayInt", "accInt", ["A"]],
    ["accrueAndPayInt", "accInt", ["B"]],
    ["payInt", "reserveAcc", ["A", "B"]],   # backstop draws; no replenishment
    ["transfer", "accInt", "accPrin"],      # sweep ALL interest into principal
    ["payPrinBySeq", "accPrin", ["A", "B", "E"]],  # turbo deleveraging
    ["transfer", "reserveAcc", "accPrin", {"reserve": "excess"}],  # end release
    ["payIntResidual", "accPrin", "E"],            # only once notes are repaid
    ["payIntResidual", "accInt", "E"],
]

# Reserve target: 1.00% of the CURRENT pool balance (initially
# $1,000,000 on the $100mm pool). A percentage-of-balance target steps
# down as the pool amortizes, so the {"reserve": "excess"} transfers in
# the waterfalls release the step-down amount progressively and nothing
# is left trapped at maturity. (A fixed target combined with a
# bond-balance predicate was tried first: the predicate is evaluated
# before the period's principal payments, so ~$0.9mm stayed trapped —
# documented in git history.)

def _trigger(threshold: float):
    return {
        "AfterCollect": {
            "cnlTrigger": {
                "condition": [("cumPoolNetLoss",), ">", threshold],
                "effects": ("newStatus", "Accelerated"),
                "status": False,
                "curable": False,
            }
        }
    }


_RESERVE_TYPE = ("target", ("poolBalance",), 0.01)


def build_deal_v3(cnl_trigger: float = CNL_TRIGGER):
    return Generic(
        "AutoABS-v3-DynamicCE",
        {"cutoff": "2025-12-01", "closing": CLOSING, "firstPay": "2026-02-25",
         "payFreq": ["DayOfMonth", 25], "poolFreq": "MonthEnd",
         "stated": "2031-06-01"},
        {name: {"assets": [_asset(bal, apr, term)]}
         for name, bal, apr, term in SEGMENTS},
        (("accInt", {"balance": 0}),
         ("accPrin", {"balance": 0}),
         ("reserveAcc", {"balance": RESERVE_TARGET,
                         "type": _RESERVE_TYPE})),
        _BONDS,
        _FEES,
        {"amortizing": _WF_NORMAL, "Accelerated": _WF_ACCELERATED},
        [[["prime", "nearprime", "subprime"], "CollectedInterest", "accInt"],
         [["prime", "nearprime", "subprime"], "CollectedPrincipal", "accPrin"],
         [["prime", "nearprime", "subprime"], "CollectedPrepayment", "accPrin"],
         [["prime", "nearprime", "subprime"], "CollectedRecoveries", "accPrin"]],
        None, None, None,
        _trigger(cnl_trigger),
        ("PreClosing", "Amortizing"),
    )
