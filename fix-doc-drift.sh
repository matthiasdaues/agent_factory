#!/usr/bin/env bash
# fix-doc-drift.sh — mechanical reconciliation of doc drift after
# mechanize-dispatch, agentic-quality-gates, copilot-allowlist, and
# capture-project-constraints proposals landed on dev.
#
# Generated 2026-08-27. Idempotent — safe to run more than once.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "=== 1. mdformat — copilot-tool-allowlist-normalization ==="
factory/scripts/mdformat --number docs/proposals/copilot-tool-allowlist-normalization.md

echo ""
echo "=== 2. ruff E402 — test_dispatch_e2e.py ==="
# sys.path.insert before import is an intentional test-harness pattern
sed -i 's/^import dispatch_lib$/import dispatch_lib  # noqa: E402/' tests/test_dispatch_e2e.py

echo ""
echo "=== 3. UC-13 phantom reference — mechanized-dispatch.md ==="
# Remove the Scenario that references a non-existent UC-13.md
# Lines 1054-1058: the entire Scenario block
sed -i '/Scenario: Step guard and premerge-check use the same matching semantics/,/Then both reach the same allow-or-deny decision/d' \
  docs/spec/supplementary_specs/mechanized-dispatch.md

echo ""
echo "=== 4. arch-lint stale images — re-export ==="
factory/scripts/arch-lint --docs-dir docs/arc42 --no-validate 2>&1 | grep -E 'EXPORT|STALE' || true

echo ""
echo "=== 5. Broken links — proposals moved to implemented/ ==="
# docs/reviews/token-efficiency-completion.md
sed -i 's|(../proposals/proposal-session-transcript-token-control.md)|(../proposals/implemented/proposal-session-transcript-token-control.md)|g' \
  docs/reviews/token-efficiency-completion.md
sed -i 's|(../proposals/agent-dispatch-token-efficiency.md)|(../proposals/implemented/agent-dispatch-token-efficiency.md)|g' \
  docs/reviews/token-efficiency-completion.md

echo ""
echo "=== 6. Broken links — proposals moved to superseded/ ==="
# docs/reviews/spec-review-2026-08-18*.md → mechanize-dispatch-orchestration.md
for f in docs/reviews/spec-review-2026-08-18.md \
         docs/reviews/spec-review-2026-08-18-pass2.md \
         docs/reviews/spec-review-2026-08-18-pass3.md; do
  [ -f "$f" ] && sed -i 's|(../proposals/mechanize-dispatch-orchestration.md)|(../proposals/superseded/mechanize-dispatch-orchestration.md)|g' "$f"
done

# docs/reviews/proposal-review-artifact-pipeline-discipline → superseded
sed -i 's|(../proposals/artifact-pipeline-discipline.md)|(../proposals/superseded/artifact-pipeline-discipline.md)|g' \
  docs/reviews/proposal-review-artifact-pipeline-discipline-2026-08-19.md

# docs/proposals/agentic-quality-gates → cost-aware-agent-delegation.md superseded
sed -i 's|(cost-aware-agent-delegation.md)|(superseded/cost-aware-agent-delegation.md)|g' \
  docs/proposals/agentic-quality-gates-and-specification-consolidation.md

echo ""
echo "=== 7. Broken links — implemented/ proposals lost depth after move ==="
# From docs/proposals/implemented/, ../reviews/ → ../../reviews/
sed -i 's|(../reviews/retro-2026-07-12.md)|(../../reviews/retro-2026-07-12.md)|g' \
  docs/proposals/implemented/agent-dispatch-token-efficiency.md
sed -i 's|(../reviews/retro-2026-07-10.md)|(../../reviews/retro-2026-07-10.md)|g' \
  docs/proposals/implemented/agent-dispatch-token-efficiency.md
sed -i 's|(../reviews/dispatch-safeguard-audit-2026-08-04.md)|(../../reviews/dispatch-safeguard-audit-2026-08-04.md)|g' \
  docs/proposals/implemented/agent-dispatch-token-efficiency.md
sed -i 's|(../reviews/token-efficiency-completion.md)|(../../reviews/token-efficiency-completion.md)|g' \
  docs/proposals/implemented/agent-dispatch-token-efficiency.md

