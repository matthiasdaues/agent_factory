---
title: Proof-of-Concept Spike Playbook
category: orchestration
type: runbook
scenario: poc-spike
version: 1.0.0
---

# Proof-of-Concept Spike Playbook

Operational procedure for **getting from an idea to something you can look at and see run** — in minutes, not phases.

This is the deliberate opposite of the other playbooks. There is no spec, no architecture, no backlog, no agent chain, and no gate. Skipping all of that is the point: a spike answers one question — "does this basic idea even work, and what does it look like?" — and nothing else. Throw the result away by default. Only promote it if it earns a real playbook.

## Prerequisites

- [ ] One idea, statable in a single sentence
- [ ] Nothing else

## Step 1 — State the Success Condition

Write one sentence describing exactly what "it runs" means — the thing you will look at, click, or run, and the change you expect to see. If you can't state it in one sentence, the spike is too big; narrow it until you can. In a CLI session, the [`scratchpad`](../skills/scratchpad/SKILL.md) skill is the right weight for capturing it — one line, no file to manage afterward.

Example: "A page shows a red button; clicking it turns the page background blue."

## Step 2 — Build the Smallest Thing That Could Show It

No agent runs this step. [`developer-agent`](../agents/developer-agent.md) is the closest fit in the catalog, but it exists for TDD against a backlog story with spec traceability — exactly the ceremony a spike exists to skip. Build it yourself, in whatever CLI session you're already in.

Pick whatever gets you to the success condition fastest — a single file is normal, a full project is a smell. Don't:

- Add a framework, build step, dependency, or test unless the success condition literally cannot be shown without it
- Handle any case beyond the one in Step 1 (no error handling, no edge cases, no config)
- Write a spec, ADR, backlog story, or commit message beyond a one-line description

Do:

- Write the whole thing in one sitting, one file if at all possible
- Prefer the platform's own primitives over a library ("just HTML/CSS/JS" beats "React app")

Example implementation for the success condition above — a single file, no build step:

```html
<!doctype html>
<button onclick="document.body.style.background='blue'">Turn background blue</button>
```

## Step 3 — Run It and Look

Open it, run it, click it — whatever "run" means for this artifact. Compare what you see against Step 1's sentence.

**Matches** → go to DONE.
**Doesn't match** → fix the smallest thing standing in the way and look again. Do not add scope while fixing — if the gap reveals the idea needs more than a spike, stop and go to DONE anyway; that's a real finding too.

## DONE

✅ **Idea demonstrated (or shown not to work) — that was the only goal**

- [ ] Success condition from Step 1 was checked by eye, not assumed
- [ ] Nothing was built beyond what Step 1 required

Three ways forward, pick one:

1. **Idea confirmed, worth building for real** → hand off to [feature-addition](feature-addition.md) (existing system) or the full requirements → architecture → planning chain (new system). Nothing from the spike carries over automatically — re-derive requirements properly; the spike was a sketch, not a foundation.
2. **Idea confirmed, but this exact throwaway is still useful to keep around for reference** → commit it as-is, clearly marked (e.g. a `spikes/` or `poc/` directory), with no expectation it is maintained or gated.
3. **Idea didn't hold up** → delete it. A spike that fails fast and gets discarded is a successful spike, not a wasted one.
