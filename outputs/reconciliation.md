# Reconciliation report (v2 engine outputs)

| Scenario | Pool identity max resid | Bond identity max resid | Account end balance | Loss-order OK |
|---|---:|---:|---:|:--:|
| base | 2.98e-08 | 1.49e-08 | 0.00 | YES |

## base — loss attribution

- Pool cumulative net loss: $2,427,416.19
- Absorbed by excess spread: $2,427,416.19 (100.0% of losses; total interest collected $20,888,849.37)
- Borne by E: $0.00 | B: $0.00 | A: $0.00
| optimistic | 1.49e-08 | 1.49e-08 | 0.00 | YES |

## optimistic — loss attribution

- Pool cumulative net loss: $1,022,770.87
- Absorbed by excess spread: $1,022,770.87 (100.0% of losses; total interest collected $20,410,185.39)
- Borne by E: $0.00 | B: $0.00 | A: $0.00
| stress | 2.98e-08 | 1.49e-08 | 1,222.98 (post-maturity collections, see note) | YES |

## stress — loss attribution

- Pool cumulative net loss: $7,487,023.13
- Absorbed by excess spread: $7,487,023.13 (100.0% of losses; total interest collected $21,055,978.57)
- Borne by E: $0.00 | B: $0.00 | A: $0.00

Note: a non-zero account end balance is reconciled when it equals collections arriving after the last bond payment date (e.g. late recoveries after the final distribution on 2031-05-25, collected 2031-05-31 in the stress run: $1,222.98, 0.001% of the pool).

**Overall: ALL CHECKS PASS** (tolerance $0.01). Pool opens at exactly $100,000,000 and every period reconciles: BegBal − Principal − Prepayment − Default = EndBal.