sed -i 's|(../reviews/token-efficiency-completion.md)|(../../reviews/token-efficiency-completion.md)|g' \
  docs/proposals/implemented/proposal-session-transcript-token-control.md

# From docs/proposals/implemented/, ../../scripts/ → ../../../factory/scripts/
sed -i 's|(../../scripts/init-factory)|(../../../factory/scripts/init-factory)|g' \
  docs/proposals/implemented/codex-cli-support.md
sed -i 's|(../../scripts/remove-factory)|(../../../factory/scripts/remove-factory)|g' \
  docs/proposals/implemented/codex-cli-support.md
sed -i 's|(../../config/AGENTS.md)|(../../../factory/config/AGENTS.md)|g' \
  docs/proposals/implemented/codex-cli-support.md

# pi-invocation-layer.md — ../../config/extensions/ and ../factory-guide.md
sed -i 's|(../../config/extensions/block-dangerous-git.ts)|(../../../factory/config/extensions/block-dangerous-git.ts)|g' \
  docs/proposals/implemented/pi-invocation-layer.md
sed -i 's|(../factory-guide.md)|(../../factory/docs/factory-guide.md)|g' \
  docs/proposals/implemented/pi-invocation-layer.md

# research-survey-mode.md — ../../rulebooks/ → ../../../factory/rulebooks/
sed -i 's|(../../rulebooks/conventions/dispatch-contract.md)|(../../../factory/rulebooks/conventions/dispatch-contract.md)|g' \
  docs/proposals/implemented/research-survey-mode.md

echo ""
echo "=== 8. Broken links — reviews referencing factory/ with wrong depth ==="
# docs/reviews/ → ../rulebooks/ should be ../../factory/rulebooks/
sed -i 's|(../rulebooks/conventions/finding-format.md#when-to-file)|(../../factory/rulebooks/conventions/finding-format.md#when-to-file)|g' \
  docs/reviews/fagan-review-2026-08-06-bug-0008-envelope.md
sed -i 's|(../rulebooks/conventions/finding-format.md)|(../../factory/rulebooks/conventions/finding-format.md)|g' \
  docs/reviews/qa-revalidation-2026-08-06-bug-run-agent-envelope.md

echo ""
echo "=== 9. Broken links — ADR cross-references ==="
# docs/adr/0003 → ../08_crosscutting_concepts.md should be ../arc42/08_crosscutting_concepts.md
sed -i 's|(../08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)|(../arc42/08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)|g' \
  docs/adr/0003-test-execution-via-hooks.md

# docs/adr/0004,0005,0006 → ../09_architecture_decisions.md should be ../arc42/09_architecture_decisions.md
for f in docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md \
         docs/adr/0005-openrouter-model-discovery-for-model-conf.md \
         docs/adr/0006-research-flat-storage-and-validation-pipeline.md; do
  sed -i 's|(../09_architecture_decisions.md)|(../arc42/09_architecture_decisions.md)|g' "$f"
done

# docs/adr/0006 → bare 05_building_block_view.md should be ../arc42/05_building_block_view.md
sed -i 's|(05_building_block_view.md#522-research-artifact-validators-schema-validate-policy-validate)|(../arc42/05_building_block_view.md#522-research-artifact-validators-schema-validate-policy-validate)|g' \
  docs/adr/0006-research-flat-storage-and-validation-pipeline.md

# docs/adr/0001 — orchestrator/ paths are historical (subproject removed); fix to note
sed -i 's|(../../orchestrator/backlog/ST-0067.md)|(<removed: orchestrator subproject>)|g' \
  docs/adr/0001-precommit-monorepo-scoping.md
sed -i 's|(../../orchestrator/docs/adr/0003-pre-commit-as-gate-bus.md)|(<removed: orchestrator subproject>)|g' \
  docs/adr/0001-precommit-monorepo-scoping.md

echo ""
echo "=== 10. Broken links — findings ==="
# SPEC-001: ../todos.md → ../spec/todos.md
sed -i 's|(../todos.md#t-03-script_exit_zero-condition-type-is-stubbed)|(../spec/todos.md#t-03-script_exit_zero-condition-type-is-stubbed)|g' \
  docs/findings/SPEC-001-script-exit-zero-inconsistency.md

