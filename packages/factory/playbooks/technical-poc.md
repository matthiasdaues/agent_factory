---
title: Technical Proof-of-Concept Playbook
category: orchestration
type: runbook
scenario: technical-poc
version: 1.0.0
---

# Technical Proof-of-Concept Playbook

Operational procedure for **answering a genuine technical or architectural risk question** with one or more working prototypes, before committing to a design decision.

Heavier than [poc-spike](poc-spike.md) — real dependencies are expected, multiple candidates are usually compared side by side, and the output feeds an actual decision. Lighter than the full requirements → architecture → planning → implementation → QA chain — no backlog frontmatter, no arc42 documentation of the prototype itself, no QA gates. This playbook sits between the two on purpose.

## When to use this, not the alternatives

| Situation                                                                                                                                                                              | Use                                                                                                                  |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| "Does this basic idea even work, what does it look like" — no comparison, no infra, throwaway                                                                                          | [poc-spike](poc-spike.md)                                                                                            |
| A specific technical/architectural risk or open question, often with 2+ candidate approaches, real dependencies (network, DB, external service, containers), feeding a coming decision | **This playbook**                                                                                                    |
| Building the real, production system                                                                                                                                                   | [feature-addition](feature-addition.md) (existing system) or the full requirements → architecture chain (new system) |

## Prerequisites

- [ ] A specific technical question or risk, stated clearly enough to design an experiment around
- [ ] If the risk is already tracked (an ADR's "Risks" section, an open todo), reference it — don't restate it from scratch

## Step 1 — Frame One Story per Candidate

For the question itself, or for each candidate approach being compared, write a short plain-markdown story (no backlog frontmatter needed yet — this isn't tracked work, it's an experiment). Store under `poc/spike/<name>.md` or similar. Each story states:

- **Goal** — the one thing this prototype must prove.
- **Why this is a candidate** — the tradeoff that makes it worth trying, and the specific risk being tested. Reference an existing ADR or open question if one already names this risk; don't invent a new framing for a risk that's already documented.
- **What to build** (or **What to research**, if the story is research-only — see below).
- **Definition of done** — a precise, mechanical checklist (starts on port X, exact input/output pair, runs twice without error), not a vague "it works."
- A closing instruction to **write a short comparison note** — this is what Step 4 consumes.

A story can be research-only: the deliverable is a short document, not code, with a working example as an optional bonus if time allows. Say so explicitly in the story so nobody over-builds it.

If a candidate's goal or Definition of Done is fuzzy, invoke [`grilling`](../skills/grilling/SKILL.md) first. Fixing it mid-build costs more.

## Step 2 — Build (or Research) Each Candidate Independently

Real dependencies are allowed here, unlike a spike: Docker containers, external libraries, multiple communicating processes — whatever the question actually requires to be answered honestly. Still skip:

- Backlog stories, spec/architecture docs, QA gates, test coverage beyond what proves the Definition of Done
- Handling anything the story's Definition of Done doesn't ask for

If candidates are independent (the usual case in a bake-off), build them in parallel — one worktree/session per candidate, same isolation principle the [Implementation Agent § Branching model](../agents/implementation-agent.md#branching-model) uses for backlog stories, just without the backlog machinery. No agent runs the build. You build each candidate yourself. Same rule as [poc-spike § Step 2](poc-spike.md#step-2--build-the-smallest-thing-that-could-show-it).

## Step 3 — Check Each Candidate Against Its Own Definition of Done

Run it. Compare against the checklist, not a feeling. Write the comparison note the story asked for — what worked, what didn't, effort/risk observed, anything surprising.

**All candidates checked and noted** → Step 4.
**A candidate can't be made to satisfy its Definition of Done** → note that as a real, useful result (a candidate ruled out is not a failed spike) and move on; don't sink more time chasing it than the other candidates got.

## Step 4 — Synthesize the Decision

Read every comparison note side by side.

**Multiple genuine candidates were compared** → this is exactly a Pugh Matrix moment: invoke the [Pugh Matrix skill § Build the matrix](../skills/pugh-matrix/SKILL.md#step-1--build-the-matrix) to formally score them against weighted criteria drawn from the comparison notes.
**One research question, one recommendation** → state the recommendation directly, citing the comparison note as evidence.

Then decide whether the decision itself is ADR-worthy, using this repo's usual bar (see [grill-with-docs](../skills/grill-with-docs/SKILL.md) / [Domain Modeling § Offer ADRs sparingly](../skills/domain-modeling/SKILL.md#offer-adrs-sparingly)): hard to reverse, surprising without context, and the result of a real trade-off. If all three hold, invoke [write-adr § Check for conflicts](../skills/write-adr/SKILL.md#step-1--check-for-conflicts) — the ADR cites the PoC's comparison notes (and Pugh Matrix, if one was built) as its evidence, not a restatement of the code.

## DONE

✅ **Question answered, decision made or explicitly deferred**

- [ ] Every candidate/question has a Definition-of-Done check and a comparison note
- [ ] A decision was recorded (ADR) or explicitly deferred with a stated reason — not left implicit
- [ ] Prototype code stays clearly marked as spike code (e.g. under `poc/`) — nothing here was silently promoted into the real codebase

**Next**: if the decision means the system is worth building for real, hand off to [feature-addition](feature-addition.md) or the full chain — same rule as [poc-spike](poc-spike.md): re-derive requirements properly, don't carry prototype code forward as a foundation just because it happened to run.
