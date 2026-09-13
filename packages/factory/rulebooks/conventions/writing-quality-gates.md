# Writing Quality Gates

Three gates apply to every persistent prose artifact the factory produces.
Run them at the end of every authoring phase, not just the final one.

## Junior Clarity / Senior Acceptance

Two complementary lenses. Both must pass before the artifact leaves the gate.

**Junior Clarity.** Read the artifact as someone encountering it cold. Can
you start working from it right now — do you know what it delivers, where
to begin, what "done" looks like, and what every unresolved question is,
without consulting the author? If not, the artifact is underspecified.

**Senior Acceptance.** Read the artifact as a senior responsible for the
next step. Would you hand it to your team without a follow-up conversation
— is the scope bounded, the demonstration concrete, every criterion
testable, and nothing left to interpret? If not, the artifact is not ready.

A junior pass with a senior failure means the artifact is understandable
but insufficiently decided. A senior pass with a junior failure means it
is bounded but not navigable.

## Agent-Answerability

A structured artifact (story, proposal, spec) fails this gate if any
applicable check cannot be answered from the artifact alone:

| Check                                | Answered by                   |
| ------------------------------------ | ----------------------------- |
| What behavior must exist after?      | Goal / Summary                |
| Which files change?                  | Affected Paths / Scope        |
| Which domain rule owns the behavior? | Domain Rule / Motivation      |
| What existing state matters?         | Inputs / Context              |
| What should tests prove?             | Acceptance / Completion       |
| What commands verify completion?     | Verification                  |
| What is explicitly out of scope?     | Out of Scope / Deferrals      |
| When should the agent stop and ask?  | Agent Stop Conditions / Risks |
| What contract decisions remain open? | Resolve Before Implementation |

Not every artifact type has all nine sections. Apply the checks that map
to the artifact's structure — the principle is self-containedness, not a
rigid section checklist.

## International Readability

Six sentence-level checks on all prose sections:

1. No idioms, slang, or culture-specific metaphors.
2. No ambiguous pronouns across sentence boundaries. Repeat the noun.
3. Short sentences (under 25 words). One idea per sentence.
4. Active voice.
5. Domain terms are used consistently — one term per concept, never
   alternated with synonyms for variety.
6. Abbreviations are spelled out on first use within the artifact, even
   when defined elsewhere.

If any sentence fails, rewrite it before the artifact leaves the gate.
