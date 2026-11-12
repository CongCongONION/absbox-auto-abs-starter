# P2 — Same lifetime CNL, different default timing

All variants calibrated to CNL ≈ $8.00mm (v2 deal, uniform CPR 8% / recovery 35%):

| variant          |   cdr_scale |   lag |         cnl |   defaults_in_first_12m_pct |   A_prin_loss |      A_cash |   B_prin_loss |      B_cash |   E_prin_loss |      E_cash |   E_xirr_pct |
|:-----------------|------------:|------:|------------:|----------------------------:|--------------:|------------:|--------------:|------------:|--------------:|------------:|-------------:|
| flat             |      0.057  |     4 | 8.0011e+06  |                        41.2 |            -0 | 9.22676e+07 |             0 | 1.3027e+07  |             0 | 6.68861e+06 |         6.33 |
| front_loaded     |      0.1048 |     4 | 7.99894e+06 |                        75.9 |            -0 | 9.23841e+07 |             0 | 1.30977e+07 |             0 | 6.12132e+06 |         4.31 |
| back_loaded      |      0.1487 |     4 | 8.00056e+06 |                        12.9 |             0 | 9.21401e+07 |             0 | 1.29284e+07 |             0 | 7.40864e+06 |         8.8  |
| flat_recov_lag12 |      0.057  |    12 | 7.93006e+06 |                        41.2 |            -0 | 9.24051e+07 |             0 | 1.30523e+07 |             0 | 6.47057e+06 |         5.56 |

Reading: identical lifetime losses do NOT produce identical tranche outcomes — when defaults land determines how much excess spread has accumulated to absorb them and how long the senior notes stay outstanding.
The lag-12 variant has identical defaults; its slightly higher measured CNL is recoveries on late defaults arriving after the final distribution date.
