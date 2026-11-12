# SIMULATED CREDIT COMMITTEE MEMO

**To:** Credit Committee (simulation — training material, not investment advice)
**From:** Structured Credit Analytics
**Date:** 2026-11-12
**Subject:** Synthetic Auto Loan ABS — $100mm pool, Classes A / B / E —
structural review, stress results and tranche recommendations
**Model:** AbsBox / Hastructure 0.50.2 (absbox 0.50.3), fully reproducible
from this repository (`src/run_scenarios.py`, `src/run_v3.py`)

---

## 1. Recommendation summary

| Class | Par | Coupon | Recommendation (simulated) | Key support |
|---|---:|---:|---|---|
| A | $85mm | 5.00% | **Approve at par** | No loss up to pool CNL 12.06% (≈5× base CNL); XIRR 5.12% in all scenarios |
| B | $10mm | 7.50% | **Approve at par, with trigger** | Break-even CNL 12.05–12.06%; in v3 stress the CNL trigger is the difference between full repayment and a $2.49mm principal loss |
| E | $6mm (v3) | residual | **Only at a discount / for risk capital** | Return is timing-dominated: 4.3% XIRR front-loaded vs 8.8% back-loaded at identical lifetime CNL of 8% |

## 2. Transaction summary

- **Collateral:** $100mm synthetic auto loans in three segments —
  prime $50mm @ 6.50% APR / 60m; near-prime $30mm @ 10.50% / 60m;
  subprime $20mm @ 17.00% / 48m; pool WAC ≈ 9.8%. Level-payment
  amortizing loans, all originated at the 2025-12-01 cutoff.
- **Structure (v3):** A $85mm / B $10mm / E $6mm = $101mm of notes
  against the $100mm pool plus a $1mm reserve account funded at
  closing by the equity upsizing. Cutoff 2025-12-01, closing
  2026-01-15, monthly payments on the 25th, stated maturity 2031-06-01.
- **Credit enhancement:** subordination of 15% beneath A (5% beneath
  B); reserve account targeted at 1.00% of the *current* pool balance;
  excess spread (pool WAC 9.8% vs weighted note coupons) as first line
  of defence; CNL trigger at $4.0mm cumulative net loss (4% of the
  pool) switching the deal to a turbo waterfall.
- **Cutoff-to-closing bridge** is fully reconciled
  (`outputs/closing_bridge.md`): sources $100mm of v2 note proceeds =
  uses $100mm pool purchase; the closing-date balance of $97.67mm plus
  $2.99mm of collected cash ties to the cent.

## 3. Scenario results (engine runs, `outputs/summary.md`)

| Scenario | Pool CNL | Tranche principal losses | E residual | E XIRR |
|---|---:|---|---|---:|
| Optimistic | $1.02mm (1.02%) | none | $10.10mm | 28.7% |
| Base | $2.43mm (2.43%) | none | $8.67mm | 25.1% |
| Stress | $7.49mm (7.49%) | none | $2.65mm | 9.3% |

In the v2 structure excess spread absorbs every dollar of loss in all
three scenarios; the equity risk expresses itself as **residual
compression**, not principal impairment. That changes at higher
multiples of base CDR (see break-evens) and it changes in the v3
normal waterfall, where principal proceeds alone cannot retire the
notes under stress (see §5).

## 4. Break-even analysis (P3, `outputs/breakeven.md`)

Bisection to a 0.005× tolerance on the CDR multiplier (base CPR /
recovery / lag), reported as brackets — at the lower bound the tranche
is whole, at the upper bound it has its first loss:

- **Class E:** break-even CNL **8.63–8.64%** (3.84× base CDR)
- **Class B:** break-even CNL **12.05–12.06%** (5.64× base CDR)
- **Class A:** no loss at or below the Class B break-even; A's
  protection is the full $15mm of subordination plus reserve and
  excess spread.

Price sensitivity at par ±5 (XIRR, `outputs/price_yield.csv`):
under stress, E yields 10.50% at 95 / 9.32% at 100 / 8.21% at 105;
B yields 9.33% / 7.76% / 6.30%; A yields 8.32% / 5.12% / 2.22%.

## 5. Dynamic credit enhancement (P1, `outputs_v3/summary_v3.md`)

The v3 waterfall separates interest and principal proceeds. In the
**normal** state, notes amortize only from principal proceeds and
excess interest is released to equity monthly. If cumulative net
losses pass $4.0mm, the deal **accelerates**: releases stop, reserve
replenishment stops, and all interest proceeds turbo-pay the notes.

