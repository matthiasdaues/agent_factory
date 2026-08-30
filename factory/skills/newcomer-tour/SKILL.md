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

1. Ask whether the user has completed a `poc-spike`, created a project
   charter, or run a Factory playbook.
2. If yes, offer to skip ahead or start fresh. If no, begin the tour.
3. Read the full Getting Started section of `factory/docs/factory-guide.md`.
4. Cover its concepts in order, combining adjacent material when one
   explanation is enough.
5. For each concept:
   - Lead with the key idea in plain language.
   - Use at most two short paragraphs or one small list.
   - Define jargon before using it.
   - Avoid repeating earlier explanations.
   - Give an example only when useful or requested.
   - End with one brief invitation to continue or ask a question.
6. Pause after each concept. When the user says `continue` or equivalent,
   move on without a recap.
7. Stay above the reference-material seam in the guide. Route advanced
   questions to `explain-concept`.
8. Finish by offering `poc-spike`, questions, or routing to a playbook
   suited to the user's goal.

## Boundaries

- Calibrate detail to the user's experience.
- Prefer one clear sentence over a paragraph.
- Do not announce, preview, and repeat the same point.
- Do not praise every acknowledgement.
- Do not assume a charter exists.
- Do not reference `docs/arc42/beginner-intro.md`.
- Do not spawn agents or launch a playbook.

## References

- [Factory Guide — Getting Started section](../../docs/factory-guide.md)
- [Newcomer Tour Proposal](../../../docs/proposals/newcomer-tour-as-portable-skill.md)
