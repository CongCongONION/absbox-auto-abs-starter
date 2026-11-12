# Actual vs. projected — WOART 2025-D servicer reports vs. this model

Source: SEC EDGAR, World Omni Auto Receivables Trust 2025-D (CIK 2087069), Form 10-D Exhibit 99.1 monthly distribution reports, 2025-10-31 to 2026-09-30 (12 reports), extracted by `src/backtesting.py` into `data/woart_2025d_actuals.csv`.

**Scope:** WOART 2025-D is a prime deal (original pool $982,748,036); this project's pool is a synthetic prime/near-prime/subprime blend. The comparison benchmarks performance *speeds* — it is not a re-underwriting of WOART, and differences are not 'model error' in the calibration sense.

## Reported actuals (latest month)

- Pool factor after 12 months: **0.575** (this model's base case at the same horizon: 0.758 — the real prime pool amortizes much faster)
- Cumulative net loss: **0.61%** of the original pool
- Latest monthly net-loss ratio (annualized): 0.85%
- Prepayment: ABS speed 1.77%/mo ≈ CPR 19.3%
- Delinquency 31+ / 61+: 2.27% / 0.69% of ending balance
- Reserve account: $2,295,966 (0.25% of the initial note balance, held at its required amount)

## CNL at matched horizon — forecast scoring

| Projection | CNL at month 12 | Error vs actual |
|---|---:|---:|
| WOART 2025-D actual | 0.61% | — |
| Naive benchmark (first-3-months pace, extrapolated) | 0.24% | -0.37 pts |
| This model, base case | 0.59% | -0.02 pts |
| This model, stress case | 1.18% | +0.57 pts |

Reading — three conclusions, stated carefully:

1. **The naive benchmark fails in the instructive direction.** Extrapolating the first three months (~0.02 pts/month) underestimates month-12 CNL by 0.37 pts, because auto-loan losses season: WOART's monthly CNL increments roughly tripled after month 3 (to ~0.05–0.08 pts). Early-pace extrapolation is exactly the error a structural model exists to avoid.
2. **Our base case lands within 0.02 pts of WOART's realized CNL at this horizon — and that must not be over-read.** The pools are different (50% of ours is near-prime/subprime), and offsetting differences roughly cancel at month 12: a hotter loss mix against much slower amortization (pool factor 0.76 modelled vs 0.57 realized) and recovery lags. Treat it as a reasonableness check that the model's loss *order of magnitude* is sane, not as calibration validation.
3. **Pace comparison:** WOART's realized monthly net-loss ratio runs at roughly 0.8–1.2% annualized in recent months; our base implies ~1.05% (weighted CDR 1.74% gross, ~39.5% blended recovery). The stress case sits at about twice the base pace — well outside the realized band, as a stress should.

## Actual monthly series

|   month | period_end          |   pool_balance_end |   pool_factor |   net_loss_month |   cumulative_net_loss_pct |   monthly_net_loss_ratio_ann_pct |   cpr_from_abs_pct |   delinq_31plus_pct |   reserve_balance |
|--------:|:--------------------|-------------------:|--------------:|-----------------:|--------------------------:|---------------------------------:|-------------------:|--------------------:|------------------:|
|       1 | 2025-10-31 00:00:00 |        8.7672e+08  |      0.892111 |          42353.8 |                      0    |                       nan        |            10.6065 |                0.64 |       2.29597e+06 |
|       2 | 2025-11-30 00:00:00 |        8.50032e+08 |      0.864954 |         131178   |                      0.02 |                         0.179548 |            16.4851 |                1.11 |       2.29597e+06 |
|       3 | 2025-12-31 00:00:00 |        8.2058e+08  |      0.834985 |         213575   |                      0.04 |                         0.301506 |            19.0921 |                1.34 |       2.29597e+06 |
|       4 | 2026-01-31 00:00:00 |        7.9148e+08  |      0.805374 |         757030   |                      0.12 |                         1.10707  |            19.0921 |                1.49 |       2.29597e+06 |
|       5 | 2026-02-28 00:00:00 |        7.62897e+08 |      0.77629  |         769804   |                      0.19 |                         1.16714  |            19.0921 |                1.5  |       2.29597e+06 |
|       6 | 2026-03-31 00:00:00 |        7.30522e+08 |      0.743346 |         652679   |                      0.26 |                         1.02663  |            22.1029 |                1.64 |       2.29597e+06 |
|       7 | 2026-04-30 00:00:00 |        7.01304e+08 |      0.713615 |         754145   |                      0.34 |                         1.2388   |            20.3675 |                1.62 |       2.29597e+06 |
|       8 | 2026-05-31 00:00:00 |        6.7488e+08  |      0.686728 |         545685   |                      0.39 |                         0.933721 |            18.7952 |                1.79 |       2.29597e+06 |
|       9 | 2026-06-30 00:00:00 |        6.45137e+08 |      0.656462 |         679631   |                      0.46 |                         1.20845  |            21.3359 |                1.78 |       2.29597e+06 |
|      10 | 2026-07-31 00:00:00 |        6.16753e+08 |      0.62758  |         429150   |                      0.51 |                         0.798249 |            20.8531 |                1.95 |       2.29597e+06 |
|      11 | 2026-08-31 00:00:00 |        5.8965e+08  |      0.600001 |         630489   |                      0.57 |                         1.22673  |            20.3675 |                1.94 |       2.29597e+06 |
|      12 | 2026-09-30 00:00:00 |        5.64606e+08 |      0.574518 |         419638   |                      0.61 |                         0.854007 |            19.2896 |                2.27 |       2.29597e+06 |
