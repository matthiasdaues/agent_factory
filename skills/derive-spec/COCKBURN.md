# Cockburn's Fully Dressed Use Case Format

Disclosed reference for the `derive-spec` skill. Every persona use case must follow this structure.

## Template

```markdown
# UC-XX — [Title]

**Primary Actor**: [who initiates and has the goal]
**Scope**: [system or subsystem name]
**Level**: User Goal

## Stakeholders and Interests

- [Stakeholder]: [what they need from this use case]

## Preconditions

- [what must be true before the use case starts]

## Trigger

[the specific event that starts the use case]

## Main Success Scenario

1. [Actor does something]
2. [System responds]
3. …

## Extensions

- **3a.** [condition]: [what happens]
  1. [step]
  2. [step]

- **4a.** [condition]: [what happens]

## Postconditions

**Success Guarantee**: [system state after successful completion]
**Minimal Guarantee**: [system state even on failure — what is always true]

## Business Rules

- **BR-001**: [rule description]
- **BR-002**: [rule description]
```

## Rules

- **Primary Actor** has the goal — not the system, not a timer.
- **Main Success Scenario** is the happy path only. Keep it short — 3 to 9 steps.
- **Extensions** branch from specific step numbers (3a, 4b) and cover every path the activity diagram shows.
- **Postconditions** are what tests assert.
- **Business Rules** are numbered and stable — referenced by system use cases and validation rules downstream.
- **Subfunctions** are referenced by name, not inlined — written as separate use cases at Subfunction level.
