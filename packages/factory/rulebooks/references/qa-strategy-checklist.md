# QA Strategy Quality Checklist

Fifteen checks to run before finishing a per-feature QA strategy document.
Used by [qa-strategy-from-spec](../../skills/qa-strategy-from-spec/SKILL.md).

01. The output is about **one feature**, not the whole project.
02. The `Feature` section includes both proposal and Gherkin traces; if the
    proposal trace cannot be recovered from the source artifacts, record that
    as a gap rather than inventing one.
03. The "Generated from" header includes charter layer bindings and repo test
    infrastructure sources.
04. `Test Layers in Scope` uses status states (`available`,
    `partially covered`, `planned`, `blocked`, `out`) — not the old
    `add / strengthen / out`.
05. `Test Layers in Scope` includes a `Charter binding` column showing the
    charter's tool and entry point, or "Factory convention fallback" when the
    charter is absent.
06. `Contract Owners` is a table with columns: Contract, Source scenario or
    gap, Owner layer, Test ID, Test location, Command, State.
07. Every contract-owner row has a test ID following `<scope-ID>-<layer-abbreviation>-<sequence>`.
08. Every contract-owner row has a `State` of `implemented`, `planned`, or
    `blocked`.
09. The spec marker convention (`@pytest.mark.spec("<scope-ID>")`) is
    documented in the Contract Owners section.
10. `Boundary Cases` contains only entries traced to a `Scenario:` or `Gap:`.
11. `Gap Findings` records all charter/repo mismatches, missing layer
    declarations, and fidelity insufficiencies found during Steps 1 and 3.
12. When a contract was assigned to a layer, fidelity declarations were
    checked against contract requirements.
13. `Defect Severity Triage` reflects the feature's risk profile, not
    boilerplate.
14. `Test Retention Policy` points back to
    [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md)
    for overlap deletion protocol.
15. No section is just a paraphrase of the generic testing strategy.
