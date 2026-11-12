# Deal v3 — dynamic credit enhancement (reserve + CNL trigger + turbo)

Reserve target 1.00% of current pool balance (initial $1.0mm, funded by upsizing E to $6mm). CNL trigger at $4.0mm cumulative net loss switches the deal to the Accelerated (turbo) waterfall.

| Run | Trigger fired | A WAL | B prin loss | E prin repaid | E total cash | E cash before trigger | Reserve min / end | OC min |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| base | — | 1.90y | $0 | $2,572,582 | $13,020,829 | $13,020,829 | $0 / $0 | 105.9% |
| optimistic | — | 1.79y | $0 | $3,977,228 | $14,546,718 | $14,546,718 | $0 / $0 | 106.2% |
| stress | 2027-02-28 | 2.01y | $0 | $2,521,762 | $6,998,971 | $4,477,208 | $558,729 / $631,111 | 102.5% |
| stress_no_trigger | — | 2.13y | $2,489,871 | $0 | $9,350,114 | $9,350,114 | $0 / $0 | 76.1% |
