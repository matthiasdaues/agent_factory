# EARS Syntax

Disclosed reference for the `derive-spec` skill. Use EARS (Easy Approach to Requirements Syntax) for system use case requirements where a structured sentence pattern adds precision.

## Patterns

| Pattern          | Template                                                | When to use                            |
| ---------------- | ------------------------------------------------------- | -------------------------------------- |
| **Ubiquitous**   | The system shall [action].                              | Always-on behavior, no trigger needed  |
| **Event-driven** | When [event], the system shall [action].                | Response to a discrete event           |
| **State-driven** | While [state], the system shall [action].               | Behavior during a sustained condition  |
| **Optional**     | Where [feature is included], the system shall [action]. | Configurable or optional features      |
| **Unwanted**     | If [condition], then the system shall [action].         | Error handling, safety, recovery       |
| **Complex**      | While [state], when [event], the system shall [action]. | Combine state + event when both matter |

## Rules

- One requirement per sentence.
- Reference Business Rule IDs (BR-001) for validation logic rather than restating the rule.
- Each requirement gets a stable ID (e.g., SYS-001) for traceability.
