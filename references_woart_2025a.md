# Real-deal comparison: WOART 2025-A (verified facts only)

## World Omni Auto Receivables Trust 2025-A (WOART 2025-A)

Status: **partially verified 2026-11-11** from the prospectus-derived presale page
(`https://data.consumercreditmatters.com/abs/issuance/presale/world-omni-auto-receivables-trust-2025-a.html`,
sources labelled 424B5 = final prospectus, FWP = pricing term sheet).
This is NOT the S&P presale report itself — S&P's own CNL assumption is not on this page.

### Verified against that page (424B5 / FWP)

| Item | WOART 2025-A (verified) |
|---|---|
| Closing date | 2025-01-29 |
| Pool balance at cut-off | $1,305.7mm |
| WA credit score | 756 |
| WA APR | 6.60% |
| WA original term | 68.2 months |
| % new vehicles | 95.6% |
| Geography top-3 | FL 49.1% / GA 18.2% / NC 17.8% |
| Classes | 7: A-1 $241.4mm, A-2a $309.8mm, A-2b $110.0mm, A-3 $419.8mm, A-4 $89.3mm, B $36.8mm, C $18.4mm |
| Class A enhancement, initial | 4.75% |
| Class A enhancement, target | 5.65% |
| Subordinate notes | 4.5% |
| Overcollateralization, initial | 0.00% |
| Overcollateralization, target | 0.90% |
| OC floor | 0.50% |
| Reserve account | 0.25% |
| Yield-supplement OC (YSOC) | 6.15% |
| A-3 coupon / WAL / spread | 4.73% / 2.63y / +45 bps |
| Sponsor / servicer | World Omni Financial Corp. |

### NOT verified — do not cite on a resume or in the README yet

- **S&P Expected CNL 1.25%**: no CNL figure appears on the prospectus-derived page.
  The other AI's thread attributes it to the S&P presale report; that report itself
  (RatingsDirect) was not checked in this run. Do not use 1.25% until the S&P
  presale is read directly.
- **Class A stress credit support ~9.8%**: hard enhancement on this page is
  4.75% initial / 5.65% target. A ~9.8% figure, if real, would have to include
  stressed excess-spread contribution on top of hard enhancement — it must be
  labelled that way and sourced to the S&P presale, not presented as hard
  credit enhancement.
- **Expected loss 5.25%** (appears in the user's course material per the other
  AI's thread): conflicts with the 1.25% claim and matches nothing on the
  WOART 2025-A page. Note: the peer table on the same page shows FCAOT 2024-D
  with 5.25% initial enhancement — a plausible source of a mix-up between
  deals. Do not use 5.25% for WOART 2025-A.
- **PenFed 2025-A**: not checked in this run; no coursework file has been
  supplied. No PenFed figures are included here.

### Side-by-side: this project's synthetic deal vs WOART 2025-A

| Item | Synthetic starter (this repo, actual run, v2/v3) | WOART 2025-A (real, prime) |
|---|---|---|
| Pool | $100mm, 3 segments (prime $50mm / near-prime $30mm / subprime $20mm) | $1,305.7mm, prime, WA FICO 756, 95.6% new |
| Senior | A $85mm @ 5.00%, WAL 1.64y (base) | A-1..A-4 totalling $1,170.3mm; A-3 @ 4.73%, WAL 2.63y |
| Subordination beneath senior | 15% (B $10mm + E $5mm) | 4.75% initial / 5.65% target |
| Reserve / OC | v3: reserve 1.00% of current pool balance; OC (pool+reserve)/(A+B) starts 106.3%; CNL trigger $4mm → turbo | Reserve 0.25%, OC 0.00% → target 0.90% |
| Base cumulative net loss | $2.43mm (2.43%), no tranche loss | S&P expected CNL — unverified, see above |
| Stress cumulative net loss | $7.49mm (7.49%), no tranche loss (v2); in v3 the trigger is what keeps B whole | Not modelled here |
| Break-even CNL | E 8.63–8.64%, B 12.05–12.06% | n/a |

Honest takeaway for interviews: the synthetic deal is **~3x more thickly
subordinated than a real prime deal** (15% vs 4.75%). A prime issuer can live
with thin hard enhancement because the pool is high-FICO, the WA APR funds
excess spread, and OC builds to target. Our synthetic pool is mixed
prime/near-prime/subprime, so it needs the thicker cushion — that contrast,
not a claim that the synthetic deal replicates WOART, is the correct way to
talk about the comparison.

### What is still missing for a full real-deal layer

1. S&P presale (RatingsDirect) for the 1.25% CNL and ~9.8% stress-support
   figures — or drop both figures and cite only the 424B5 numbers above.
2. The user's ISE 598 coursework files, if they exist — the PenFed side of
   the comparison cannot be built without them.
3. Servicer-report backtest (later step, not needed for the comparison table).
