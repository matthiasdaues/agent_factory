---
id: RECON-0030
source: reconcile-spec
review_class: document
category: defect
type: spec-stale
severity: major
basis:
  in_use: false
  harms_downstream: false
  fails_purpose: true
  raises_cost: true
rating:
override_by:
override_reason:
stop_confirmed_by:
stop_confirmed_reason:
artifact: docs/spec/features/counter-ids-fitting.feature:323-342
status: open
owner: requirements-agent
traces: [ST-0380, BR-102, DEC-16]
---

# Rule CIF-11 still puts C back on the local counter, which DEC-16 forbids

**What is wrong:** Rule CIF-11 of `counter-ids-fitting.feature` reads "next-id --move-to-origin leaves both counters as they are when origin holds one or the push fails". Its two Scenarios expect the old behaviour:

- "A counter on origin refuses the move" expects `/work/demo/.git` to hold `refs/ids/counters` at C after the refusal.
- "A failed push puts the claim commit back on the local counter" expects the same after a push that a `pre-receive` hook refuses.

DEC-16 settled the opposite: a failed move push never puts C back. BR-102, ADR-0033, the Move Lifecycle, arc42 6.16, and QS-23 all say that the local counter keeps the marker and the setting stays. The code does the same. `_after_refusal` in `packages/factory/scripts/next-id:897` keeps the marker. The tests with the markers CIF-11-IT-01 and CIF-11-IT-02 assert the marker with parent C (`tests/factory/test_next_id_move.py:194` and `:212`). So the two Scenarios contradict the specification and the tests that claim to cover them.

**Why this severity:** The feature file is the acceptance specification of the slice. An agent that checks the code against these Scenarios reads a refused move as a code defect and would ask for C to come back, which DEC-16 forbids (fails_purpose). The Rule title also reaches the scope map, the gaps report, and the QA strategy, so each of them needs a second edit (raises_cost).

**Fix:** Rename the Rule, for example to "next-id --move-to-origin keeps the marker and the setting when origin holds a counter or the push fails". In "A counter on origin refuses the move", replace the step "/work/demo/.git holds refs/ids/counters at C" with "/work/demo/.git holds the marker commit with parent C". Rename the second Scenario, for example to "A failed push keeps the marker, and a second move resumes". Replace its step on C the same way, and add the resume that `test_dec_16_a_refused_push_keeps_the_marker_and_a_second_move_resumes` checks. Then rename the Rule in `docs/spec/scope-map.md:210`, in `docs/spec/work/counter-ids-fitting-gaps.md:24`, and in `docs/spec/work/counter-ids-fitting-qa-strategy.md:31`.
