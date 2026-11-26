---
title: Script reference
type: concept
status: implemented
order: 75
description: Manpages for the executable scripts shipped with Agent Factory.
---

# Script reference

Factory agents, hooks, and contributors call these scripts to install the Factory, coordinate work, check artifacts, and record usage. The synopsis uses the installed path for project commands. Each page also links to the source shipped with the Factory.

If you are checking a specification, start with [spec-lint](spec-lint.md). For eligible agents, see [intent](intent.md). For updates and project usage, see [update-factory](update-factory.md) and [usage-query](usage-query.md).

<!-- handbook-index:start -->

## Reference

- [\_docs_assemble.py](_docs_assemble.py.md): Assemble the chapters and assets used by the architecture PDF renderer.
- [arch-lint](arch-lint.md): Check the structure of the project's arc42 documentation and architecture references.
- [backlog-lint](backlog-lint.md): Check backlog story files, their metadata, and their dependencies.
- [build-release](build-release.md): Package the committed Factory source into release artifacts.
- [commit-safe](commit-safe.md): Stage selected files and retry a commit if formatting hooks change them.
- [concept-history-check](concept-history-check.md): Check the history of domain concepts against the glossary.
- [concern-lint](concern-lint.md): Check the concerns and source references in the agent context.
- [conjecture-lint](conjecture-lint.md): Check a research conjecture and its required fields.
- [context-lint](context-lint.md): Check context declarations for Factory artifacts.
- [crap-score](crap-score.md): Measure change risk using function complexity and test coverage.
- [dependency-check](dependency-check.md): Check source imports against declared dependency rules.
- [dispatch](dispatch.md): Manage implementation stories, worktrees, waves, and merges.
- [finding-lint](finding-lint.md): Check findings and their severity against the finding rules.
- [gate-setup-proof](gate-setup-proof.md): Prove a change-risk gate can distinguish tested and untested code.
- [generate-codex-agents](generate-codex-agents.md): Generate Codex agent definitions from Factory agent files.
- [generate-copilot-agents](generate-copilot-agents.md): Generate Copilot agent definitions from Factory agent files.
- [handbook-index](handbook-index.md): Regenerate the page lists in both Factory handbooks.
- [handbook-lint](handbook-lint.md): Check handbook layout, page metadata, and generated indexes.
- [handoff-lint](handoff-lint.md): Check a session handoff against its required structure.
- [hook-demo](hook-demo.md): Demonstrate the configured Factory hook behavior.
- [hook-subset](hook-subset.md): Select and run the pre-commit hooks that apply to a set of files.
- [housekeeping-about](housekeeping-about.md): Report the installed Factory and project setup state.
- [index-lint](index-lint.md): Generate or check the Factory catalog from source metadata.
- [init-factory](init-factory.md): Install the Factory and wire it into the selected coding CLIs.
- [install-agent-factory](install-agent-factory.md): Install Agent Factory from a release source.
- [intent](intent.md): Report which agents can run or assess the artifacts in a project.
- [link-check](link-check.md): Check local links in Markdown files.
- [matrix-lint](matrix-lint.md): Validate the model matrix used to route agent sessions.
- [mdformat](mdformat.md): Format Markdown with the Factory's formatter and plugins.
- [merge-precommit-config](merge-precommit-config.md): Merge Factory hook entries into a project's pre-commit configuration.
- [mermaid-lint](mermaid-lint.md): Check Mermaid blocks in Markdown for Factory notation rules.
- [migrate-layout](migrate-layout.md): Move an older Factory installation to the current directory layout.
- [migrate-spec-layout](migrate-spec-layout.md): Move older specification files into the supported layout.
- [migrate-usage-transcripts](migrate-usage-transcripts.md): Convert older usage transcripts to the current storage layout.
- [module-graph-check](module-graph-check.md): Check module dependencies against the allowed module graph.
- [move-docs](move-docs.md): Move Markdown documentation and rewrite affected links.
- [mutation-testing](mutation-testing.md): Run a project's mutation tests and check the configured result.
- [next-id](next-id.md): Allocate the next ID for a Factory artifact.
- [openrouter-discover](openrouter-discover.md): Discover OpenRouter models for the Pi model matrix.
- [pi-capture-bootstrap.mjs](pi-capture-bootstrap.mjs.md): Start the Pi usage supervisor and handle a failed startup.
- [policy-validate](policy-validate.md): Check research artifacts against the evidence policy.
- [premerge-check](premerge-check.md): Check a branch and its required evidence before merge.
- [publish-docs](publish-docs.md): Build a checked PDF from a project's arc42 documentation.
- [remark-deck](remark-deck.md): Build a remark.js deck from its slide source.
- [remove-factory](remove-factory.md): Remove the Factory installation and its local usage data.
- [resolve-model](resolve-model.md): Resolve a model from a CLI and tier in the model matrix.
- [schema-validate](schema-validate.md): Validate an artifact against a Factory schema.
- [scope-lint](scope-lint.md): Check the format and references in a scope map.
- [scratchpad](scratchpad.md): Append a dated note to the session scratchpad.
- [session-reconcile](session-reconcile.md): Compare session audit records with repository artifacts.
- [source-record-check](source-record-check.md): Validate a research source record.
- [spec-lint](spec-lint.md): Check specification artifacts for structural consistency.
- [statemachine-lint](statemachine-lint.md): Check state-machine descriptions and their correspondence to diagrams.
- [step-guard](step-guard.md): Check tool actions against an active step's declared boundaries.
- [structurizr](structurizr.md): Validate the architecture workspace or export its views.
- [test-design-verify](test-design-verify.md): Check that required test evidence is present for a story.
- [trigger](trigger.md): Resolve and start a Factory agent session.
- [update-factory](update-factory.md): Refresh an installation from the selected Factory source.
- [usage-capture](usage-capture.md): Normalize and count tokens from a CLI transcript.
- [usage-capture-lifecycle](usage-capture-lifecycle.md): Manage registration and completion of pending usage captures.
- [usage-capture-runtime](usage-capture-runtime.md): Launch usage capture through its installed Python runtime.
- [usage-explore](usage-explore.md): Open the explorer for a persisted usage database.
- [usage-query](usage-query.md): Query the views provided by the optional usage add-on.
- [validate](validate.md): Check Markdown prose for prohibited at-reference syntax.
- [verify-base](verify-base.md): Verify that a worktree is on its declared branch and base.
- [voice-anchor-lint](voice-anchor-lint.md): Check that prose-producing instructions include the Factory voice reference.

<!-- handbook-index:end -->
