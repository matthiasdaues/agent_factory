# QA Strategy: factory-handbooks

Generated from:

- Feature spec: [factory-handbooks.feature](../features/factory-handbooks.feature), 7 Rules and 14 Scenarios
- Gaps report: [factory-handbooks-gaps.md](factory-handbooks-gaps.md), with its acceptance criteria for the stories
- Proposal: [factory-handbooks.md](../../proposals/factory-handbooks.md), `accepted`, decisions DEC-01 to DEC-14
- Run decisions: [handbooks-decision-log.md](handbooks-decision-log.md)
- Rules and contracts: [validation-rules.md § Factory handbooks](../validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152), BR-140 to BR-152, and [interface-contracts.md § Factory Handbooks Contracts](../interface-contracts.md#factory-handbooks-contracts)
- Layer bindings: [testing.yaml](../../testing.yaml), `default` pytest suite

## Feature

The feature adds two scripts, moves the content of three files into two handbooks, and repoints every link to those files. The highest risk is a check that passes a broken handbook, because every later page then drifts without notice. The second risk is lost text: `handbook-index` must never touch the text outside the markers, and the link rewrite must change only link destinations in a record (DEC-14). The third risk is a dead link after the move.

So each Scenario has one integration test or text check that owns it. The detail of each rule, such as each invalid value and each sort tie, goes to the contract tests of [Contract-test cases](#contract-test-cases).

## Test Layers in Scope

| Layer                | Status    | Scope                                                                                                            |
| -------------------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| Deterministic linter | available | Text checks over the real repository after the migration, as pytest tests in `tests/factory/`                    |
| Contract test        | available | Functions of `handbook-index`, `handbook-lint`, and `_link_rewrite.py`, loaded with `load_script`, without files |
| Integration test     | available | The scripts as subprocesses on temporary handbook folders, a real commit, `init-factory` and `update-factory`    |
| Acceptance test      | out       | The charter declares no Gherkin runner                                                                           |
| End-to-end test      | out       | The newcomer journey of session menu H belongs to `newcomer-onboarding.feature`                                  |

Every test runs with `uv run pytest --tb=short --quiet tests/factory/<file>`. Agents do not run it by hand, because the guardrail blocks `uv run pytest`. The tests run through the commit hook `run-tests` and the gate-check step. `tests/select_tests.py` selects a test file only when it names the changed script as a whole word, so `test_handbook_index.py` and `test_handbook_lint.py` name `handbook-index` and `handbook-lint` literally.

The integration tests of FH-01 and FH-02 build the model chapter `cli-integrations/` of the feature description with one helper in `test_handbook_index.py`. `test_handbook_lint.py` imports that helper, so both files test one model.

## Contract Owners

| Contract                                                                                                                                                                                                                                                                                                        | Source scenario | Owner layer          | Test ID     | Test location                                     | State       |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | -------------------- | ----------- | ------------------------------------------------- | ----------- |
| Grouped, sorted list with links and descriptions between the markers, exit 0                                                                                                                                                                                                                                    | FH-01-01        | Integration test     | FH-01-IT-01 | `tests/factory/test_handbook_index.py`            | implemented |
| Stub and `index.md` stay out; text outside the markers keeps its bytes                                                                                                                                                                                                                                          | FH-01-02        | Integration test     | FH-01-IT-02 | `tests/factory/test_handbook_index.py`            | implemented |
| A page without `type` makes `handbook-index` exit non-zero and write nothing                                                                                                                                                                                                                                    | FH-01-03        | Integration test     | FH-01-IT-03 | `tests/factory/test_handbook_index.py`            | implemented |
| The top-level lists name every chapter by `order`, a stub chapter included                                                                                                                                                                                                                                      | FH-01-04        | Integration test     | FH-01-IT-04 | `tests/factory/test_handbook_index.py`            | implemented |
| `--check` names the stale `index.md`, exits non-zero, changes no file                                                                                                                                                                                                                                           | FH-02-01        | Integration test     | FH-02-IT-01 | `tests/factory/test_handbook_index.py`            | implemented |
| `handbook-lint` fails and reports each of the seven failure kinds                                                                                                                                                                                                                                               | FH-02-02        | Integration test     | FH-02-IT-02 | `tests/factory/test_handbook_lint.py`             | implemented |
| One run reports a page, a folder, and a stale list across both handbooks                                                                                                                                                                                                                                        | FH-02-03        | Integration test     | FH-02-IT-03 | `tests/factory/test_handbook_lint.py`             | implemented |
| A commit with a page that lacks `type` is not created                                                                                                                                                                                                                                                           | FH-03-01        | Integration test     | FH-03-IT-01 | `tests/factory/test_precommit_config_contract.py` | implemented |
| After each command the installed handbook equals the source, path and bytes; the installed guide is absent; no contributor handbook file is copied                                                                                                                                                              | FH-04-01        | Integration test     | FH-04-IT-01 | `tests/factory/test_update_factory.py`            | implemented |
| Each section of the three files at `4ebf5101` has a map row with a real page; guide rows, the `beginner-intro.md` row, and the rows of "The phase chain" and "Key ideas" name user handbook pages; the row of "Project directory tree" names the `reference` page of the contributor handbook's `architecture/` | FH-05-01        | Integration test     | FH-05-IT-01 | `tests/factory/test_handbook_content.py`          | implemented |
| No link to the three files remains; records change only in destinations; `link-check` passes over every [live document](../../proposals/factory-handbooks.md#design-details)                                                                                                                                    | FH-05-02        | Integration test     | FH-05-IT-02 | `tests/factory/test_handbook_links.py`            | implemented |
| The three files and their archive copies are gone; the search finds nothing                                                                                                                                                                                                                                     | FH-05-03        | Deterministic linter | FH-05-LN-01 | `tests/factory/test_handbook_content.py`          | implemented |
| Session menu H, the tour skills, and the other entry points name the handbook                                                                                                                                                                                                                                   | FH-06-01        | Deterministic linter | FH-06-LN-01 | `tests/factory/test_handbook_content.py`          | implemented |
| The root README and the agent context route to contributor handbook pages                                                                                                                                                                                                                                       | FH-07-01        | Deterministic linter | FH-07-LN-01 | `tests/factory/test_handbook_content.py`          | implemented |

Notes on single rows:

- FH-02-IT-02 runs one case per Examples row. FH-04-IT-01 runs one case per Examples row, `init-factory` on an empty project and `update-factory` on a project with an earlier installation.
- FH-05-IT-01 reads the migration map, which now holds the rows of all three files. It reads the three files with `git show` at commit `4ebf5101f70c1540a0d53dcfb3d00cfa977d361a` and skips with a message when `git cat-file -e` fails in a shallow clone.
- FH-05-IT-02 installs the factory from the reviewed tree into a temporary project with `init-factory`, so links into `.agent-factory/` resolve against that copy (SPEC-0156).
- `test_handbook_content.py` builds the name of the deleted guide from two parts, such as `"factory" + "-guide"`, so its own search does not find it.

## Contract-test cases

The developer covers these cases from the rules. Each is a contract test with its own Test ID `FH-CT-NN`, named by the developer.

- `test_handbook_index.py`: the five group headings and their order; no heading for a type without a listed page; `order` values -5, 0, 1, 20, and the default 100; ties by `title`, then by path, for pages and for chapters; an entry without a description; no `index.md` in its own list; a stub chapter in the top-level list; a filled stub that joins the list; an image in a chapter folder that no list names (BR-144, BR-145).
- `test_handbook_index.py`: the five broken-marker cases (missing start, missing end, start twice, end twice, end before start) for `handbook-index` and for `--check`; `--check` refuses by BR-140 and still names every stale list whose pages pass (BR-143, BR-146).
- `test_handbook_lint.py`: no `title`, `type`, or `status`; `title` 42, `""`, and null; `type` `guide`; `status` `planned` and `specified`; `order` `first` and 2.5; `order` 0, -5, and 20 pass; a page with no frontmatter block; frontmatter that does not parse (BR-140).
- `test_handbook_lint.py`: titles that differ only in case fail; a stub may share a title with an implemented page; two chapters may share a title; a broken link and the word "must" do not fail (BR-142, BR-147).
- `test_precommit_config_contract.py`: the hook `handbook-lint` has `always_run: true` and `pass_filenames: false`; a commit that only deletes a page fails; `init-factory` writes no handbook hook into a user project (BR-148).
- `test_handbook_link_rewrite.py`: an anchor kept when the new page has the heading and dropped when it lacks it; a link without an anchor to each of the three files; a link to the installed guide keeps the `.agent-factory/factory/docs/` prefix; a record changes only in link destinations; links in code spans stay; reference-style links are rewritten; a query stays while the path moves; an encoded fragment is decoded for the map and kept; a link in a code span with inner backticks stays; a doubtful link is refused with its file and line, and the refusal edits nothing; a doubtful construct without a mapped link is left alone; an escaped backtick opens no code span; a label end without an open bracket is plain text (BR-150, BR-151, PROP-08).

## Review checks

Two checks need a person, because they judge prose:

- **Binding rules in ordinary prose.** The lector read before release and the code review of each story that writes a handbook page check that no page states a binding rule in ordinary prose (DEC-02). A rule appears only in a `> Rule summary:` callout with a `> Source:` line (BR-149). A finding of this check is a `fails purpose` defect of the story.
- **Migration completeness.** The code review of the migration story compares each section of `factory-guide.md` at commit `4ebf5101` with the page that the migration map names, and checks that its facts, commands, and paths are there. A test cannot check this, because the move rewrites the text (SPEC-0172).
- **The type table.** The same review checks that each page holds what its `type` allows, as the type table of the proposal sets, and that each `description` holds one sentence.

## Spec marker convention

Each test carries its Test ID as the `spec` marker and names the Scenario trace in its name, for example `@pytest.mark.spec("FH-01-IT-02")` on `test_fh_01_02_stub_and_outside_text()`. `pyproject.toml` already registers the marker `spec`.

## Defect Severity Triage

| Impact on this feature                                                                                                          | Consequence      | Expected action               |
| ------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------- |
| `handbook-index` changes text outside the markers; the rewrite changes a record's wording; `update-factory` removes a user file | "harm if in use" | stops the run                 |
| A check passes a broken page or a stale list; a stub appears in a list; a link or an entry point still names a deleted file     | "fails purpose"  | fix in the same story; blocks |
| A tie sorts differently without changing the set of pages; a report names the path but words the cause poorly                   | "raises cost"    | register file; does not block |
