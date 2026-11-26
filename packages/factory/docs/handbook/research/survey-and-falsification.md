---
title: Survey research and falsification research
type: concept
status: implemented
order: 10
description: The two research modes, when each fits, and how a survey leads to a falsification study.
---

# Survey research and falsification research

Research runs apart from the chain from idea to production. It has two modes, and the field `mode` of the shared research brief selects one:

- **Survey** is the default, when `mode` is missing or set to `survey`. [`research-survey.md`](../../../playbooks/research-survey.md) plans a bounded search for sources and produces a cited synthesis. Choose it for questions of landscape and discovery, such as "what exists?", where coverage and a sourced overview matter more than verdicts on claims.
- **Falsification** runs only with `mode: falsification`. [`research-topic.md`](../../../playbooks/research-topic.md) tests a few contestable, consequential claims through independent research, refutation, review, and voting. A claim that survives is not proved. It has only withstood the defined tests.

The research agents and their `research-*` skills drive both modes. Every artifact passes schema validation, then policy validation where it applies, then a semantic review, before the next step begins. [Validate a research artifact](validate-research-artifacts.md) shows the commands.

A survey can find claims that deserve stronger scrutiny, and it lists them under `candidates_for_deeper_falsification_study`. It never changes its mode by itself. Only a new research brief with `mode: falsification` starts a falsification study of such claims. The survey report then stays source context. It is not evidence that those claims already earned a falsification verdict.
