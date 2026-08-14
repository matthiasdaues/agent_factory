---
schema_version: 2
title: "Research Workflow CLI Portability Audit"
status: implemented
owner: agent-factory
created: 2026-07-26
updated: 2026-07-29
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/playbooks/research-topic.md
    - factory/playbooks/research-survey.md

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Research Workflow CLI Portability Audit

Status: implemented by ST-0063.

## Result

The research workflow is not structurally tied to Claude Code. Its briefs,
schemas, evidence policy, claim lifecycle, role separation, and reporting
contracts are CLI-neutral, and `init-factory` exposes the canonical research
agents and skills to Claude Code, GitHub Copilot CLI, Codex, and Pi.

The workflow was nevertheless **Claude-biased in its orchestration language**:
its efficiency proposal and dispatch convention named Claude models, assumed
native subagent fan-out, and did not state how source access or independent
sessions are verified on each CLI. These assumptions are fixable without
changing the research method.

## Evidence

| Surface                              | Finding                                                                                                                     | Disposition                                             |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Briefs, schemas, templates, policies | No CLI-specific fields or tools                                                                                             | Portable                                                |
| Research agents and skills           | Roles describe capabilities and artifacts, not vendor tools                                                                 | Portable                                                |
| Installed agent surfaces             | All four CLIs receive the canonical research agents; Codex receives generated native-agent adapters and Pi uses `run_agent` | Portable                                                |
| Dispatch economy guidance            | Named Opus, Sonnet, and Haiku instead of Factory tiers                                                                      | Corrected to economy, standard, and strong              |
| Research playbook dispatch           | Said “independent researchers” without a CLI mechanism or capability preflight                                              | Uses the CLI-portability contract                       |
| Survey design                        | Assumed cheap waves and a built-in deep-research shape without source-access checks                                         | Uses portable capabilities and explicit preflight       |
| Falsification independence           | Depends on genuinely separate identities, which Pi and Codex implement differently from Claude/Copilot                      | Stops when the active CLI cannot establish independence |

## Implemented contract

1. Dispatch logical requests using `agent`, `tier`, `task`, `output`, and
   `independent_session`; map the request to the active CLI at runtime.
2. Preflight source access for every mode and independent-session capability
   for falsification mode.
3. Give every concurrent assignment a unique output path.
4. Allow survey collection to fall back to sequential execution; never weaken
   falsification role separation.
5. Test the canonical research artifacts and installed discovery surfaces for
   Claude Code, Copilot, Codex, and Pi.

## Conclusion

The bias was real but localized: model names and dispatch assumptions, not the
research domain model. The canonical dispatch convention, falsification
playbook, survey portability shell, and orchestrator now apply the requirements
above. Acceptance tests also install Factory into a fresh consumer and verify
that Claude Code, GitHub Copilot CLI, Codex, and Pi expose the same canonical
research contracts through their supported discovery surfaces.
