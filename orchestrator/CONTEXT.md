# CONTEXT — Agent Session Orchestrator

Domain glossary for the orchestrator project. This is a glossary only — no implementation detail. All agents read it; keep terminology consistent with `docs/spec/`.

## Terms

- **Orchestrator** — the thin Python CLI that drives the `ai_tooling` agent chain, running steps or the whole chain with deterministic gates and human approval at phase gates.
- **Phase** — one unit of the chain, with an **author agent** and an **optional reviewer agent**. The four phases: requirements, architecture, planning (no reviewer), implementation.
- **Author agent** — the agent that produces a phase's artifacts (e.g. `requirements-agent`).
- **Reviewer agent** — the agent that independently reviews a phase's artifacts in a fresh session (e.g. `spec-review-agent`). A phase may have none.
- **Session isolation** — running each agent in a fresh CLI subprocess with no inherited context, so a reviewer never sees the author's reasoning.
- **CLI adapter** — the abstraction that lets the orchestrator drive any AI CLI (Copilot first; Claude, Gemini later) through one `invoke` contract.
- **Gate** — the deterministic check between steps, run via **pre-commit** hooks on the phase's commit. Blocks only on error-severity findings.
- **spec-lint** — the deterministic spec linter used as the requirements phase's gate hook.
- **Finding** — a single reviewed defect, stored as one validated JSON file. Has a `source` (`spec-lint` or `semantic`), `severity`, `iteration`, and `status` (`open`, `superseded`, `resolved`).
- **Findings store** — the local, file-per-finding directory that is the source of truth for loop state (external ticket tools deferred).
- **Iteration** — one author→gate→review cycle within a phase.
- **Loop-back** — re-running the author with the open findings; bounded by the **cap** (default 3), after which the run **halts**.
- **Supersede** — at the start of each iteration, the prior iteration's open findings are marked `superseded` so the loop can terminate.
- **Run** — one execution of a phase or the chain, tracked in `.orchestrator/run.json`, isolated by a **run lock** on a dedicated **run branch**.
- **Awaiting-approval** — the persisted state a clean phase reaches; the orchestrator exits and the human runs `approve`/`reject`.
- **Phase gate** — the human sign-off point at a phase boundary; the judgment a linter cannot make.
- **Halt** — a safe stop (cap exhausted, gate error, adapter-auth failure, adapter-config failure, rejection) that summons the human rather than proceeding.
- **Backlog** — the set of planned stories the planning phase produces, held locally as human-readable artifacts rather than in an external tracker.
- **Story** — one planned unit of implementation work, sized to INVEST; the item the planning phase emits and the implementation phase consumes.
- **Tier** — an abstract model-strength band, `economy | standard | strong`, judged directly by whoever declares it (an agent's own frontmatter, or a story's own frontmatter during planning); a tier resolves to a concrete model for the CLI in use.
- **model.conf** — the operator-curated tier router: per-CLI `[facts]` mapping each tier to a concrete model, plus `on_missing`. No policy layer — a tier is either configured for the active CLI or it isn't.
