# UAT Script — Value-First Onboarding Journey

**Date:** 2026-09-25
**Branch:** `feature/value-first-onboarding`
**Version:** 1.1.0-rc
**Tester:** Manual, single operator
**Scope:** Stories ST-0280 through ST-0294 (EPIC 4)

## Prerequisites

- The feature branch is checked out and all story commits are merged.
- Working tree changes (UAT bug fixes) are committed or stashed.
- The installed copy at `.agent-factory/` is current with the branch.
- `uv` is available on PATH.

## 1. Build a release

**Story coverage:** ST-0280

```bash
cd /home/matthiasdaues/Documents/datenschoenheit/agent_factory
uv run -- packages/factory/scripts/build-release
```

**Expected outcome:**

- [ ] Script exits 0.
- [ ] A tarball is created under `releases/1.1.0-rc/`.
- [ ] The tarball name includes `1.1.0-rc`.
- [ ] The `-rc` suffix is accepted on a non-main, non-dev branch (the relaxed constraint).

**Failure signals:** exit code non-zero, "version/branch mismatch" error, missing tarball.

______________________________________________________________________

## 2. Install to a fresh target (local source)

**Story coverage:** ST-0281

```bash
mkdir -p /tmp/uat-target && cd /tmp/uat-target && git init
python3 /home/matthiasdaues/Documents/datenschoenheit/agent_factory/packages/factory/scripts/install-agent-factory \
  --source /home/matthiasdaues/Documents/datenschoenheit/agent_factory \
  --target /tmp/uat-target
```

**Expected outcome:**

- [ ] Prerequisite checks pass (or fix loop runs and resolves).
- [ ] CLI auto-detection selects `claude` (or prompts for selection).
- [ ] Preview shows changed paths and asks for consent.
- [ ] After consent, init-factory runs all sections (scaffolding, wiring, project identity, context scan, test regime, gitignore, pre-commit hooks).
- [ ] Installation receipt prints with correct version (`1.1.0-rc`).
- [ ] Receipt "Next" section shows: `cd /tmp/uat-target`, followed by instructions to start the CLI and send a prompt.
- [ ] `.agent-factory/` directory exists at `/tmp/uat-target/.agent-factory/`.
- [ ] `.agent-factory/install.json` has `"version": 2` and correct `"cli"` list.

**Failure signals:** script error, missing receipt, version 1 manifest, unclear "Next" instructions.

______________________________________________________________________

## 3. Install to a fresh target (remote source)

**Story coverage:** ST-0282

```bash
rm -rf /tmp/uat-remote-target
mkdir -p /tmp/uat-remote-target && cd /tmp/uat-remote-target && git init
python3 /home/matthiasdaues/Documents/datenschoenheit/agent_factory/packages/factory/scripts/install-agent-factory \
  --source https://github.com/datenschoenheit/agent-factory/releases/download/v1.1.0-rc/agent-factory-1.1.0-rc.tar.gz \
  --target /tmp/uat-remote-target
```

> **Note:** This step requires the release asset to be published. If unpublished, skip and mark as "blocked — no published release asset."

**Expected outcome:**

- [ ] Archive is downloaded and its SHA-256 digest is verified.
- [ ] Receipt includes the resolved URL and verified digest.
- [ ] Installed factory matches the local-source install.

**Failure signals:** download error, digest mismatch, missing digest in receipt.

______________________________________________________________________

## 4. Greenfield first-session insight

**Story coverage:** ST-0287

```bash
cd /tmp/uat-target
claude   # or the CLI under test
# Send any initial prompt, e.g. "hi"
```

**Expected outcome:**

- [ ] The CLI reads `.agent-factory/config/project-context.json`.
- [ ] `fitting.status` is `"greenfield"` (no prior fitting on a fresh target).
- [ ] The session activates the **First-session insight** procedure (not the session menu directly).
- [ ] A key-value scan is reported: **Stack**, **Test entry**, **Safety signal**, **Recommended action**.
- [ ] Unknown values use the documented language: "not detected" (Stack, Test entry), "none observed" (Safety signal).
- [ ] Exactly one recommended action is presented.
- [ ] The scan changes no project file.
- [ ] After the insight, the session menu is presented.

**Failure signals:** session menu appears without insight, missing key-value fields, files changed by the scan, more than one recommended action.

______________________________________________________________________

## 5. Context capture as recommended action

**Story coverage:** ST-0288

After the insight from step 4:

- [ ] "Context capture" is offered as a recommended action (not run automatically).
- [ ] If the user selects context capture, the `capture-context` skill runs.
- [ ] If the user declines, no scan occurs.

