---
schema_version: 2
title: External Artifact Sync
status: draft
owner: md@matthiasdaues.de
created: 2026-09-23
updated: 2026-09-23
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - backlog/ST-*.md
    - docs/findings/**/*.md

governance:
  assurance: elevated
  risk_domains:
    - operations
    - compatibility

estimate:
  as_of: 2026-09-23
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: External Artifact Sync

## Summary

Enable the factory to publish actionable artifacts — backlog stories and review
findings — to external systems (GitHub Issues, Jira) without changing agents or
skills. Agents keep writing markdown; a GitHub Action on commit parses
frontmatter and creates or updates external items. A thin Jira REST read layer
lets agents query external state when they need it.

## Motivation

Teams already manage work in Jira and code in GitHub. Today the factory writes
stories and findings as local markdown files that stay invisible to those
systems. This forces manual re-entry or means the artifacts are never seen by
the people who act on them. The factory should meet teams where their tooling
already lives.

## Core Principles

- **Agents stay ignorant of the target system.** No agent or skill learns about
  Jira or GitHub Issues. Markdown remains the canonical write format.
- **Push is commit-driven.** A GitHub Action triggered on push handles outbound
  sync. No new daemon, no MCP server, no agent-side API calls for writes.
- **Pull is explicit and thin.** When an agent needs external state (story
  status, acceptance criteria refinements), it calls a factory script that wraps
  Jira REST. Failure falls back to local markdown.
- **Auth uses what the team already has.** `gh` CLI credentials for GitHub,
  `JIRA_API_TOKEN` environment variable for Jira REST. No factory-managed
  secrets.
- **MCP servers are out of scope.** Organization policy does not permit most MCP
  integrations.

## Design

### Artifact families and their targets

| Artifact family | Markdown location             | Push target                               | Read-back needed                                    |
| --------------- | ----------------------------- | ----------------------------------------- | --------------------------------------------------- |
| Backlog stories | `backlog/ST-*.md`             | GitHub Issue → Jira (via org integration) | Yes — status, priority, sprint, acceptance criteria |
| Findings        | `docs/findings/<TAG>-NNNN.md` | GitHub Issues (labeled by tag)            | No — findings are resolved in code                  |
| Todo entries    | `docs/spec/todo.md`           | None (session-internal, low volume)       | No                                                  |

### Push channel: GitHub Action

A workflow triggered on pushes to `backlog/ST-*.md` and `docs/findings/**/*.md`:

1. Diff the commit to find added or changed files in those paths.
2. Parse YAML frontmatter from each file.
3. For new files: create a GitHub Issue with title, body, and labels derived
   from frontmatter fields (type, priority, epic, finding tag).
4. For changed files: update the existing linked GitHub Issue.
5. Write the GitHub Issue number back into the frontmatter as `github_issue`
   (via a follow-up commit or annotation).

The org's existing GitHub-to-Jira integration carries stories from GitHub
Issues into Jira. The factory does not talk to Jira for writes.

### Pull channel: Jira REST read layer

A factory script at `factory/scripts/jira-read` that wraps `curl` against the
Jira REST API v3. Three query patterns:

- `get-story <jira-key>` — returns status, priority, acceptance criteria, sprint.
- `list-stories <epic-key> [--status <filter>]` — for wave planning.
- `get-epic <jira-key>` — returns status and child story count.

Output is JSON. The script exits non-zero when Jira is unreachable; callers
fall back to local markdown state.

### Identity linking

The Jira key lives in the story's markdown frontmatter:

```yaml
jira_key: PROJ-123
github_issue: 42
```

`github_issue` is written by the GitHub Action after sync. `jira_key` is
written by the GitHub Action once the org integration creates the Jira item, or
manually by a team member. Both fields are optional — their absence means the
story has not been synced.

### Agents that read external state

| Agent                | What it reads                  | When                                                              |
| -------------------- | ------------------------------ | ----------------------------------------------------------------- |
| implementation-agent | story status, sprint, priority | Before wave scheduling — skip deprioritized or reassigned stories |
| planning-agent       | epic status, existing stories  | Before creating stories — avoid duplicates, respect PO reordering |
| code-review-agent    | acceptance criteria            | Before review — PO may have refined post-planning                 |
| reconciliation-agent | story status                   | Before reconciliation — only reconcile completed stories          |

Each agent calls `factory/scripts/jira-read` only when `jira_key` is present in
the story frontmatter. When absent or when the call fails, the agent uses local
markdown as the sole source.

## Scope

**In the first release:**

- GitHub Action workflow for push-sync of stories and findings to GitHub Issues.
- Frontmatter field additions (`github_issue`, `jira_key`) to the story and
  finding templates.
- `factory/scripts/jira-read` script with the three query patterns.
- Configuration in `.agent-factory/config/` for Jira base URL and project key.
- Documentation of required environment variables and org integration
  prerequisites.

**Explicitly deferred (do NOT plan stories for these):**

- Write-back to Jira (creating Jira items directly, bypassing GitHub Issues).
- Bidirectional sync (Jira changes updating local markdown).
- Confluence integration for review reports or specifications.
- Todo entry sync.
- Research claim sync.
- Custom field mapping beyond the default frontmatter-to-issue translation.

## Open Questions

- Should the GitHub Action write `jira_key` back automatically, or does the
  org integration not expose the Jira key in a way the Action can capture?
- What is the org's GitHub-to-Jira integration — native GitHub for Jira app,
  or a custom workflow? This determines what fields carry over.
- Should findings sync to the same GitHub repo as issues, or to a separate
  tracking repo?
- Rate limiting: for a large backlog commit (20+ stories in one push), does the
  Action need throttling?

## Completion Criteria

- A commit adding `backlog/ST-0001.md` creates a GitHub Issue with correct
  title, labels, and body within one Action run.
- A commit modifying a synced story updates the linked GitHub Issue.
- A commit adding `docs/findings/SPEC-0001.md` creates a labeled GitHub Issue.
- `factory/scripts/jira-read get-story PROJ-123` returns valid JSON with
  status, priority, acceptance criteria, and sprint fields.
- `factory/scripts/jira-read` exits non-zero and produces a clear error when
  Jira is unreachable or the token is missing.
- Agents that read Jira state fall back gracefully when `jira_key` is absent.

## Guiding Rule

The factory writes markdown; the infrastructure delivers it to where the team
already works.
