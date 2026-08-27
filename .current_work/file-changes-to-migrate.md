# Migration from `.agent-factory` to `.current_work`

## Skills Affected

The following skills create folders/files in `.agent-factory/` and need to be updated to use `.current_work/` instead:

1. **crap-score** - Creates `.agent-factory/crap-score/`
2. **dependency-check** - Creates `.agent-factory/dependency-check/`
3. **mutation-analysis** - Creates `.agent-factory/mutation-analysis/`
4. **run-step** - Reads/writes `.agent-factory/playbook-state.yml`

______________________________________________________________________

## File Changes Required

### 1. `factory/scripts/crap-score`

**Line 21:** Change output path documentation

- Old: `Writes JSON to .agent-factory/crap-score/<story-id>.json and to`
- New: `Writes JSON to .current_work/crap-score/<story-id>.json and to`

**Line 70:** Update `--report-dir` default

- Old: `--report-dir,.default .agent-factory/crap-score`
- New: `--report-dir,.default .current_work/crap-score`

**Line 201:** Update `write_report` function

- Old: `report_dir = Path(args.report_dir).resolve()` (uses default `.agent-factory/crap-score`)
- New: `report_dir = Path(args.report_dir).resolve()` (uses default `.current_work/crap-score`)

**Line 208:** Update report directory creation

- Old: `report_dir.mkdir(parents=True, exist_ok=True)`
- New: `report_dir.mkdir(parents=True, exist_ok=True)` (same - just the path changed)

**Line 227:** Update error message

- Old: `print(f"crap-score: threshold={threshold} wrote {report_path}", file=sys.stderr)`
- New: Same (path is in `report_path` variable)

**Skill documentation** (`/.pi/skills/crap-score/SKILL.md`):

- **Line 21:** Update logged output path
  - Old: `Logged output at .agent-factory/crap-score/<story-id>.json`
  - New: `Logged output at .current_work/crap-score/<story-id>.json`

______________________________________________________________________

### 2. `factory/scripts/dependency-check`

**Line 22:** Update output path documentation

- Old: `Writes JSON to .agent-factory/dependency-check/<story-id>.json and to`
- New: `Writes JSON to .current_work/dependency-check/<story-id>.json and to`

**Line 82:** Update `--report-dir` default

- Old: `--report-dir,.default .agent-factory/dependency-check`
- New: `--report-dir,.default .current_work/dependency-check`

**Line 307:** Update `write_report` function

- Old: `report_dir.mkdir(parents=True, exist_ok=True)`
- New: `report_dir.mkdir(parents=True, exist_ok=True)` (same - just the path changed)

**Line 311:** Update report path

- Old: `report_path = report_dir / f"{story_id}.json"`
- New: Same (path is in `report_dir` variable)

**Line 321:** Update error message

- Old: `print(f"dependency-check: wrote {report_path}", file=sys.stderr)`
- New: Same (path is in `report_path` variable)

**Skill documentation** (`/.pi/skills/dependency-check/SKILL.md`):

- **Line 21:** Update logged output path
  - Old: `Logged output at .agent-factory/dependency-check/<story-id>.json`
  - New: `Logged output at .current_work/dependency-check/<story-id>.json`

______________________________________________________________________

### 3. `factory/scripts/mutation-analysis`

**Line 106:** Update report path resolution

- Old: `report_path = write_report(repo_root, story_id, report)`
- New: Same (function handles path internally)

**Line 280:** Update workspace directory

- Old: `workspace_root = repo_root / ".agent-factory" / "mutation-analysis" / "workspaces"`
- New: `workspace_root = repo_root / ".current_work" / "mutation-analysis" / "workspaces"`

**Line 497-502:** Update `write_report` function

- Old: `report_dir = repo_root / ".agent-factory" / "mutation-analysis"`
- New: `report_dir = repo_root / ".current_work" / "mutation-analysis"`

**Line 499:** Update mkdir

- Old: `report_dir.mkdir(parents=True, exist_ok=True)`
- New: Same

**Line 500:** Update report path

- Old: `report_path = report_dir / f"{story_id}.json"`
- New: Same

**Skill documentation** (`/.pi/skills/mutation-analysis/SKILL.md`):

- **Line 100:** Update report location
  - Old: `.agent-factory/mutation-analysis/<story-id>.json`
  - New: `.current_work/mutation-analysis/<story-id>.json`

______________________________________________________________________

### 4. `factory/scripts/phase`

**Line 54:** Update default marker path

- Old: `DEFAULT_MARKER = Path(".agent-factory/playbook-state.yml")`
- New: `DEFAULT_MARKER = Path(".current_work/playbook-state.yml")`

**Lines 554, 568:** Update marker resolution (implicit via DEFAULT_MARKER)

- Old: `args.marker or (args.repo_root / DEFAULT_MARKER)`
- New: Same (uses updated DEFAULT_MARKER)

**Line 389:** Update mkdir for marker

- Old: `marker_path.parent.mkdir(parents=True, exist_ok=True)`
- New: Same (path now points to `.current_work/playbook-state.yml`)

______________________________________________________________________

### 5. `factory/scripts/trigger`

No changes required (does not reference `.agent-factory` directly).

______________________________________________________________________

### 6. `factory/scripts/transition-lint`

**Line 12:** Update marker reference in documentation

- Old: ``` Reads the git-ignored run-state marker (``.agent-factory/playbook-state.yml``) ```
- New: ``` Reads the git-ignored run-state marker (``.current_work/playbook-state.yml``) ```

**Line 51:** Update default marker path

- Old: `DEFAULT_MARKER = Path(".agent-factory/playbook-state.yml")`
- New: `DEFAULT_MARKER = Path(".current_work/playbook-state.yml")`

**Line 363:** Update marker resolution (implicit via DEFAULT_MARKER)

- Old: `marker = args.marker or (args.repo_root / DEFAULT_MARKER)`
- New: Same (uses updated DEFAULT_MARKER)

______________________________________________________________________

## Summary

**Total files to modify:** 6

**Script files:**

1. `factory/scripts/crap-score`
2. `factory/scripts/dependency-check`
3. `factory/scripts/mutation-analysis`
4. `factory/scripts/phase`
5. `factory/scripts/transition-lint`

**Skill documentation files:**

1. `.pi/skills/crap-score/SKILL.md`
2. `.pi/skills/dependency-check/SKILL.md`
3. `.pi/skills/mutation-analysis/SKILL.md`

**Key change:** Replace all instances of `.agent-factory/` with `.current_work/` in the paths listed above.

\<tool_call>
\<function=bash>
