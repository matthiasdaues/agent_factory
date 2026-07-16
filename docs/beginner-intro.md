# A Beginner's Introduction to Agent Factory

The doorway to Agent Factory for a first-time user — of the factory, or of any AI
coding workflow. Read it start to finish, once, before you touch a single
command. The [`factory/README.md`](../factory/README.md) and
[factory guide](../factory/docs/factory-guide.md) are references you return to
afterward; this page is the one you walk through first.

## Who this is for

You have an idea for something to build. You have an AI coding assistant — a
tool like Claude Code or GitHub Copilot CLI that reads and writes files and runs
commands in a terminal. What you do not yet have is a *way of working* with it
that produces code you would trust in production.

That is the whole problem Agent Factory solves. You do not need to be a
professional software engineer to follow along. You do need to be willing to
read what the assistant proposes and say yes or no to each step.

## The one idea to hold onto

**You are the boss. The assistant does the work. You approve each step.**

Everything else is detail. Agent Factory never runs off and builds the whole
thing while you look away. It works in small, visible moves, and it stops to show
you each one. If a move looks wrong, you say so, and it tries again. This is
deliberate: an AI is a fast but noisy worker, and the cure for noise is frequent,
cheap checking — by a tool, a test, or you.

## The four words you will keep hearing

Agent Factory hands your assistant four kinds of things. Learn these four words
and the rest of the documentation stops feeling foreign.

| Word         | Plain meaning                                                                    | Everyday analogy                                   |
| ------------ | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Agent**    | One *job* — "write the requirements," "review the architecture," "fix one bug."  | A specialist you hire for one task.                |
| **Skill**    | One *how-to* an agent follows to do a job well.                                  | The written procedure the specialist works from.   |
| **Playbook** | A *recipe* — which agents to run, in what order, for a common situation.         | The plan for the whole job, start to finish.       |
| **Gate**     | An *automatic check* that catches mistakes before you waste time reviewing them. | The quality inspector who won't let bad work pass. |

You never memorise the full list. Your assistant reads a catalogue —
[`INDEX.yaml`](../factory/INDEX.yaml) — and picks the right agent or skill for
what you asked. Your job is to know *that these things exist* so you understand
what the assistant is doing when it says "I'll use the requirements agent now."

## Two ways to run it — and why you start by hand

Agent Factory has two modes, and the difference between them is simply *who turns
the crank.*

- **Manual mode** is where every beginner starts. You drive a playbook yourself,
  one step at a time. Each step ends with a set of defined artifacts — a
  specification, an architecture document, a slice of code — and those artifacts
  are the visible marker that the step is done. You read them, you decide whether
  the work is good, and you start the next step. Nothing moves without you.
- **Automatic mode** is where you go once you trust the process. An optional
  companion tool, the **orchestrator**, does the one thing you were doing by hand
  between steps: it presses "enter." It reads the playbook, runs the next agent,
  checks the gate, and moves on — pausing wherever a step genuinely needs a human
  decision.

Do not reach for automatic mode yet. You cannot trust a process you have never
watched run. Turn the crank by hand first — a few times, on small tasks — until
the rhythm is familiar and the gates have earned your confidence. The move to
automatic is a graduation, not a shortcut.

## Why two agents, not one

The single most important habit Agent Factory builds in is this: **the worker and
the checker are never the same agent.**

When one agent writes a specification, a *different* agent reviews it — in a fresh
session, without ever seeing the first agent's reasoning. It sees only the
finished document, the way a stranger would. This is the same reason you don't
approve your own expense report or review your own pull request. You cannot catch
the mistake you cannot see, because the same blind spot that made it hides it.

In manual mode, *you* are what makes this real. When the requirements, architecture,
or developer agent finishes and hands you its artifacts, you open a **second, clean
session** and start the matching reviewer there — pointed at those artifacts and
nothing else. The blank session is the isolation: the reviewer cannot lean on a
conversation it never had. Author then reviewer, write then check — and in manual
mode, a fresh window between the two.

## Your very first session

Do the setup once, following [`factory/README.md`](../factory/README.md) — it
lists the handful of tools you need and the one script that wires everything up.
When it is done, open your AI assistant in your project folder and say hello. It
should greet you back and confirm it has read the project's rules. That handshake
means the factory is live.

Now try the gentlest possible task. Tell your assistant:

> "Let's run the poc-spike playbook. I want to see if \<your rough idea> is
> even worth building."

