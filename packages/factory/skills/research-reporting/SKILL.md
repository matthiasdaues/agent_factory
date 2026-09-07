---
name: research-reporting
description: Build a final report from the frozen claim register without adding new findings, citing surviving claim IDs and preserving qualifications.
category: research
---

# Research Reporting

Compose the final research report from a frozen claim register. The playbook controls when the register is frozen and when the report is written; this skill covers how to write it.

The report must:

- Use only surviving claims as its factual basis.
- Cite the claim IDs that support each factual statement.
- Preserve all material qualifications, scope limits, and uncertainties.
- Distinguish findings from recommendations.
- Not conduct new research, create new claims, or present surviving claims as proved.

The report is the deliverable output of the research workflow. It must accurately represent what was found, what remains uncertain, and which tests failed.

## Input Artifacts

- **Frozen claim register** — the completed compilation of all claims (surviving, refuted, unresolved, and superseded), their evidence, tests, reviews, and votes. Frozen means no further claims or votes will be added. (Validated by `rulebooks/schemas/research-claim-register.schema.json`).

## Output Artifacts

- **Final report** — structured final report drawn from surviving claims (from `rulebooks/templates/research-final-report.md` and validated by `rulebooks/schemas/research-final-report.schema.json`).

## Key Principles

### No New Findings

This skill uses only the surviving claims from the frozen register. It does not:

- Conduct additional research or source searches.
- Propose new claims or conjectures.
- Derive inferences not already stated in the surviving claims.
- Add interpretations or analysis beyond summarizing surviving claims.

If a gap exists in the evidence, it must be noted as an unresolved question or evidence gap, not filled in speculatively.

### Cite Surviving Claim IDs

Every factual statement in the report must be traceable to one or more surviving claim IDs. The report must:

- Reference the claim IDs explicitly (e.g., "According to claim CLM-0042, ...").
- Link each finding to its supporting evidence, tests, and vote result.
- Show the chain from evidence → tests → reviews → votes → claim survival.

Unsupported statements (statements not traceable to a surviving claim) must be moved to the recommendations section, evidence gaps, or unresolved questions.

### Preserve Qualifications

All surviving claims carry qualifications, scope limits, and uncertainty statements. The report must:

- Preserve every material qualification attached to a claim.
- Avoid language that overstates confidence or certainty.
- Show which tests failed, which were inconclusive, and which passed.
- Identify evidence that could still refute a claim.
- Mark claims as "not refuted within the tested scope" rather than "proved" or "true."

Preferred wording includes:

- "survived the defined tests,"
- "not refuted within the tested scope,"
- "provisionally retained,"
- "remains open to refutation."

### Distinguish Findings from Recommendations

The report must clearly separate:

- **Findings** — statements supported by surviving claims and their evidence.
- **Recommendations** — proposed actions or next steps, clearly labeled as outside the scope of the research findings.
- **Unresolved questions** — gaps in evidence or competing claims that could not be settled.
- **Evidence gaps** — questions that no surviving claim addresses.
- **Limitations** — bounds on the scope, freshness, or applicability of the findings.

## Forbidden Content

The report must not:

- Present a surviving claim as proved or true.
- Use refuted or unresolved claims as factual basis.
- Hide material failed tests or inconclusive results.
- Omit required qualifications or scope statements.
- Change the scope of a claim from its surviving form.
- Treat correlated or paraphrased sources as independent evidence.
- Present stale or outdated evidence as current.
- Invent evidence to fill gaps.

## Structure and Form

The final report follows the template at `rulebooks/templates/research-final-report.md` and must conform to the schema at `rulebooks/schemas/research-final-report.schema.json`.

Typical sections include:

- **Research Question** — the question the research addressed.
- **Methodology** — how the research was conducted (planning, evidence collection, refutation strategy, review process).
- **Findings** — results organized by theme or question, each traceable to surviving claim IDs.
- **Failed and Inconclusive Tests** — important tests that did not support the claims.
- **Unresolved Alternatives** — claims that survived review but remain uncertain, or alternatives that could not be tested.
- **Evidence Gaps** — questions no surviving claim addresses.
- **Limitations** — scope, freshness, and applicability limits.
- **Recommendations** — proposed next steps or actions (optional, clearly outside the findings).

## Validation

The frozen claim register must be validated before report writing begins. The report itself must be validated after completion to ensure:

- Every factual statement cites a surviving claim ID.
- No refuted or unresolved claims appear as fact.
- No claim is presented as proved or true.
- All material qualifications are present.
- No required limits are omitted.
- Sources and evidence are accurately described.
