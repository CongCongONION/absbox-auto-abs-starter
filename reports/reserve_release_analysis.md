# Reserve remainder at maturity — release analysis (v3, stress)

In the v3 stress run the CNL trigger fires (2027-02-28) and the reserve target stops stepping down in the Accelerated state, leaving **$631,111.45** in the reserve account at the final distribution date (2031-05-25). The v3 outputs conservatively leave it there. In an actual transaction the reserve remainder is released at legal final maturity to the residual holder once the notes are repaid — and in this run Classes A and B are repaid in full, so the release belongs entirely to Class E:

| Class E (v3 stress) | As modelled | With legal-final release |
|---|---:|---:|
| Total cash | $6,998,970.52 | $7,630,081.97 |
| XIRR (on $6.0mm par) | 8.10% | 11.85% |

Effect: +$631,111.45 of cash (+9.0% of E's total distributions) and +3.75 pts of XIRR. No effect on Classes A or B, on the trigger date, or on any break-even result. The as-modelled (conservative) treatment is retained in all headline outputs; this note exists so the size of the simplification is on the record.
