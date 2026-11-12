# Cutoff-to-closing bridge (cutoff 2025-12-01 → closing 2026-01-15)

Sources & uses at closing — identical for all scenarios:

| Sources | $ | Uses | $ |
|---|---:|---|---:|
| Class A proceeds | 85,000,000.00 | Purchase of pool at cutoff balance | 100,000,000.00 |
| Class B proceeds | 10,000,000.00 | | |
| Class E proceeds | 5,000,000.00 | | |
| **Total sources** | **100,000,000.00** | **Total uses** | **100,000,000.00** |

**Concept note (read this before adding any two numbers in this file):** sources & uses describes the closing-date *funding flows* and balances at exactly $100mm. The trust *balance sheet* at closing is a different statement: loans ($97,673,228.91 in base) + collected cash ($2,985,652.34) = $100,658,881.25 of assets against $100,000,000 of notes. The $658,881.25 difference is pre-closing net earnings — interest collected between cutoff and closing, less defaults incurred in the same window (their recoveries are still pending and are NOT counted) — and it belongs to the residual holder. It is neither missing money nor double-counted collateral, and it must not be presented as part of the pool's principal balance.

## base

| Asset balance bridge | $ |
|---|---:|
| Pool balance at cutoff (2025-12-01) | 100,000,000.00 |
| Scheduled principal collected | (1,370,337.89) |
| Prepayments | (806,579.53) |
| Defaults (removed from balance; recovery pending) | (149,853.67) |
| **Pool balance at closing (2026-01-15)** | **97,673,228.91** |

| Pre-closing collections → collection account | $ |
|---|---:|
| Interest | 808,734.92 |
| Principal + prepayments | 2,176,917.42 |
| Recoveries received by closing | 0.00 |
| **Account balance at closing** | **2,985,652.34** |

Trust balance sheet at closing: loans $97,673,228.91 + cash $2,985,652.34 = notes $100,000,000.00 + pre-closing net earnings $658,881.25 (interest − defaults; recoveries still pending). ✓

## optimistic

| Asset balance bridge | $ |
|---|---:|
| Pool balance at cutoff (2025-12-01) | 100,000,000.00 |
| Scheduled principal collected | (1,368,131.53) |
| Prepayments | (1,042,241.58) |
| Defaults (removed from balance; recovery pending) | (73,535.10) |
| **Pool balance at closing (2026-01-15)** | **97,516,091.79** |

| Pre-closing collections → collection account | $ |
|---|---:|
| Interest | 807,792.04 |
| Principal + prepayments | 2,410,373.11 |
| Recoveries received by closing | 0.00 |
| **Account balance at closing** | **3,218,165.15** |

Trust balance sheet at closing: loans $97,516,091.79 + cash $3,218,165.15 = notes $100,000,000.00 + pre-closing net earnings $734,256.94 (interest − defaults; recoveries still pending). ✓

## stress

| Asset balance bridge | $ |
|---|---:|
| Pool balance at cutoff (2025-12-01) | 100,000,000.00 |
| Scheduled principal collected | (1,371,568.57) |
| Prepayments | (460,046.39) |
| Defaults (removed from balance; recovery pending) | (404,454.93) |
| **Pool balance at closing (2026-01-15)** | **97,763,930.11** |

| Pre-closing collections → collection account | $ |
|---|---:|
| Interest | 808,746.95 |
| Principal + prepayments | 1,831,614.96 |
| Recoveries received by closing | 0.00 |
| **Account balance at closing** | **2,640,361.91** |

Trust balance sheet at closing: loans $97,763,930.11 + cash $2,640,361.91 = notes $100,000,000.00 + pre-closing net earnings $404,292.02 (interest − defaults; recoveries still pending). ✓

All bridge identities hold to $0.01 in every scenario.
