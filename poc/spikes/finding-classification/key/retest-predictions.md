# Retest predictions, written before the run (2026-11-18)

Arm K (control): raters K1, K2 with rules-1.md (current rulebook).
Arm T (treatment): raters T1, T2 with rules-2.md (current + R1..R4).
Same ten filed-version findings for both arms.

- P1 (R1): T1 and T2 both give in_use false for SPEC-0007, SPEC-0013, SPEC-0014, and both give in_use true for SPEC-0015. Refuted by any split or other value.
- P2 (R2): T1 and T2 both give SPEC-0015 harms_downstream false and severity major. Refuted if either says harms true.
- P3 (R3): T1 and T2 both put ATAM-0002, ATAM-0003, ATAM-0007 in the architecture class and ATAM-0009 in the document class. Refuted by any other class.
- P4 (R4): T1 and T2 both give ATAM-0002, ATAM-0003, ATAM-0007 importance high and severity major. Refuted by any other importance.
- Necessity: arm K repeats at least one split of the first run on these findings (class on ATAM-0002/0003/0007, or in_use on SPEC-0007). If arm K agrees everywhere, the recommendation is a clarification only, not a demonstrated fix.
- Rule gap count: arm T reports fewer rule_gap entries on SPEC-0007, 0013, 0014, 0015, ATAM-0002, 0003, 0007 than arm K.
