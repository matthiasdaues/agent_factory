# 0016. Dual-mode entry — a TUI presentation layer behind a MenuRenderer port

**Status**: Accepted

## Context

The direct-mode CLI is efficient for scripting and for operators who know the command surface, but it is not discoverable: `argparse` requires the operator to remember subcommands, phase names, flags, and when to use approve versus resume versus release (prd-tui-addendum §1). The v1.2.0 TUI specification adds an interactive menu that exposes the same capabilities through nested navigation, while direct mode must remain unchanged for automation (FR-V, constraint 4).

The risk is architectural, not cosmetic. A menu that grew its own dispatch, gate handling, or run-state logic would become a **second orchestration engine** — two code paths that could diverge in exit codes, gating, or state mutation (NFR-10). The design must also avoid committing prematurely to a terminal framework: the choice among `curses`, `blessed`, `prompt_toolkit`, and `textual` is unresolved (T-29) and constrained by the stdlib-first policy (NFR-12, ADR-0006).

### Alternatives (Pugh Matrix)

Baseline **A**: no TUI — direct mode only, discoverability left to `--help`. **B**: adopt a full TUI framework now and build screens directly against it, wiring each screen to services as needed. **C**: model the TUI as a thin presentation layer over the existing core — a `MenuController` in the core traversing the menu tree, a `MenuRenderer` port abstracting the terminal, and function leaves dispatching to the same services direct mode uses; the concrete framework stays behind the port.

| Criterion                                       | Weight | A: no TUI | B: framework now | C: presentation layer + port |
| ----------------------------------------------- | ------ | --------- | ---------------- | ---------------------------- |
| Discoverability / operability (Q4)              | 3      | -1        | +1               | +1                           |
| Behavioural equivalence, one engine (NFR-10)    | 3      | 0         | 0                | +1                           |
| Core portability + testability (Q5)             | 2      | 0         | -1               | +1                           |
| Direct-mode stability (constraint 4)            | 2      | +1        | 0                | +1                           |
| Minimal dependencies, framework deferrable (Q7) | 1      | +1        | -1               | +1                           |
| **Weighted total**                              |        | **0**     | **+1**           | **+11**                      |

C wins. Building directly against a framework (B) both takes a dependency the policy has not yet accepted and invites screen-local logic that drifts from direct mode. The presentation-layer approach keeps one engine and defers the framework behind a seam.

## Decision

1. **Dual-mode entry at the composition root.** A bare `orchestrate` on an interactive terminal enters menu mode; any subcommand runs direct mode unchanged (FR-V1, FR-V2). The entry point inspects the argument vector and the terminal, then dispatches to the `Command Dispatcher` or the `MenuController`.

2. **`MenuController` lives in the core.** It traverses the menu tree defined by `cli_specification.md`, holds the navigation state (root → submenu → display → executing → exited, per `state-machines.md`), and dispatches every function leaf to the **same application service its direct-mode command uses** (FR-V3). Long-running leaves exit the TUI before streaming begins (FR-P7).

3. **`MenuRenderer` is a port.** It renders one menu or display node at a time and returns normalised `KeyEvent`s; the concrete terminal framework is deferred (T-29) and must honour the stdlib-first policy (NFR-12). A non-interactive or unsupported terminal never enters menu mode and receives a direct-mode diagnostic (FR-V4, T-30).

4. **Navigation mutates no run state.** Cursor movement, menu entry, back navigation, display viewing, and exit leave `run.json`, findings, and logs untouched; only a dispatched leaf may change them (VR-030).

## Consequences

**Positive**

- The command surface becomes discoverable without a second orchestration engine; direct mode is untouched, so scripts and tests keep working (Q4, constraint 4).
- The core stays terminal-agnostic and unit-testable: the `MenuController` is exercised against a fake `MenuRenderer`, with no real terminal (Q5).
- The framework decision (T-29) can be made — or changed — later without touching the core, exactly as new CLIs plug in behind `CLIAdapter`.

**Negative / risks**

- Terminal-compatibility handling is real work confined to the renderer adapter (R-7); arrow-key sequences and cursor control vary across terminals.
- Two entry paths share one core, so a service invoked from a leaf must not assume a direct-mode-only context; the equivalence is a property to test (QS-18), not a given.
- The deferred framework leaves a visible gap between "specified" and "runnable" until T-29 closes.
