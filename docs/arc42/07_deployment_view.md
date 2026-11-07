[back to index](../README.md)

# 7. Deployment View

## 7.1 Release 1: Local Operator Workstation

Release 1 runs inside one project checkout on one operator workstation. There
is no database server, container, daemon, or cloud resource. The one remote
that Release 1 needs is the project's own git remote, for ID allocation.

![Local release-1 deployment](../assets/images/Deployment.svg)

The project checkout contains three independent runtime boundaries:

- **Workstream state** under `.agent-factory/workstreams/` holds immutable
  workstream identity files. Session bindings under
  `.agent-factory/workstreams/sessions/<session-id>.yaml` record
  session-to-workstream mappings. The Eligibility Engine reads agent
  definitions and the repository; it has no separate model file.
- **`.agent-factory/usage/`** holds Factory-owned, append-only JSONL evidence.
  Capture writes here whether or not analysis is installed.
- **`.agent-factory/usage-analysis/`** is the opt-in component installed by
  `init-factory`. It contains the Python package, locked DuckDB and PyArrow
  dependencies, SQL query model, accounting registry, and installed copy of
  the usage-record contract.

The Eligibility Engine runs in-process within the `intent select` command
invocation. It evaluates agent preconditions against the repository and
returns immutable readiness verdicts. There is no long-running engine process
and no state written by the engine.

The operator starts a query with
`uv run --project .agent-factory/usage-analysis usage-query`. The embedded
DuckDB runtime and all registered relations live in that process. A complete
dependency cache supports network-disabled execution after dependencies have
been cached. The optional DuckDB UI is an ephemeral localhost process and may
fetch its own assets when the operator opens it; it is outside deterministic
analysis and gate execution.

An explicit Parquet destination may be anywhere the operator selects. It is a
verified, attributable export and remains outside the authoritative
`.agent-factory/usage/` evidence boundary.

The ID Allocation container runs as the script `next-id` on the workstation.
It creates a throwaway bare repository in a new temporary directory for each
call, pushes the claim to `refs/ids/counters` on the project's git remote, and
deletes the directory at exit. So a session that cannot reach the remote cannot
create a story, finding, todo entry, or ADR. The
[Deployment](../assets/images/Deployment.svg) view shows the container on the
workstation. The remote itself is outside the Factory's deployment.

Finding classification adds no process. `finding-lint`, the stop check in
`dispatch`, and `premerge-check` run as scripts in the checkout. The Finding
Registers and Factory Settings are tracked files under `docs/`, and the
Finding Schemas ship with the Factory as
`packages/factory/rulebooks/schemas/finding-register-<class>.schema.json`
(BR-090). `guard-human-fields` runs in the process of each CLI hook.
`init-factory` writes the guard entries of Claude Code, Codex, Copilot CLI,
and Pi beside the `step-guard` entries. In OpenCode, `init-factory --cli opencode` links the plugin `agent-factory.ts` into `.opencode/plugins/`, and
OpenCode loads it at session start.

`finding-lint` reaches a project as the pre-commit hook
`agent_factory_hook-finding-lint` in
`packages/factory/config/pre-commit-config.yaml`. Its entry in
`packages/factory/config/hook-metadata.yaml` is `trade_off: none` and
`availability: always`, so fitting includes it without
asking. A project that finished its fitting earlier gets the hook from
`update-factory`. The update re-splices the `agent_factory_hook-*` block of
`.pre-commit-config.yaml` from the template of the new release and writes it
on a yes. It also runs `init-factory` of the new release, which adds the
missing guard entries.

## 7.2 Lifecycle Boundaries

`init-factory --with-usage` and `init-factory --add usage` install the analysis
module without changing raw evidence. `init-factory --update usage` replaces
only a compatible component. `init-factory --remove usage` removes only the
component and its manifest entry. `update-factory` updates Factory core and
reports component presence without updating components.

`remove-factory` remains the complete-uninstall operation: it removes both the
analysis module and the raw usage data beneath `.agent-factory/`.

Workstream state files under `.agent-factory/workstreams/` are local,
git-ignored working state. They survive Factory updates and are removed only
by explicit operator action or `remove-factory`.

## Referenced from

- [architecture.dsl](../spec/architecture.dsl) -- canonical `Deployment` view
- [ADR-0015 -- Query authoritative JSONL with ephemeral DuckDB views](../adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md)
- [Interface contracts section Usage-analysis component lifecycle](../spec/interface-contracts.md#usage-analysis-component-lifecycle)
