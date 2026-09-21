# Secure-by-Design Integration Assessment

**Date:** 2026-09-17
**Type:** Exploration
**Subject:** `../secure-by-design` — feasibility and value of factory integration

## What It Is

A policy-as-code repository that converts a 568+ rule Cyber Security Baseline Excel
into structured markdown. Two policy sets (`.security-policies/`, `.testing-policies/`)
cover mandatory controls, frontend, backend, cloud infrastructure, and technology-specific
overlays (React, Express, Docker, Terraform, PostgreSQL, Sequelize, Axios, AI agent
runtime, and others). Built for consumption as a git submodule at `.secure-by-design/`.

No application code. Shell scripts (`bin/sbd-*.sh`) run audits against target repos.
Agent protocol and conditional policy loading already defined. Last LLM provenance
recorded as GPT-5.3-Codex. Originally built for GitHub Copilot workspace
(`.github/agents/`, `.github/instructions/`, `.github/skills/`).

## Integration Value by Factory Stage

| Stage                    | Value   | Mechanism                                                                                        |
| ------------------------ | ------- | ------------------------------------------------------------------------------------------------ |
| Feature discussion       | Low     | Conversational awareness of hard constraints only                                                |
| Proposal                 | Low     | Heads-up if proposed stack triggers policy domains                                               |
| Architecture             | Medium  | Policy domains as quality-attribute inputs to ATAM/ADRs                                          |
| Specification / Planning | High    | Fingerprint target stack → derive non-functional acceptance criteria and QA strategy per feature |
| Implementation           | Highest | Developer and code-review agents load relevant policy files as context                           |
| QA                       | Highest | Replace generic OWASP checklist with project-specific policy set                                 |

## Two Real Integration Points

1. **Spec/planning seam.** Fingerprint the target stack, determine which policy
   domains apply, feed non-functional criteria into QA strategy and story acceptance
   criteria. The repo's conditional-loading scheme (based on repository signals)
   already supports this.

2. **Implementation/QA seam.** Agents load relevant policy files when writing,
   reviewing, and testing code. The repo provides an agent protocol
   (`.security-policies/AGENT_PROTOCOL.md`) and a policies index for routing.

## Access Options

| Option                                                  | Portable | Versioned | Effort       |
| ------------------------------------------------------- | -------- | --------- | ------------ |
| Symlink (`ln -s ../secure-by-design .secure-by-design`) | No       | No        | Trivial      |
| Git submodule                                           | Yes      | Yes       | Two commands |

Submodule is the intended consumption model.

## Open Questions

- Which factory agents should be policy-aware? (Minimally: qa-agent, code-review-agent,
  developer-agent. Possibly: requirements-agent for QA strategy derivation.)
- Does the factory need its own policy-routing logic, or can it delegate to the
  repo's existing `AGENT_PROTOCOL.md`?
- Should policy compliance be a gate (blocks progression) or advisory (flagged in
  review)?
- The repo targets GitHub Copilot conventions — how much adaptation is needed for
  factory agent definitions?

## Recommendation

Add as submodule. Start with the implementation/QA seam (lowest friction, highest
value). Defer the spec/planning seam until the first real target project exercises it.