# SPEC-002: bare UC-04 filename → ../spec/use_cases/UC-04...
sed -i 's|(UC-04-dispatch-an-agent-via-trigger.md#business-rules)|(../spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md#business-rules)|g' \
  docs/findings/SPEC-002-uc07-missing-test-command-reference.md

echo ""
echo "=== 11. Broken links — active proposals with factory-relative paths ==="
# playbook-structured-harness-strategy.md: ../../playbooks/ → ../../factory/playbooks/
# ../../scripts/ → ../../factory/scripts/  etc.
sed -i \
  -e 's|(../../playbooks/)|(../../factory/playbooks/)|g' \
  -e 's|(../../playbooks/greenfield-development.fsm.yml)|(../../factory/playbooks/greenfield-development.fsm.yml)|g' \
  -e 's|(../../scripts/spec-lint)|(../../factory/scripts/spec-lint)|g' \
  -e 's|(../../scripts/arch-lint)|(../../factory/scripts/arch-lint)|g' \
  -e 's|(../../scripts/backlog-lint)|(../../factory/scripts/backlog-lint)|g' \
  -e 's|(../../scripts/transition-lint)|(../../factory/scripts/transition-lint)|g' \
  -e 's|(../../scripts/phase)|(../../factory/scripts/phase)|g' \
  -e 's|(../../rulebooks/conventions/state-machine-notation.md)|(../../factory/rulebooks/conventions/state-machine-notation.md)|g' \
  -e 's|(../../agents/spec-review-agent.md)|(../../factory/agents/spec-review-agent.md)|g' \
  -e 's|(../../rulebooks/templates/finding.md#frontmatter)|(../../factory/rulebooks/templates/finding.md#frontmatter)|g' \
  -e 's|(../../config/pre-commit-config.yaml)|(../../factory/config/pre-commit-config.yaml)|g' \
  -e 's|(../factory-guide.md#playbook-phase-gates)|(../../factory/docs/factory-guide.md#playbook-phase-gates)|g' \
  docs/proposals/playbook-structured-harness-strategy.md

# session-log-addendum.md: same pattern
sed -i \
  -e 's|(../../scripts/spec-lint)|(../../factory/scripts/spec-lint)|g' \
  -e 's|(../../scripts/_session_log.py)|(../../factory/scripts/_session_log.py)|g' \
  -e 's|(../../scripts/session-reconcile)|(../../factory/scripts/session-reconcile)|g' \
  -e 's|(../../rulebooks/conventions/branching-policy.md#two-shas-tracked-per-invocation)|(../../factory/rulebooks/conventions/branching-policy.md#two-shas-tracked-per-invocation)|g' \
  -e 's|(../../rulebooks/conventions/finding-format.md#when-to-file)|(../../factory/rulebooks/conventions/finding-format.md#when-to-file)|g' \
  -e 's|(../factory-guide.md#linting-and-gating)|(../../factory/docs/factory-guide.md#linting-and-gating)|g' \
  -e 's|(../factory-guide.md#session-logging)|(../../factory/docs/factory-guide.md#session-logging)|g' \
  docs/proposals/session-log-addendum.md

# session-log-addendum.md — orchestrator test paths (subproject removed)
sed -i \
  -e 's|(../../../orchestrator/tests/test_session_log.py)|(<removed: orchestrator subproject>)|g' \
  -e 's|(../../../orchestrator/tests/test_session_reconcile.py)|(<removed: orchestrator subproject>)|g' \
  docs/proposals/session-log-addendum.md

echo ""
echo "=== Done. Re-running link-check to verify ==="
git ls-files -z '*.md' ':!factory/**' | xargs -0 factory/scripts/link-check 2>&1 | tail -5
echo ""
echo "=== Re-running spec-lint ==="
factory/scripts/spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json 2>&1 | grep -E 'WARNING|ERROR|spec-lint:' || true
echo ""
echo "=== Re-running ruff ==="
ruff check . 2>&1 | tail -3
echo ""
echo "=== Re-running mdformat --check ==="
factory/scripts/mdformat --number --check . 2>&1 | tail -3