**Failure signals:** context capture runs automatically at session start, skill invocation fails.

______________________________________________________________________

## 6. Gate demonstration before hook configuration

**Story coverage:** ST-0289

During the fitting flow (after selecting "Context capture" or entering fitting):

- [ ] A gate demonstration is presented before the user is asked about hooks.
- [ ] The demonstration shows what gates protect and how they fire.
- [ ] The user sees the gate in action before deciding on hook configuration.

**Failure signals:** hook configuration question appears without prior demonstration, demonstration is unclear or missing.

______________________________________________________________________

## 7. Hook configuration grouped by outcome

**Story coverage:** ST-0290

After the gate demonstration:

- [ ] Hooks are presented grouped by the outcome they protect (not by individual hook name).
- [ ] Source-only triggers (hooks that only make sense in the factory source repo) are filtered out in a target project.
- [ ] The user can accept or decline each group.

**Failure signals:** hooks listed individually without grouping, source-only triggers shown in a non-source target, no accept/decline per group.

______________________________________________________________________

## 8. First task in a repository with commits

**Story coverage:** ST-0291

In the fitted `/tmp/uat-target`:

- [ ] Create a commit (e.g. add a README).
- [ ] Start a new session and begin a task.
- [ ] The session recognizes the repository has commits and behaves normally (no sandbox mode, no special empty-repo handling).

**Failure signals:** sandbox mode activated despite commits, errors referencing empty repo.

______________________________________________________________________

## 9. First task in a repository without commits (sandbox)

**Story coverage:** ST-0292

```bash
rm -rf /tmp/uat-sandbox
mkdir -p /tmp/uat-sandbox && cd /tmp/uat-sandbox
python3 /home/matthiasdaues/Documents/datenschoenheit/agent_factory/packages/factory/scripts/install-agent-factory \
  --source /home/matthiasdaues/Documents/datenschoenheit/agent_factory \
  --target /tmp/uat-sandbox
```

**Expected outcome:**

- [ ] init-factory creates a plain sandbox when the repository has no HEAD (no commits).
- [ ] The `git init` succeeds but the repo has no commits.
- [ ] A session started in this sandbox operates correctly without errors.

**Failure signals:** init-factory fails on headless repo, session crashes on missing HEAD.

______________________________________________________________________

## 10. Check for available updates (dry run)

**Story coverage:** ST-0284

```bash
cd /tmp/uat-target
.agent-factory/factory/scripts/update-factory --target . --check
```

**Expected outcome:**

- [ ] Script exits 0.
- [ ] Reports installed version and candidate version.
- [ ] No files are modified (dry run).
- [ ] No `TypeError` on `manifest.get("cli")` (the list-vs-string bug).

**Failure signals:** TypeError traceback, files modified during check, non-zero exit.

______________________________________________________________________

## 11. Apply a staged update

**Story coverage:** ST-0285

```bash
cd /tmp/uat-target
.agent-factory/factory/scripts/update-factory --target . \
  --source /home/matthiasdaues/Documents/datenschoenheit/agent_factory
```

**Expected outcome:**

- [ ] Update applies cleanly.
- [ ] User-changed files are backed up to `.agent-factory/user-changes/`.
- [ ] Factory files are refreshed.
- [ ] Manifest is updated.
- [ ] On failure, rollback restores the prior state.

**Failure signals:** TypeError, collision error, missing backup, broken rollback.

______________________________________________________________________

## 12. Update across a source boundary

**Story coverage:** ST-0286

> This step tests switching from a local source to a remote source (or vice versa). Requires a published release asset.

- [ ] update-factory detects the source-type change.
- [ ] A separate consent prompt is shown for cross-boundary updates.
- [ ] The update completes or rolls back cleanly.

**Failure signals:** no consent prompt on source change, silent source switch.

______________________________________________________________________

## 13. Reinstall preserves usage data

**Story coverage:** Bug fix from this session

```bash
cd /tmp/uat-target
# Seed fake usage data
mkdir -p .agent-factory/usage/records .agent-factory/usage/transcripts
echo '{"record_id":"test-001","tokens":42}' > .agent-factory/usage/records/test-session.jsonl
echo '{"role":"user","content":"hello"}' > .agent-factory/usage/transcripts/test-session.jsonl
```

Now reinstall:

```bash
python3 /home/matthiasdaues/Documents/datenschoenheit/agent_factory/packages/factory/scripts/install-agent-factory \
  --source /home/matthiasdaues/Documents/datenschoenheit/agent_factory \
  --target /tmp/uat-target
```

