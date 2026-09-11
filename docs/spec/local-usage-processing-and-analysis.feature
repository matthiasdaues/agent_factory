Feature: Local usage processing and analysis
  The local operator derives reproducible usage answers from retained JSONL evidence
  without operating a database service, reading transcripts, or changing capture.

  Rule: Local operator queries only published views over a fixed local input set
    # actor: Local operator

    Scenario: Default input selection is local and deterministic
      Given a project contains top-level JSONL files under ".agent-factory/usage/"
      And transcript and lifecycle files exist only in subdirectories
      When the operator invokes "uv run --project .agent-factory/usage-analysis usage-query" for a published view
      Then the query snapshots the sorted top-level JSONL paths at query start
      And the query excludes every subdirectory
      And the query performs no network request

    Scenario: Explicit input directory overrides the default
      Given a directory contains a selected set of top-level JSONL usage files
      When the operator invokes a published view with "--usage-dir" set to that directory
      Then the query uses only the sorted top-level JSONL files in that directory

    Scenario: Six views form the stable query surface
      Given the selected input set passes preflight
      When the operator lists the stable query surface
      Then it contains exactly "raw_usage_snapshots", "latest_run_snapshots", "canonical_session_usage", "usage_by_dimension", "cache_efficiency", and "capture_health"
      And stable table, JSON, and export outputs read only those published views

    Scenario: Empty usage directory returns typed empty results
      Given the selected usage directory contains no top-level JSONL files
      When the operator queries any published view
      Then the query succeeds with that view's declared empty schema

    Scenario: File enumeration order does not affect results
      Given two queries select the same JSONL files in different enumeration orders
      When both queries produce sorted logical rows
      Then the logical rows and content digest are identical

  Rule: Local operator obtains conservative canonical usage without duplication
    # actor: Local operator

    Scenario: Latest run snapshot uses deterministic evidence identity
      Given a logical run has cumulative snapshots with source file and line identity
      When "latest_run_snapshots" selects the canonical snapshot
      Then it selects the greatest capture sequence
      And equal capture sequences use the declared deterministic source-position tie-breaker

    Scenario: Claude Code conserves root and distinct children
      Given a Claude Code session has repeated root snapshots and duplicate child evidence
      When "canonical_session_usage" computes the session total
      Then it adds the latest root snapshot and each distinct child run exactly once

    Scenario: Pi conserves root and distinct descendants
      Given a Pi session has a root record and nested descendant runs
      When "canonical_session_usage" computes the session total
      Then it adds the root record and each distinct descendant run exactly once

    Scenario: Codex uses the inclusive root total
      Given a Codex session has an inclusive root snapshot and child attribution records
      When "canonical_session_usage" computes the session total
      Then it uses the latest inclusive root snapshot as the session total
      And it does not add child attribution records to that total

    Scenario: GitHub Copilot CLI uses the inclusive root total
      Given a GitHub Copilot CLI session has an inclusive root snapshot and child attribution records
      When "canonical_session_usage" computes the session total
      Then it uses the latest inclusive root snapshot as the session total
      And it does not add child attribution records to that total

    Scenario: Unknown CLI is a contract error
      Given a valid usage record names a CLI outside the closed accounting registry
      When canonical accounting begins
      Then the query exits non-zero and names the unsupported CLI

    Scenario: Dimensional totals remain additive
      Given canonical session rows contain time, project, CLI, provider, model, agent, branch, and exit status dimensions
      When "usage_by_dimension" groups by any supported dimension set
      Then each reported measure equals the additive total of its canonical session rows

    Scenario: Cache signals preserve unavailable states
      Given provider-qualified cache fields are unavailable or input-only
      When "cache_efficiency" reports those fields
      Then it preserves their declared null or input-only state
      And it does not coerce unavailable values to zero

  Rule: Local operator diagnoses all invalid evidence before accounting
    # actor: Local operator

    Scenario: Preflight classifies every selected line
      Given the selected files contain valid, malformed, truncated, wrong-type, and invariant-breaking lines
      When strict preflight runs
      Then every line appears in exactly one query-scoped valid or failure relation
      And each failure reports source file, line number, field, and stable failure code

    Scenario: Health remains available for an invalid selected set
      Given strict preflight records at least one failure
      When the operator queries "capture_health"
      Then the view reports valid counts and failures grouped by failure code and source file

    Scenario: Stable analytical views refuse partial results
      Given strict preflight records at least one failure
      When the operator queries a published view other than "capture_health"
      Then the query exits non-zero before accounting runs
      And it emits no partial stable result

    Scenario: Diagnostic mode labels incomplete evidence
      Given strict preflight records at least one failure
      When the operator requests diagnostic mode
      Then the result identifies valid and invalid lines as incomplete
      And diagnostic mode cannot emit a stable export

  Rule: Local analyst consumes typed table, JSON, relation, and Arrow results
    # actor: Local analyst

    Scenario: Table and JSON preserve the selected view
      Given a published view returns typed rows containing null values
      When the analyst requests table or JSON format
      Then the output represents the same logical rows, field types, and null states as the view

    Scenario: Programmatic conversions preserve the selected view
      Given a published view returns typed rows containing null values
      When Python requests a DuckDB relation or PyArrow table
      Then the result preserves the same schema, logical rows, and null states as the view

    Scenario: Deferred dataframe formats are unavailable
      Given release 1 has no Pandas or Polars dependency
      When a caller requests a Pandas or Polars conversion
      Then the interface rejects the unsupported format without changing the SQL model

  Rule: Local operator exports attributable Parquet without damaging prior output
    # actor: Local operator

    Scenario: Successful export round-trips the published view
      Given a published view succeeds for a valid selected input set
      When the operator requests Parquet with an explicit output path
      Then the export writes a temporary sibling and verifies its rows and schema
      And the export records query-model version and input-set digest as provenance
      And the verified temporary file atomically replaces the destination

    Scenario: Interrupted export preserves the prior destination
      Given a valid Parquet destination already exists
      When a replacement export is interrupted or fails its round-trip check
      Then the command exits non-zero
      And the prior destination remains unchanged

    Scenario: Parquet remains an explicit rebuildable export
      Given retained JSONL is the authoritative evidence
      When no operator requests a Parquet export
      Then no scheduled, incremental, or automatically refreshed Parquet state is created

  Rule: Local analyst explores published views through DuckDB's bundled UI
    # actor: Local analyst

    Scenario: UI opens the same published query model
      Given the usage-analysis component is installed
      When the analyst follows the documented DuckDB UI launch path
      Then the UI exposes the six published views for ad hoc local SQL
      And it does not supply repository-owned dashboard formulas or saved charts

    Scenario: UI bootstrap is outside deterministic analysis
      Given DuckDB UI assets are absent or cannot be fetched
      When deterministic query and accounting gates run
      Then the gates complete without installing or starting the UI

  Rule: Project maintainer manages the opt-in usage-analysis component without accidental data loss
    # actor: Project maintainer
    # @packages/factory/scripts/init-factory
    # @packages/factory/scripts/update-factory
    # @packages/factory/scripts/remove-factory

    Scenario: Initial opt-in installs the analytical component
      # @packages/factory/scripts/init-factory
      Given a target project has no usage-analysis component
      When the maintainer initializes Factory with "--with-usage"
      Then ".agent-factory/usage-analysis/" contains the self-contained module and installed contract copy
      And "factory-install.json" records "usage" under "installed_components"
      And ".agent-factory/usage/" remains untouched

    Scenario: Post-hoc add installs the analytical component
      # @packages/factory/scripts/init-factory
      Given Factory is installed without usage analysis
      When the maintainer runs "init-factory --add usage"
      Then the component and manifest entry match an initial opt-in installation

    Scenario: Compatible component update preserves evidence
      # @packages/factory/scripts/init-factory
      Given usage analysis is installed with a contract version accepted by the replacement module
      When the maintainer runs "init-factory --update usage"
      Then only the installed component is replaced
      And its install metadata records the new source version
      And raw usage evidence, Factory core, and CLI wiring remain unchanged

    Scenario: Incompatible component update aborts before replacement
      # @packages/factory/scripts/init-factory
      Given the replacement module does not accept the installed contract version
      When the maintainer runs "init-factory --update usage" without a force option
      Then the command exits non-zero with a compatibility diagnostic
      And the installed component and raw usage evidence remain unchanged

    Scenario: Component removal preserves evidence and capture
      # @packages/factory/scripts/init-factory
      Given usage analysis and raw usage evidence are present
      When the maintainer runs "init-factory --remove usage"
      Then the installed component and its manifest entry are removed
      And raw usage evidence remains unchanged
      And capture can append another usage record

    Scenario: Factory core update leaves components alone
      # @packages/factory/scripts/update-factory
      Given usage analysis is installed
      When the maintainer runs "update-factory"
      Then Factory core may be refreshed
      And the installed usage-analysis component remains unchanged

    Scenario: Full Factory removal retains complete-uninstall semantics
      # @packages/factory/scripts/remove-factory
      Given Factory, usage analysis, and raw usage evidence are installed
      When the maintainer runs "remove-factory"
      Then the complete ".agent-factory/" installation including raw usage evidence is removed

    Scenario: Component lifecycle operations are idempotent
      # @packages/factory/scripts/init-factory
      Given an install, add, update, or component removal has completed successfully
      When the maintainer repeats the same operation against the resulting state
      Then the command succeeds as a clean no-op

  Rule: Factory producer publishes a compatible record contract without depending on analysis
    # actor: Factory producer
    # @packages/factory/scripts/usage-capture

    Scenario: Canonical contract belongs to Factory
      Given Factory publishes usage records
      When the usage-record contract is inspected
      Then "packages/factory/contracts/usage-record/contract.yaml" names Factory as owner and declares its compatibility policy
      And "v1.schema.json" declares a JSON Schema Draft 2020-12 record contract
      And the consumer reads only the installed contract copy

    Scenario: Contract validation covers schema and cross-field invariants
      Given a selected JSONL object is checked against an accepted contract version
      When "usage-contract-check" validates the object
      Then it validates field names, types, nullability, identifiers, timestamps, non-negative counters, and nested transcript reference shape
      And it verifies that normalized total equals normalized input plus normalized output

    Scenario: Capture remains available without analysis
      # @packages/factory/scripts/usage-capture
      Given the usage-analysis component is absent or its derived outputs are corrupt
      When Factory capture records a completed run
      Then capture appends authoritative JSONL without invoking DuckDB or analysis

    Scenario: Analysis remains transcript-blind
      Given selected usage records contain missing or unreadable transcript references
      When any deterministic analysis query runs
      Then the query does not open, copy, index, or tokenize transcript content
      And the result depends only on selected usage records and the versioned query model

  Rule: Quality maintainer assigns one deterministic owner to each observable contract
    # actor: Quality maintainer

    Scenario: Contract and accounting gates have distinct ownership
      Given the usage-record, registry, accounting, reproducibility, preflight, boundary, query, Parquet, capture-independence, lifecycle, and architecture-dependency contracts
      When the quality plan assigns deterministic gates
      Then each contract has exactly one owning gate
      And no query or export test duplicates SQL accounting assertions

    Scenario: Fixtures are synthetic and boundary-owned
      Given a deterministic gate needs usage evidence
      When its fixture set is created or extended
      Then each fixture is synthetic and contains no copied transcript or prompt
      And each fixture names one equivalence class, boundary, or distinct failure mode

    Scenario: Blocking gates provide executable evidence
      Given a contract is violated
      When its owning gate runs locally
      Then the gate exits non-zero with contract-specific diagnostics
      And screenshots, notebook output, and agent reports do not count as gate evidence