Under the stress scenario the trigger fires on **2027-02-28**, and it
is decisive:

| Stress run | B principal loss | Min OC (pool+reserve)/(A+B) | E total cash |
|---|---:|---:|---:|
| Trigger armed ($4mm) | **$0** | 102.5% | $7.00mm |
| Trigger disabled | **$2,489,871** | 76.1% | $9.35mm |

Two committee-relevant observations: (i) without the trigger the deal
goes **underwater on an OC basis (76.1%)** — collateral plus reserve
falls below A+B outstanding; (ii) the trigger protects the rated notes
**at equity's expense** — equity collects $4.48mm before the trigger
date and $7.00mm in total, vs $9.35mm when no trigger exists. Early
equity distributions are not clawed back; that asymmetry is precisely
why the trigger exists.

The reserve account is also drawn in the normal state under stress
(minimum balance $558,729 against a ~$0.9mm target) through its
interest-shortfall backstop role.

## 6. Default-timing experiment (P2, `outputs/timing_experiment.md`)

Three default-timing shapes calibrated to the **same** lifetime CNL of
$8.00mm (CPR 8%, recovery 35%):

| Variant | Defaults in first 12m | E total cash | E XIRR |
|---|---:|---:|---:|
| Front-loaded | 75.9% | $6.12mm | **4.31%** |
| Flat | 41.2% | $6.69mm | 6.33% |
| Back-loaded | 12.9% | $7.41mm | **8.80%** |

Identical lifetime losses produce a 4.5-point XIRR range for equity:
early defaults strike before excess spread has accumulated and keep
the senior notes outstanding longer (senior interest paid is highest
in the front-loaded case). Stretching the recovery lag from 4 to 12
months on the flat shape costs equity another ~0.8pt of XIRR.
**Lifetime CNL alone is not a sufficient statistic for tranche risk.**

## 7. Benchmarking against a real deal (verified facts only)

World Omni Auto Receivables Trust 2025-A (prime auto, closed
2025-01-29; facts from the 424B5/FWP-derived record — see
`references_woart_2025a.md` for sourcing and for the figures we could
NOT verify and therefore do not use):

| Item | This synthetic deal | WOART 2025-A |
|---|---|---|
| Pool | $100mm, mixed prime/near-prime/subprime | $1,305.7mm, prime (WA FICO 756) |
| Class A enhancement | 15% subordination + reserve 1% + excess spread | 4.75% initial → 5.65% target, OC 0.00% → 0.90%, reserve 0.25% |
| Senior coupon / WAL | A 5.00% / 1.64y (base) | A-3 4.73% / 2.63y |

Our structure carries roughly **3× the hard enhancement** of a real
prime deal — appropriately so: the synthetic pool blends subprime
collateral that a prime shelf would not hold, and the exercise is to
make the protection mechanics visible, not to replicate the real
deal's sizing.

## 8. Key risks and model limitations

1. **Representative-line collateral.** Three segment lines, not
   loan-level data; no delinquency roll dynamics, no used-vehicle
   price channel, no servicer behaviour. Results are structural, not
   a rating.
2. **Static scenario assumptions** per segment in the headline runs;
   the timing experiment relaxes this for defaults only. CPR is not
   stressed jointly with CDR outside the sensitivity grid.
3. **Engine-observed reserve behaviour:** in Accelerated status the
   reserve target stops stepping down (observed frozen at $631,111 in
   stress); that cash would be released at legal final maturity and
   is conservatively excluded from equity distributions here.
4. **Recovery modelling** is a fixed percentage of defaulted balance
   with a fixed lag; the lag experiment (§6) shows equity returns are
   materially sensitive to it.
5. **Version pinning:** results are reproducible only on the matched
   engine/library pair (Hastructure 0.50.2 + absbox 0.50.3).
6. **Verification:** every identity in this memo can be re-derived
   from the committed CSVs by the pytest suite in `tests/`
   (26 tests, no engine required).

## 9. Conclusion

The structure is sound at its stated sizing: the senior class is
protected to roughly 5× base-case losses, the mezzanine is protected
by the trigger mechanism in the states of the world where protection
matters, and the equity is a timing bet that should be priced as one.
Approve A and B at par (B conditional on the turbo trigger being in
the documents — in this model, removing it costs B $2.49mm under
stress); equity only at a discount that compensates for front-loaded
timing risk.
