# Auto ABS starter — scenario summary (AbsBox / Hastructure, actual run)

Pool: USD 100mm synthetic auto loans (Installment rep lines). Tranches: A 85mm @5.00% / B 10mm @7.50% / E 5mm equity, sequential pay.

| scenario   | tranche   |   origin_balance |   principal_paid |   principal_loss |   interest_paid |   total_cash |   WAL_years |   final_balance |
|:-----------|:----------|-----------------:|-----------------:|-----------------:|----------------:|-------------:|------------:|----------------:|
| base       | A         |         85000000 |      8.5e+07     |      0           |     7.06944e+06 |  9.20694e+07 |       1.662 |     0           |
| base       | B         |         10000000 |      1e+07       |      0           |     2.82875e+06 |  1.28288e+07 |       3.769 |     0           |
| base       | E         |          5000000 |      5e+06       |      0           |     2.15937e+06 |  7.15937e+06 |       4.291 |     0           |
| optimistic | A         |         85000000 |      8.5e+07     |      0           |     6.65346e+06 |  9.16535e+07 |       1.564 |     0           |
| optimistic | B         |         10000000 |      1e+07       |      0           |     2.7708e+06  |  1.27708e+07 |       3.692 |     0           |
| optimistic | E         |          5000000 |      5e+06       |      0           |     1.65514e+06 |  6.65514e+06 |       4.277 |     0           |
| stress     | A         |         85000000 |      8.5e+07     |      0           |     7.58765e+06 |  9.25877e+07 |       1.784 |     0           |
| stress     | B         |         10000000 |      1e+07       |      0           |     3.04897e+06 |  1.3049e+07  |       4.063 |     0           |
| stress     | E         |          5000000 |      2.96896e+06 |      2.03104e+06 |     0           |  2.96896e+06 |       4.535 |     2.03104e+06 |

Scenarios: base CDR 1.5% / CPR 8% / recovery 35% lag 4m; optimistic CDR 0.8% / CPR 12% / recovery 45% lag 3m; stress CDR 4.0% / CPR 5% / recovery 25% lag 6m.

Note: tranche E is the equity piece — its 'interest_paid' is residual cash (excess spread) paid via payIntResidual, not a coupon. In the stress scenario E absorbs the first loss: principal loss 2,031,040 of 5,000,000, while A and B are fully repaid.
