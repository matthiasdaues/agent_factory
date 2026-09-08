---
name: newcomer-tour
description: >-
  Give first-time Agent Factory users a short, interactive orientation when
  they choose option A or ask to be shown around
category: onboarding
version: 1.0.0
---

# Newcomer Tour

Orient newcomers warmly and briefly.

## Procedure

01. Ask whether the user has completed a `poc-spike`, set up agent context,
    or run a Factory playbook.

02. If yes, offer to skip ahead or start fresh. If no, begin the tour.

03. Read the full Getting Started section of `factory/docs/factory-guide.md`.

04. Cover its concepts in order, combining adjacent material when one
    explanation is enough.

05. For each concept:

    - Lead with the key idea in plain language.
    - Use at most two short paragraphs or one small list.
    - Define jargon before using it.
    - Avoid repeating earlier explanations.
    - Give an example only when useful or requested.
    - End with one brief invitation to continue or ask a question.

06. Pause after each concept. When the user says `continue` or equivalent,
    move on without a recap.

07. After the Getting Started walkthrough, cover **what init-factory put
    on their disk** — briefly explain the three configuration artifacts:

    - `config/project.json` — project identity (UUID, name, test command).
      Created at install. Rarely edited by hand.
    - `config/model.conf` — the model matrix. Maps agent tiers (economy,
      standard, strong) to AI model ids per CLI. Configured during fitting
      or by editing the file directly.
    - `docs/agent-context.md` — does not exist yet. Created during fitting
      via `capture-context`, which scans the repo and proposes concerns
      (cross-cutting, technical, domain) for agent routing.

    Keep this to one short explanation per artifact. The point is awareness,
    not mastery.

08. Mention the **fitting**: if the project has an existing codebase,
    VIRGIL offers a fitting walk-through that configures the model matrix,
    confirms the detected stack, populates agent context, and reviews
    pre-commit hooks. Greenfield projects skip it by default but can
    return to it later. The user does not need to do anything with this
    information now — just know it exists.

09. Stay above the reference-material seam in the guide. Route advanced
    questions to `explain-concept`.

10. Finish by offering `poc-spike`, questions, or routing to a playbook
    suited to the user's goal.

## Boundaries

- Calibrate detail to the user's experience.
- Prefer one clear sentence over a paragraph.
- Do not announce, preview, and repeat the same point.
- Do not praise every acknowledgement.
- Do not assume agent context or a charter exists.
- Do not reference `docs/arc42/beginner-intro.md`.
- Do not launch a playbook directly -- offer it and let the session menu handle the transition.

## References

- [Factory Guide — Getting Started section](../../docs/factory-guide.md)
- [Newcomer Tour Proposal](../../../docs/proposals/newcomer-tour-as-portable-skill.md)
