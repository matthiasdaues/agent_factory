---
title: Five kinds of work
type: concept
status: implemented
order: 30
description: Requirements, architecture, planning, implementation, and quality, and how each agent's needs set their order.
---

# Five kinds of work

When you move from spikes to real work, the factory organizes it into five kinds of activity:

1. **Requirements.** What are we building, and for whom? The assistant interviews you, sometimes stubbornly, until the answer is clear and written down.
2. **Architecture.** How will it be shaped? The big structural decisions are made on purpose and recorded before code fixes them.
3. **Planning.** The work is broken into a backlog of small, independent stories.
4. **Implementation.** Each story is built test-first. The test comes before the code, so the code has something to be checked against.
5. **Quality.** An independent review, a security pass, and a hunt for the bugs the earlier steps missed.

The typical dependency chain produces them in this order. The factory does not prescribe the order. It follows from what each agent needs before it can run. So the assistant asks for a specification before it writes code, because the developer agent needs one.

Each activity has an [author and a reviewer](author-and-reviewer.md), and you approve the handover between them. You do not have to run all five. Most real tasks, such as a bug fix, a small feature, or a cleanup of the documentation, use a shorter playbook with only the activities they need.

When work needs rework, you fix the artifact directly. Then you check again which agents can run. There is no return to an earlier phase. `intent select` shows which agents can run with the artifacts that exist, and you choose the next step.
