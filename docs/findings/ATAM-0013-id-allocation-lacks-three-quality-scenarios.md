---
id: ATAM-0013
source: atam-review
severity: medium
category: defect
artifact: docs/arc42/10_quality_requirements.md#qs-18-no-id-is-handed-out-twice
status: open
owner: architecture-agent
traces: [QS-18, ADR-0031, ADR-0032, DEC-07, DEC-15, DEC-23]
---

# Chapter 10 has no scenario for the availability, security, or operability of an ID claim

**What is wrong:** The proposal names the risk domains `data_integrity`, `operations`, and `security`. The ID claim also adds a new availability dependency: no indexed artifact without the remote (DEC-07). Chapter 10 gains one scenario, QS-18, for unique IDs. No scenario gives a response measure for the other three attributes, so this review cannot judge them against the architecture, and a test strategy cannot derive a check from them.

The gap shows in one concrete case. QS-18 measures two parallel claims. The implementation agent dispatches one developer agent per story with no upper limit, and each may file findings at the same moment. All prefixes share one ref, so every claim collides with every other. The retry budget is ten stale leases with a wait of 0.1 to 1 second (DEC-15). On a hosted remote, one fetch and push can take about as long as the longest wait. With eight claims at once, the last one can use up its ten tries. That fails loudly and hands out no duplicate, but nothing in chapter 10 says how many parallel claims the design must carry.

**Fix:** Add three scenarios to section 10.1 and to the priority table in 10.2, each with a stimulus and a measurable response:

1. Availability: N parallel claims on one remote, with N set to the largest number of parallel sessions the Factory starts, all succeed within the retry budget. If N has no upper limit, say so and set the number that the race test checks.
2. Security: a push of `refs/ids/counters` by a principal without write access is refused, and a claim never needs more than write access to the repository.
3. Operability: every failed claim exits non-zero within a stated time and names one cause from the error table of the `next-id` contract. ATAM-0012 supplies the time limit.

Reference the scenarios from ADR-0031 and section 8.18.