**Expected outcome:**

- [ ] init-factory detects non-empty `usage/` and backs it up before proceeding.
- [ ] After the install, init-factory reports the backup and compares directory structure.
- [ ] Interactive mode: the user is prompted "Restore backed-up usage data? [Y/n]".
- [ ] On "Y": usage data is restored into the new `.agent-factory/usage/`.
- [ ] `test-session.jsonl` exists in both `records/` and `transcripts/` with original content.
- [ ] On "n": the backup path is printed; the user can restore manually.
- [ ] Non-interactive mode: restore happens automatically.

**Failure signals:** no backup prompt, data lost after reinstall, backup path not printed on decline.

______________________________________________________________________

## 14. Reinstall preserves user-changes

Same as step 13, but for `.agent-factory/user-changes/`:

```bash
cd /tmp/uat-target
mkdir -p .agent-factory/user-changes/20260901-120000
echo "backup content" > .agent-factory/user-changes/20260901-120000/CLAUDE.md.bak
```

Reinstall and verify:

- [ ] `user-changes/` is backed up and restored (or backup path printed).
- [ ] `20260901-120000/CLAUDE.md.bak` survives the reinstall.

______________________________________________________________________

## 15. Remove and verify clean removal

```bash
cd /tmp/uat-target
.agent-factory/factory/scripts/remove-factory --target /tmp/uat-target
```

**Expected outcome:**

- [ ] All factory-generated files and directories are removed.
- [ ] Orientation headers are stripped from instruction files.
- [ ] `.agent-factory/` directory is removed (or only user data remains).
- [ ] `.gitignore` agent_factory block is removed.
- [ ] Pre-commit hooks with the factory prefix are removed.

**Failure signals:** leftover factory files, broken instruction files, gitignore block remains.

______________________________________________________________________

## 16. Prerequisite fix loop

**Story coverage:** ST-0283

```bash
# Simulate missing prerequisite (e.g. remove uv from PATH temporarily)
PATH_BACKUP="$PATH"
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v uv | tr '\n' ':')
python3 /home/matthiasdaues/Documents/datenschoenheit/agent_factory/packages/factory/scripts/install-agent-factory \
  --source /home/matthiasdaues/Documents/datenschoenheit/agent_factory \
  --target /tmp/uat-prereq
export PATH="$PATH_BACKUP"
```

**Expected outcome:**

- [ ] Missing prerequisite is detected and reported.
- [ ] Fix loop offers guidance or attempts remediation.
- [ ] After fixing (restoring PATH), re-run succeeds.

**Failure signals:** silent failure, no guidance on missing prerequisite.

______________________________________________________________________

## 17. Automated journey test harness

**Story coverage:** ST-0293

- [ ] Verify `tests/factory/test_onboarding_journey.py` exists (or its planned location).
- [ ] The test harness exercises the greenfield → insight → menu → first-task path.
- [ ] Tests pass: `uv run -- pytest tests/factory/test_onboarding_journey.py -v`

> **Note:** If the journey test is a moderated-protocol template (ST-0294) rather than automated code, verify the template exists and is usable.

______________________________________________________________________

## 18. Moderated usability protocol

**Story coverage:** ST-0294

- [ ] A moderated usability protocol template exists (location per story file).
- [ ] The template covers comprehension checkpoints for the onboarding flow.
- [ ] The protocol can be followed by a moderator with a real participant.

______________________________________________________________________

## Summary checklist

| Step | Covers  | Pass | Notes |
| ---- | ------- | ---- | ----- |
| 1    | ST-0280 | [ ]  |       |
| 2    | ST-0281 | [ ]  |       |
| 3    | ST-0282 | [ ]  |       |
| 4    | ST-0287 | [ ]  |       |
| 5    | ST-0288 | [ ]  |       |
| 6    | ST-0289 | [ ]  |       |
| 7    | ST-0290 | [ ]  |       |
| 8    | ST-0291 | [ ]  |       |
| 9    | ST-0292 | [ ]  |       |
| 10   | ST-0284 | [ ]  |       |
| 11   | ST-0285 | [ ]  |       |
| 12   | ST-0286 | [ ]  |       |
| 13   | Bug fix | [ ]  |       |
| 14   | Bug fix | [ ]  |       |
| 15   | Remove  | [ ]  |       |
| 16   | ST-0283 | [ ]  |       |
| 17   | ST-0293 | [ ]  |       |
| 18   | ST-0294 | [ ]  |       |
