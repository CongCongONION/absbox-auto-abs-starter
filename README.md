# Auto ABS Cash Flow Modeling & Credit Stress Testing

A simplified, fully reproducible auto-loan securitization model built with
[AbsBox](https://github.com/yellowbean/AbsBox) (Python) on the Hastructure
cash-flow engine. It models a $100mm auto-loan pool as level-payment
amortizing loans, tranches it into a senior / mezzanine / equity stack with
a sequential-pay waterfall, and evaluates the structure with segment-level
stress scenarios, a CDR × CPR sensitivity grid, break-even cumulative net
loss (CNL) analysis, XIRR pricing at par, and a full cash-flow
reconciliation.

> **Scope & honesty note.** All collateral is *synthetic* (three
> representative segments, not loan-level real data) and the structure is a
> simplified amortizing deal. Results are outputs of this model only —
> they are **not** the results of any real transaction and not a
> rating-agency model.
>
> **v2 (2026-11-11)** replaced the v1 collateral model (flat-fee
> `Installment` rep lines with inconsistent seasoning — see git history)
> with true amortizing loans and aligned dates. v2 results therefore
> differ from v1 and supersede them; the v1 pool flows did not reconcile
> in the first period, which is exactly what the v2 reconciliation now
> verifies period by period.

中文说明见 [README_CN.md](README_CN.md).

## Transaction structure

| Component | Terms |
|---|---|
| Collateral | $100mm auto loans, 3 segments, level-payment amortizing (interest on outstanding balance): prime $50mm @ 6.50% APR / 60m; near-prime $30mm @ 10.50% / 60m; subprime $20mm @ 17.00% / 48m (pool WAC ≈ 9.8%) |
| Class A (senior) | $85mm, 5.00% fixed, sequential |
| Class B (mezzanine) | $10mm, 7.50% fixed, sequential |
| Class E (equity) | $5mm, no coupon, receives residual cash flow |
| Subordination | 15% beneath Class A (B + E) |
| Fees | Servicing: fixed $25,000 + 1.00% p.a. on pool balance |
| Waterfall (monthly) | Fees → A interest → B interest → A principal → B principal → E principal → residual to E |
| Dates | Origination = cutoff 2025-12-01; closing 2026-01-15; payments monthly on the 25th |

Collateral performance assumptions are **segment-specific** (CDR / CPR /
recovery / lag per segment):

| Segment | Base | Optimistic | Stress |
|---|---|---|---|
| Prime | 0.6% / 10% / 45% / 3m | 0.3% / 13% / 55% / 2m | 1.8% / 6% / 32% / 5m |
| Near-prime | 1.8% / 9% / 38% / 4m | 0.9% / 11% / 48% / 3m | 5.0% / 5% / 27% / 6m |
| Subprime | 4.5% / 7% / 28% / 5m | 2.2% / 9% / 35% / 4m | 11.0% / 4% / 20% / 8m |

![Tranche amortization](figures/fig2_tranche_amortization.svg)

*Sequential pay in the base scenario: Class A amortizes first while B and E
stay constant; B amortizes only after A is repaid, then E.*

## Results (actual engine run, v2, 2026-11-11)

| Scenario | Pool cum. net loss | A WAL / XIRR | B WAL / XIRR | E WAL / XIRR | Tranche principal losses |
|---|---|---|---|---|---|
| Base | $2.43mm | 1.64y / 5.12% | 3.73y / 7.76% | 4.16y / 25.08% | none |
| Optimistic | $1.02mm | 1.55y / 5.12% | 3.58y / 7.76% | 4.00y / 28.67% | none |
| Stress | $7.49mm | 1.83y / 5.12% | 4.14y / 7.76% | 4.67y / 9.32% | none |

XIRR = internal rate of return of buying at par at closing, discounted on
actual cash-flow dates (`src/pricing.py`). For E, cash flows include
residual distributions, so its XIRR is an equity IRR. Full tables:
`outputs/scenario_summary.csv`, `outputs/yield_summary.csv`.

**Key findings**

1. **Excess spread is the first line of defence — and it is thick.**
   The pool collects ≈ $21mm of interest over its life against ≈ $9.8mm of
   bond coupons and ≈ $4mm of fees. **All** losses in all three scenarios
   ($1.0mm / $2.4mm / $7.5mm) are absorbed by excess spread; no tranche
   takes a principal loss (verified in `outputs/reconciliation.md`).
2. **Equity risk shows up as residual compression, not principal loss.**
   E distributions fall from $10.10mm (optimistic) to $8.67mm (base) to
   $2.65mm (stress); E XIRR compresses 28.7% → 25.1% → 9.3%.
3. **Break-even CNL** (CDR multiplier on base, bisection in
   `src/breakeven.py`): Class E first takes a principal loss at
   ≈ **3.85× base CDR**, where pool CNL = **$8.64mm (8.64%)**; Class B at
   ≈ **5.64×**, CNL = **$12.07mm (12.07%)**. (`outputs/breakeven.md`)
4. **Faster prepayment compresses the equity residual.** In the uniform
   CDR × CPR grid (`outputs/sensitivity_grid.csv`), at a fixed CDR of
   0.5%, raising CPR from 3% to 15% cuts E distributions from $12.13mm to
   $9.81mm — prepaid loans stop generating the interest that funds the
   residual.

![Pool balance by scenario](figures/fig1_pool_balance.svg)

![Stress comparison](figures/fig3_stress_comparison.svg)

## Reconciliation

`src/reconciliation.py` checks every scenario, every period:

- Pool identity: BegBal − Principal − Prepayment − Default = EndBal
  (max residual ≈ 3e-08; pool opens at exactly $100,000,000)
- Bond identity per tranche: BegBal − PrincipalPaid = EndBal
- Loss allocation order (E before B before A)
- Account conservation; the only non-zero end balance is $1,222.98 of
  recoveries collected on 2031-05-31, after the final distribution date —
  flagged and explained in the report, not silently zeroed.

**Status: ALL CHECKS PASS** — see `outputs/reconciliation.md`.

A separate **cutoff-to-closing bridge** (`src/closing_bridge.py`,
`outputs/closing_bridge.md`) explains the first flow row: between cutoff
(2025-12-01) and closing (2026-01-15) the pool collects principal,
prepayments and interest and incurs its first defaults, so the closing
balance is $97.67mm (base), the collection account holds $2.99mm, and
sources & uses at closing balance exactly ($100mm of note proceeds =
$100mm pool purchase price). An independent pytest suite in `tests/`
re-derives every identity directly from the committed CSVs — no engine
required. (A GitHub Actions workflow for it is kept in
`.github/workflows/tests.yml` in the source tree.)

## Deal v3 — dynamic credit enhancement (`src/deal_v3.py`, `src/run_v3.py`)

The v2 structure plus the mechanisms of a real auto ABS, on a
split-proceeds design (interest proceeds and principal proceeds are
collected into separate accounts):

- **Reserve account** targeted at 1.00% of the current pool balance
  (initially $1.0mm, funded by upsizing equity to $6mm), acting as an
  interest-shortfall backstop and an excess-spread trap.
- **CNL trigger:** at $4.0mm of cumulative net losses the deal switches
  to an **Accelerated (turbo) waterfall** — equity releases stop and
  all interest proceeds pay note principal.
- In the normal state, notes amortize only from principal proceeds and
  excess interest is released to equity monthly, so the trigger has
  real economic content (with an all-cash waterfall it would change
  nothing — verified empirically).

Under stress the trigger fires on 2027-02-28 and is decisive
(`outputs_v3/summary_v3.md`): Class B is repaid in full with the
trigger and loses **$2,489,871** without it; minimum OC is 102.5%
with the trigger vs 76.1% without. Equity collects $4.48mm before the
trigger date — the protection is paid for by the residual holder, as
in real deals.

## Default timing matters (P2, `src/timing_experiment.py`)

Three default-timing shapes calibrated to the *same* lifetime CNL of
$8.00mm produce Class E XIRRs of **4.31% (front-loaded), 6.33% (flat),
8.80% (back-loaded)** — lifetime CNL alone is not a sufficient
statistic for tranche risk (`outputs/timing_experiment.md`).

## Credit committee memo

`reports/credit_committee_memo.md` — a simulated committee memo:
structure, scenario and break-even analysis, the trigger evidence, a
verified-facts-only benchmark against WOART 2025-A
(`references_woart_2025a.md`), model limitations, and per-tranche
recommendations. Price/yield sensitivity (95/100/105) is in
`outputs/price_yield.csv`.

## How to run

Version alignment matters (AbsBox rule: the Python package and the engine
must share the same minor version). Verified combination:
**absbox 0.50.3 + Hastructure 0.50.2**, run locally — the public engine at
absbox.org returned 502 Bad Gateway on 2026-11-10. Linux is the verified
platform; on macOS see the platform note in `engine/start_engine.sh`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# terminal 1 — local engine (script downloads the binary on first run)
bash engine/start_engine.sh            # http://localhost:8081

# terminal 2
python src/run_scenarios.py            # scenarios -> outputs/
python src/sensitivity.py              # CDR x CPR grid
python src/breakeven.py                # break-even CNL by tranche
python src/pricing.py                  # tranche XIRR at par + price/yield table
python src/reconciliation.py           # cash-flow checks -> outputs/reconciliation.md
python src/closing_bridge.py           # cutoff->closing bridge -> outputs/closing_bridge.md
python src/run_v3.py                   # deal v3 (reserve + trigger + turbo) -> outputs_v3/
python src/timing_experiment.py        # same-CNL, different default timing -> outputs/
python src/make_figures.py             # figures (SVG + PNG)
python -m pytest tests/ -q             # independent output-integrity tests (no engine needed)
```

## Repository layout

```
src/auto_abs_deal.py   deal v2 definition: segments, tranches, fees, waterfall
src/run_scenarios.py   base / optimistic / stress runs; WAL & loss summary
src/sensitivity.py     uniform CDR x CPR sensitivity grid
src/breakeven.py       break-even CNL via CDR-multiplier bisection (bracketed)
src/pricing.py         tranche XIRR at par on actual dates + price/yield table
src/reconciliation.py  period-by-period cash-flow verification & loss attribution
src/closing_bridge.py  cutoff-to-closing bridge: balance, collections, sources & uses
src/deal_v3.py         deal v3: reserve account, CNL trigger, turbo waterfall
src/run_v3.py          v3 runs incl. trigger-disabled control; OC & trigger timing
src/timing_experiment.py  same-CNL default-timing experiment (front/flat/back)
src/make_figures.py    figures from the engine outputs
tests/                 pytest suite re-deriving every identity from outputs/ (CI-run)
engine/start_engine.sh local Hastructure engine launcher (Linux; macOS note inside)
outputs/               v2 engine cash flows (CSV), summaries, reconciliation, breakeven
outputs_v3/            v3 engine cash flows and summary
reports/               credit committee memo
references_woart_2025a.md  real-deal benchmark facts (verified vs unverified split)
figures/               charts generated from outputs/
```

## Limitations & next steps

- Synthetic representative segments, not loan-level data; headline
  assumptions are constant CDR/CPR curves per segment (default timing
  is explored separately in the P2 experiment; no macro-linked
  dynamics).
- Engine-observed behaviour worth knowing: on Hastructure 0.50.2 the
  `cumPoolNetLossRate` trigger datasource never fires (deprecated in
  absbox 0.50.3) — the v3 trigger uses the `cumPoolNetLoss` balance
  instead; and once the deal accelerates, the reserve target stops
  stepping down (in stress it stays at its trigger-date level,
  $631,111, released at legal final).
- Technical note: segment assumptions are applied per sub-pool
  ("ByPoolId"); the "ByIndex" assumption form is not accepted by engine
  0.50.2 (verified empirically).