`poc-spike` — "proof-of-concept spike" — is the training-wheels playbook. No
specification, no architecture, no formal checks. One idea, turned into one small
thing you can run, in minutes. It exists so you can watch an agent and your
assistant work together *before* you commit to anything real. What you throw away
here cost you almost nothing.

Watch what happens:

1. The assistant reads the playbook and tells you the steps it plans to take.
2. It writes a small amount of code — and shows it to you.
3. It runs it, and you see the result.
4. You react. "Yes, keep going," or "No, that's not what I meant."

That back-and-forth *is* Agent Factory. Everything larger is the same loop, with
more rigour bolted on.

## The bigger picture: five phases

When you graduate from spikes to real work, Agent Factory drives your assistant
through five phases, in order. Think of it as a production line that turns a rough
idea into finished code:

1. **Requirements** — What are we actually building, and for whom? The assistant
   interviews you, sometimes stubbornly, until the answer is clear and written
   down.
2. **Architecture** — How will it be shaped? The big structural decisions, made on
   purpose and recorded, before any code locks them in.
3. **Planning** — The work broken into a backlog of small, independent stories.
4. **Implementation** — Each story built test-first: the test comes before the
   code, so the code has something to prove itself against.
5. **Quality** — Independent review, a security pass, and a hunt for the bugs the
   earlier steps missed.

Each phase has an author and a reviewer, and you approve the handover between
them. You do not have to run all five. Most real tasks — a bug fix, a small
feature, a documentation cleanup — use a shorter playbook that touches only the
phases it needs.

## Which playbook, when

Once the first spike feels comfortable, pick the recipe that matches your
situation. You do not choose the agents yourself; the playbook does. You just
choose the playbook.

| You want to…                                           | Start with               |
| ------------------------------------------------------ | ------------------------ |
| See whether a rough idea works at all                  | `poc-spike`              |
| Fix one reported bug                                   | `bug-fix`                |
| Bring the docs back in line with the code              | `documentation-update`   |
| Build a brand-new project properly, start to finish    | `greenfield-development` |
| Add Agent Factory to code that already exists          | `brownfield-onboarding`  |
| Add a feature to a project the factory already manages | `feature-addition`       |

The full list, with a sentence on each, lives in the
[factory guide § Playbooks](../factory/docs/factory-guide.md#playbooks).

## Graduating to automatic mode

After you have run a few playbooks by hand, the between-steps work starts to feel
like a chore rather than a decision. You check the artifacts, you open the next
session, you check the gate, you advance — the same turns, every time. That
feeling is the signal you are ready for the orchestrator.

The [orchestrator](../orchestrator/README.md) replaces exactly that manual
crank-turning and nothing more. It reads the playbook, dispatches the next agent,
waits, checks the gate, and steps forward — the same scripts you were running by
hand, run for you. It still stops where a human genuinely belongs: the
requirements phase is always yours to drive, and any step that needs your approval
pauses until you give it. You lose none of the control; you lose only the
repetition.

Two things worth knowing before you rely on it:

- **It is still maturing.** Treat automatic mode as a capable assistant you
  supervise, not an autopilot you leave alone. The audit log it writes lets you
  see exactly what ran and how long each step took.
- **You can teach it your own recipes.** A playbook the orchestrator can drive is
  described by a small state-machine file (a `.fsm.yml`) that lists each phase's
  expected artifacts and the conditions to advance. Once you understand the built-in
  playbooks, writing your own custom playbook for the orchestrator to follow is the
  natural next step — your process, automated on your terms.

## Three habits that keep you safe

1. **Read before you approve.** The assistant will always show you its move. Slow
   down enough to actually read it. Your "yes" is the last gate, and it is the one
   that matters most.
2. **Let the gates do their job.** When a check blocks a commit or a test fails,
   that is the system working, not the system breaking. Fix the cause; don't route
   around the alarm.
3. **One small step at a time.** Resist "just build the whole thing." Small,
   checked steps are how the noise gets corrected before it compounds. This is not
   slower in the end — it is how you avoid the day-long detour.

## Where to go next

- Set up the tooling: [`factory/README.md`](../factory/README.md)
- Understand each piece in depth: [factory guide](../factory/docs/factory-guide.md)
- Hand over the crank: [orchestrator](../orchestrator/README.md)
- The ideas underneath it all: [`docs/concepts.md`](concepts.md)

You do not need any of these to start. Run one `poc-spike`, watch the loop, and
come back for the rest when you are curious. The factory rewards learning by
doing.
