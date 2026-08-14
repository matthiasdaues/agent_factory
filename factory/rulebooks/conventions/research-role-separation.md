---
title: Role-Separation Policy
category: policies
enforcement: semantic review validator
version: 1.0.0
---

# Role-Separation Policy

## Purpose

The role-separation policy governs who may act in which capacity during a research run. It ensures that no single agent both produces a claim and judges it, so that survival reflects independent scrutiny rather than self-assessment.

## Roles

The policy governs four roles defined in the workflow: the **Researcher**, who authors conjectures and their supporting evidence; the **Claim Reviewer**, who attempts to refute a conjecture and casts a vote on its disposition; the **Research Orchestrator**, who runs the playbook, assigns agents, and tallies votes; and the **Research Report Writer**, who arranges the final report from the frozen claim register.

## Requirements

### Rule 1 — A Claim Author Cannot Review or Vote on That Claim

The Researcher who authored a conjecture must not act as the Claim Reviewer for that same conjecture. This rule governs the identity carried on the conjecture (the artifact the Researcher produces) against the identity carried on the review and on the `reviewer` field of the vote for that conjecture's `claim_hash`. The agent identity that produced the conjecture and the agent identity recorded as `reviewer` on its review and vote must never match.

### Rule 2 — A Reviewer Cannot Edit the Claim

The Claim Reviewer examines a conjecture and records findings in a review, but must not alter the conjecture itself — its `claim`, `scope`, `assumptions`, `supporting_evidence`, `contrary_evidence`, `possible_refuting_evidence`, `planned_tests`, or `qualifications`. Only the Researcher (through a new claim version) may change these fields. A review that also modifies the conjecture it reviews violates this rule regardless of the reviewer's intent.

### Rule 3 — The Orchestrator Cannot Vote

The Research Orchestrator tallies votes and freezes the claim register, but must never appear as the `reviewer` on a vote. The Orchestrator's role is administrative: it counts eligible votes and applies the Claim-Admission Policy's threshold; it does not supply one of the votes being counted. An orchestrator identity recorded as a vote's `reviewer` violates this rule.

### Rule 4 — The Report Writer Cannot Create Findings

The Research Report Writer arranges the final report's `findings` from the frozen claim register, and each finding's `surviving_claim_refs` must cite claim IDs already present in the register's `surviving_claims`. The Report Writer must not introduce a finding whose `surviving_claim_refs` point to a claim absent from the frozen register, and must not conduct new research or add claims of its own. Findings originate only from claims that already survived the Claim-Admission Policy; the Report Writer selects, summarizes, and cites — it does not conjecture.

### Rule 5 — One Agent Cannot Fill Conflicting Roles for the Same Claim

For a single claim, no one agent identity may hold more than one of the following positions at once: author of the conjecture, reviewer of that conjecture, voter on that conjecture, or orchestrator tallying the vote on that conjecture. This rule closes the general case that Rules 1 through 3 name individually: any combination of conflicting roles held by the same identity against the same `claim_hash` undermines the independence the review and vote are meant to provide, whether or not that specific combination is separately named above.

## Application

These requirements apply throughout claim authoring, review, voting, and report generation. A conjecture, review, vote, or final report that carries a role conflict prohibited above must not be counted toward the Claim-Admission Policy and must not be released in the final report.

## Not Covered by This Policy

This policy does not decide:

- how many Researchers or Claim Reviewers a research run requires,
- how agents are assigned to bounded questions,
- how quorum is computed for a vote,
- whether a claim otherwise meets the Claim-Admission Policy.

Those decisions belong to research planning and the Claim-Admission Policy.
