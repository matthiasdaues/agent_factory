# Agent Factory New-User Journey UX Review

Date: 2026-09-09

## Executive Summary

The core UX promise is strong: “Tell me what you want; I’ll choose a safe path,
make progress visible, and stop where your judgment matters.” The Factory is
most compelling once real work begins. Its largest weakness is the distance
between installation and that first proof of value.

## The Journey From Outside In

| Moment             | What I encounter                                                                            | What works                                                                                              | Where friction appears                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discovery          | A method for making AI-assisted development trustworthy                                     | Clear problem: AI is fast but noisy; small checked steps reduce risk                                    | “Agent Factory” initially sounds like infrastructure for building agents, not a development workflow                                                                |
| Installation       | Clone another repository, run `init-factory`, choose a CLI                                  | Reversible installation, guarded updates, and preservation of existing configuration inspire confidence | Running a repository script against my project is a large trust request before I have experienced any value                                                         |
| First hello        | The Factory detects the project and offers fitting                                          | Context-aware, resumable, and concrete: “3/5 done” is excellent                                         | Setup interrupts before I can explore. A curious new user meets a configuration gate instead of an immediate payoff                                                 |
| Orientation        | VIRGIL offers tour, start, direct execution, or open conversation                           | Intention-based navigation is excellent. I can speak in goals rather than Factory vocabulary            | The tour risks becoming documentation read aloud. “Agent,” “skill,” “playbook,” “gate,” and “context” arrive before I need all five                                 |
| First experiment   | `poc-spike` asks for one observable success condition and builds the smallest demonstration | This is the best onboarding device. Fast, safe, visible, and disposable                                 | It should be the obvious default path, but fitting and explanation can delay it                                                                                     |
| First real project | Brownfield onboarding creates architecture, scope, and vocabulary                           | “Enough to work” followed by optional deeper reverse engineering is excellent progressive commitment    | The prerequisites assume a healthier repository than many real brownfield projects have. “Tests pass” is often precisely what is not true                           |
| First feature      | Proposal → requirements → review → architecture → planning → implementation → QA            | Strong traceability, independent review, deterministic gates, and explicit approval points              | The full chain looks expensive. Users need a preview of which portions will run, why, approximate cost, and likely duration                                         |
| Everyday use       | Resume state, run shorter playbooks, ask “where am I?”                                      | Persistent artifacts make the work inspectable and recoverable                                          | State is spread across documents, Git, hidden runtime directories, fitting flags, handoffs, and sessions. The user lacks one canonical cockpit                      |
| Team adoption      | Repeat the method across projects and CLIs                                                  | Shared rules could make agent work predictable across a portfolio                                       | Much configuration and runtime state is local and ignored by Git. It is not immediately clear what is personal, what is portable, and what teammates must reproduce |

## What Feels Particularly Good

The best pattern is progressive rigor. A spike has almost none; a feature gets
more; safety-critical or architectural work gets the full chain. That is the
right product idea.

The author–reviewer separation is also excellent. “A different agent checks
the finished artifact in a clean session” is understandable, defensible, and
much more credible than vague claims about AI quality.

Other strong patterns:

- The menu begins with user intent, not implementation machinery.
- Work produces durable artifacts rather than disappearing into chat history.
- Gates are deterministic and separate from agent judgment.
- Fitting records progress and can resume later.
- Brownfield onboarding has an explicit “enough to work” exit.
- Updates detect local modifications and preserve them.
- Removal is supported; adoption does not feel irreversible.
- `docs/agent-context.md` asks agents to find project knowledge instead of
  duplicating or inventing it.

## What Does Not Feel Great

The onboarding currently asks the user to understand the Factory before
letting the Factory demonstrate itself.

The review conversation exposed this directly: the user asked for the journey,
the newcomer procedure first asked whether they had prior experience, “yes”
required another disambiguation, and only then did the conversation reach the
user’s actual intent. Each question was locally reasonable, but together they
became conversational toll booths.

There are also visible coherence seams:

- The guide emphasizes fully manual operation, while the README introduces an
  automated orchestrator “work in progress.” The user cannot yet form one
  stable mental model.
- Current material alternates between `docs/agent-context.md` and older
  `docs/agent-context/**/*.yaml` contracts.
- The feature playbook is comprehensive enough to look intimidating before
  its impact-based shortcuts are explained.
- Installation says only two tracked files change, but many hidden runtime
  integrations appear. Technically compatible statements can still feel
  emotionally inconsistent.
- Usage capture and transcript retention appear during installation, where
  privacy implications deserve a plain-language explanation.
- “Archive superseded documentation” during brownfield onboarding is
  alarming. Even if recoverable, it sounds like the tool may reorganize my
  repository before earning trust.
- The distinction between “the assistant,” “VIRGIL,” “an agent,” and “a skill”
  matters internally more than it matters to a beginner.

## Where I Would Expect Abandonment

The most dangerous interval is:

```text
Interest → install → hidden changes → fitting → terminology → first useful result
```

Every step before the useful result spends trust. The spike earns trust.
Therefore the shortest path should be:

```text
Install → inspect what changed → run a tiny spike → see it work → optionally fit the project
```

For an existing project, fitting can begin with a read-only preview:

> I found Python, uv, and pytest. Nothing will change yet. Try a five-minute
> demonstration, inspect the proposed setup, or configure the project now.

That gives the user agency without turning setup into a modal barrier.

## What Would Make Me Enthusiastic

I would become enthusiastic when the Factory gives me three sensations
quickly:

1. **Orientation:** I always know where I am, what is happening, and what comes
   next.
2. **Control:** I approve consequential decisions, while routine mechanics
   happen without repeated questioning.
3. **Accumulating trust:** Every run leaves the project easier for the next
   agent to understand and safer for a human to change.

Concretely, I would want:

- A five-minute “show me, don’t explain it” experience.
- A read-only installation preview listing every file and hook that will
  change.
- Before each playbook: expected outputs, human decisions, estimated agent
  runs, likely cost, and approximate duration.
- One status view showing current phase, completed artifacts, open findings,
  next decision, and recovery command.
- Adaptive ceremony: bug fix, small feature, structural feature, and
  safety-critical change should visibly take different routes.
- A first-class “messy project” path where tests may fail and documentation may
  contradict code.
- Clear privacy controls for transcripts and usage records.
- An easy explanation of which configuration belongs to the individual, the
  repository, and the team.
- Consistent artifact names and contracts throughout guides and playbooks.
- A satisfying completion report: what changed, what proved it works, what
  remains uncertain, and what the Factory learned about the project.

## North-Star Experience

> I describe an outcome in ordinary language. The Factory shows me the
> smallest credible route, explains the risk, and begins with a reversible
> step. I can inspect every meaningful artifact, interrupt at any point, and
> resume tomorrow without reconstructing the conversation.

The Factory already contains most of the machinery for that experience. The
opportunity is mainly editorial and interactional: hide the machinery until it
becomes relevant, move proof of value earlier, and unify progress into one
visible journey.
