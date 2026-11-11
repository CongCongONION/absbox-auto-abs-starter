# Auto ABS starter — scenario results (v2, engine run 2026-11-11)

Segment-level assumptions (CDR/CPR/recovery/lag by segment); collateral = level-payment amortizing loans, pool opens at exactly $100,000,000.

| Scenario | Tranche | Principal paid | Principal loss | Interest paid | WAL (yrs) |
|---|---|---:|---:|---:|---:|
| base | A | 85,000,000.00 | 0.00 | 6,968,547.09 | 1.639 |
| base | B | 10,000,000.00 | 0.00 | 2,799,300.14 | 3.730 |
| base | E | 5,000,000.00 | 0.00 | 8,668,584.32 | 4.163 |

_base: pool cum. net loss $2,427,416.19; segment CDR prime 0.6% / near-prime 1.8% / subprime 4.5%._
| optimistic | A | 85,000,000.00 | 0.00 | 6,578,813.57 | 1.547 |
| optimistic | B | 10,000,000.00 | 0.00 | 2,687,582.04 | 3.581 |
| optimistic | E | 5,000,000.00 | 0.00 | 10,096,017.33 | 3.995 |

_optimistic: pool cum. net loss $1,022,770.87; segment CDR prime 0.3% / near-prime 0.9% / subprime 2.2%._
| stress | A | 85,000,000.00 | 0.00 | 7,785,021.39 | 1.831 |
| stress | B | 10,000,000.00 | 0.00 | 3,105,629.25 | 4.138 |
| stress | E | 5,000,000.00 | 0.00 | 2,650,456.97 | 4.672 |

_stress: pool cum. net loss $7,487,023.13; segment CDR prime 1.8% / near-prime 5.0% / subprime 11.0%._
