"""
Auto ABS starter deal — built with AbsBox (absbox 0.50.3 / Hastructure 0.50.2)

A simplified, amortizing (non-revolving) auto-loan ABS:

  Pool  : USD 100mm of auto loans, modelled as 3 representative
          `Installment` lines (prime / near-prime / subprime).
          In AbsBox, an auto loan is an amortising installment asset:
          principal + fee are spread evenly over the term, and pool
          performance is driven by CDR / CPR / recovery assumptions.
  Bonds : A (senior, sequential)  USD 85mm @ 5.00% fixed
          B (mezzanine, sequential) USD 10mm @ 7.50% fixed
          E (equity)               USD  5mm @ 0%
          => Class A has 15% subordination (B + E) beneath it.
  Fees  : servicer fee 1.00% p.a. on pool balance, trustee fixed fee.
  Waterfall (each payment date, in order):
          fees -> A interest -> B interest -> A principal -> B principal
          -> E principal -> residual to E.

This is a *starter* structure for learning / interview discussion.
It is NOT the BMW 2023-01 deal: that real deal is revolving and much
more complex (see the AbsBox docs, "Real World Transaction").
All pool data here is synthetic and labelled as such.
"""

from absbox import Generic

POOL_SEGMENTS = [
    # (name, balance, feeRate, originTerm, remainTerm)
    # NOTE on feeRate: for an AbsBox `Installment` asset the fee is FLAT —
    # fee per month = originBalance x feeRate (verified against the engine:
    # balance 1,200 @ feeRate 0.01 -> fee 12.00 every month).
    # So feeRate is a MONTHLY flat fee on the ORIGINAL balance, not an APR.
    # Total finance charge over the full term = feeRate x term x balance:
    #   prime     0.0030 x 60 = 18.0% of original balance
    #   nearprime 0.0045 x 60 = 27.0%
    #   subprime  0.0070 x 48 = 33.6%
    ("prime",     50_000_000, 0.0030, 60, 60),
    ("nearprime", 30_000_000, 0.0045, 60, 54),
    ("subprime",  20_000_000, 0.0070, 48, 42),
]

def _installment(balance, fee_rate, origin_term, remain_term, origin_date="2025-07-01"):
    return ["Installment",
            {"originBalance": float(balance),
             "feeRate": ["fix", fee_rate],
             "originTerm": origin_term,
             "freq": "Monthly",
             "type": "f_p",
             "originDate": origin_date},
            {"status": "Current",
             "currentBalance": float(balance),
             "remainTerm": remain_term}]

assets = [_installment(b, r, ot, rt) for _, b, r, ot, rt in POOL_SEGMENTS]

auto_abs_deal = Generic(
    "AUTO-ABS-STARTER-2026"
    # dates
    , {"cutoff": "2025-12-01", "closing": "2026-01-15", "firstPay": "2026-02-25",
       "payFreq": ["DayOfMonth", 25], "poolFreq": "MonthEnd", "stated": "2031-06-01"}
    # pool
    , {"assets": assets}
    # accounts
    , (("distAcc", {"balance": 0}),)
    # bonds
    , (("A", {"balance": 85_000_000, "rate": 0.05,
              "originBalance": 85_000_000, "originRate": 0.05,
              "startDate": "2026-01-15",
              "rateType": {"Fixed": 0.05},
              "bondType": {"Sequential": None}}),
       ("B", {"balance": 10_000_000, "rate": 0.075,
              "originBalance": 10_000_000, "originRate": 0.075,
              "startDate": "2026-01-15",
              "rateType": {"Fixed": 0.075},
              "bondType": {"Sequential": None}}),
       ("E", {"balance": 5_000_000, "rate": 0.0,
              "originBalance": 5_000_000, "originRate": 0.0,
              "startDate": "2026-01-15",
              "rateType": {"Fixed": 0.0},
              "bondType": {"Equity": None}}))
    # fees
    , (("servicerFee", {"type": {"annualPctFee": [("poolBalance",), 0.01]},
                        "feeStart": "2026-01-15"}),
       ("trusteeFee", {"type": {"fixFee": 25000}, "feeStart": "2026-01-15"}))
    # waterfall
    , {"amortizing": [
        ["payFee", "distAcc", ["servicerFee", "trusteeFee"]],
        ["accrueAndPayInt", "distAcc", ["A"]],
        ["accrueAndPayInt", "distAcc", ["B"]],
        ["payPrin", "distAcc", ["A"]],
        ["payPrin", "distAcc", ["B"]],
        ["payPrin", "distAcc", ["E"]],
        ["payIntResidual", "distAcc", "E"],
    ]}
    # collection rules
    , [["CollectedInterest", "distAcc"],
       ["CollectedPrincipal", "distAcc"],
       ["CollectedPrepayment", "distAcc"],
       ["CollectedRecoveries", "distAcc"]]
    , None  # liquidity facility
    , None  # interest rate swap
    , None  # currency swap
    , None  # triggers
    , ("PreClosing", "Amortizing")
)

# ---- Pool performance scenarios -------------------------------------------
# Installment assumption = ("Installment", default, prepay, recovery, extra)
#   default : {"CDR": annualised constant default rate}
#   prepay  : {"CPR": annualised constant prepayment rate}
#   recovery: {"Rate": recovery rate on defaulted balance, "Lag": months}
SCENARIOS = {
    "base":       ("Pool", ("Installment", {"CDR": 0.015}, {"CPR": 0.08},
                            {"Rate": 0.35, "Lag": 4}, None), None, None),
    "optimistic": ("Pool", ("Installment", {"CDR": 0.008}, {"CPR": 0.12},
                            {"Rate": 0.45, "Lag": 3}, None), None, None),
    "stress":     ("Pool", ("Installment", {"CDR": 0.040}, {"CPR": 0.05},
                            {"Rate": 0.25, "Lag": 6}, None), None, None),
}
