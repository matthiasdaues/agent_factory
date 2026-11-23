---
schema_version: 2
title: SaaS Browser Switchboard
status: draft
owner: agent-factory
created: 2026-11-20
updated: 2026-11-20
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
  boundaries:
    - packages/factory/skills/
    - packages/factory/scripts/
    - docs/spec/architecture.dsl

governance:
  assurance: high
  risk_domains:
    - security
    - privacy
    - operations

estimate:
  as_of: 2026-11-20
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: SaaS Browser Switchboard

## Primer

The write-primer skill writes this section after the grilling, when the
design is settled.

## Summary

A new skill sets up a switchboard between factory agents and browser-based
SaaS platforms, starting with Jira and Confluence. The switchboard drives a
browser in which the user has signed in, so an agent can read from a platform
and write back to it with exactly the permissions of that user. The first
release works on pull only: the agent reads and writes when someone runs the
skill, and no background service runs.

## Motivation

Factory agents work in the repository, but much of a team's conversation
happens in Jira tickets and Confluence pages. Today an agent
cannot read a comment on a ticket or answer it.

Both platforms have APIs, and Atlassian offers an MCP server. In enterprise
settings, admins often narrow what an API token may do, or block personal
tokens completely. A browser session cannot be narrowed that way. It sees and
does exactly what the signed-in user may see and do (DEC-01). So the browser
is the one channel that works wherever the user can work.

## Core Principles

- **The agent acts in the open.** Every text the agent writes is marked as
  written by an agent, and the skill contains no code that hides automation
  from the platform (DEC-02).
- **The agent keeps to the platform's pace.** The skill respects rate limits
  and never sends more than a human would in one action (DEC-03).
- **The user owns compliance.** The skill does not claim that its use is
  allowed. The user confirms the platform terms and the company's automation
  policy before the first run (DEC-05).

## Design

### Channels

The switchboard has one main channel and optional extra channels:

| Channel            | Role     | Permissions                |
| ------------------ | -------- | -------------------------- |
| Playwright browser | main     | exactly those of the user  |
| REST API           | optional | those of the token's scope |
| MCP server         | optional | those the server grants    |

The user adds an optional channel per platform. Without one, the skill uses
the browser (DEC-01).

### Browser session

The skill starts the browser with a persistent profile of its own, in a
visible window. The user signs in there the usual way, single sign-on
included. The profile directory keeps the session between runs, so the user
signs in again only when the platform ends the session. The directory holds
session cookies, so it is created with mode `700` and is never committed. The
skill never copies cookies out of the browser (DEC-07).

### Jira and Confluence

The skill calls the platform's own REST endpoints with `fetch()` from inside a
signed-in page (DEC-07). The call carries the user's session, so it gets the
user's permissions, and the data arrives as JSON instead of page HTML. Three
rules come from an earlier migration tool that worked this way:

- **Dry run by default.** A write command only reports what it would do,
  until the user passes `--execute`.
- **Stable markers.** Each written comment carries a marker that names its
  source, so a rerun finds the comment and does not write it twice.
- **Capped wait.** The skill honours `Retry-After`, but waits 120 seconds at
  most, because a firewall can send a value that is far too large.

### Setup

The skill is built around the browser, so its setup checks only what the
browser channel needs (DEC-14):

1. The skill checks that Playwright and a supported browser are installed. If
   one is missing, it names what is missing and offers to install it.
2. The skill asks for the address of the user's Jira and Confluence sites.
3. The skill opens the visible browser with its own profile, and the user signs
   in.
4. The skill confirms the session with one read call per platform, such as the
   user's own profile in Jira.

The setup does not look for API tokens or MCP servers.

### Pull exchange

An agent reads from a platform and writes to it only while the skill runs
(DEC-04). A comment a colleague posts on a ticket reaches the agent the next
time someone runs the skill.

### Marking and log

- Each write starts with the marker `[agent]`, for example at the start of a
  Jira comment or a Confluence comment.
- A change that has no text of its own comes with an `[agent]` comment in the
  same run. That covers a Jira status change, a Jira field change, and a
  Confluence page body edit. Example on a ticket:
  `[agent] Status: In Progress → In Review` (DEC-13).
- The skill appends one line per write to a local log. The line holds the
  platform, the target (such as the ticket key or page URL),
  and the time in UTC.

### Pacing and rate limits

Three settings control the pace (DEC-03):

| Setting         | Example | Effect                                       |
| --------------- | ------- | -------------------------------------------- |
| minimum wait    | 2 s     | time between two actions                     |
| maximum payload | 10,000  | characters in one write                      |
| retry attempts  | 3       | tries after a `429` response before stopping |

A write longer than the maximum payload is not sent. The skill stops, reports
the length and the limit, and asks the user to shorten the text (DEC-18).

On a `429` response, the skill waits for the time the `Retry-After` header
names, at most 120 seconds. When the header is missing, it waits for a set
back-off time. After the last attempt, it stops and reports the platform and
the target.

### Blocked access

When a platform blocks the automated session, the skill reports the block and
stops. It does not try to get around the block.

## Scope

**In the first release:**

- A setup step that checks what the user has available and prepares the
  browser channel (DEC-14).
- Jira through the REST call from inside the page: read a ticket with its
  fields and comments; add a comment, move the ticket through a workflow
  transition, and change its fields (DEC-10).
- Confluence through the REST call from inside the page: read a page with its
  comments; add a comment and change the page body (DEC-10).
- The `[agent]` marker, the stable rerun markers, and the local write log.
- The three pacing settings and the `429` handling.
- A precondition prompt in which the user confirms the platform terms and the
  company's automation policy.

**Explicitly deferred (do NOT plan stories for these):**

- Push delivery through webhooks or a polling service, because a skill runs
  only when someone invokes it (DEC-04).
- Code that disguises the automated session, such as stealth plugins, fake
  browser fingerprints, or a plain HTTP client that copies the browser's
  cookies and headers. This is excluded, not only deferred (DEC-02, DEC-07).
- The API and MCP channels beyond a seam where they can plug in later, because
  the browser channel covers every case the first release needs.
- Miro. Thirteen probes showed that a board can be read through Miro's
  accessibility outline and that sticky notes can be placed at a planned
  position and size. Miro needs its own procedures and its own proposal. The
  findings are in
  [probe-findings.md](../research/miro-browser-access/probe-findings.md), and
  composing whole boards is filed as
  [T-0416](../spec/work/todo.md#t-0416--write-a-canvas-composer-proposal-with-drawio-on-confluence-first)
  (DEC-12).

## Design Details

Files (DEC-15, DEC-16):

| File             | Location                                     | Committed |
| ---------------- | -------------------------------------------- | --------- |
| project settings | `docs/switchboard.yaml`                      | yes       |
| user settings    | `~/.agent-factory/switchboard/settings.yaml` | no        |
| browser profile  | `~/.agent-factory/switchboard/profile/`      | no        |
| write log        | `.agent-factory/switchboard/writes.log`      | no        |

The project settings hold the values the team shares: the Jira and Confluence
addresses and the pacing values. The user settings hold only the browser
profile path and the browser channel, such as Edge. The two files share no key,
so no rule decides between them (DEC-17). A schema allows only the known keys, and the
validation runs before every commit, so a token or cookie pasted in by mistake
is caught. The user settings, the browser profile, and the write log stay out
of the repository.

No part of the user's session may be committed. The skill enforces this rule
mechanically: before it starts the browser, it runs
`git -C <profile directory> rev-parse --is-inside-work-tree`. If the profile
directory lies inside a git work tree, the skill stops with an error and starts
no browser.

## Open Questions

None. Every question raised in the conversation has a decision in the
Appendix.

## Completion Criteria

- On a machine without Playwright, the setup names what is missing and offers
  to install it. After the install, it opens a visible browser with the
  skill's own profile.
- The profile directory has mode `700` and lies in the user's home
  directory. When the profile directory lies inside a git work tree, the
  skill stops before it starts the browser. No code path writes cookies or
  browser storage state to any other file.
- After the user signs in, one read call per platform returns the user's own
  profile.
- Given a ticket key, the skill returns the ticket's fields and comments.
  Given a page ID, it returns the page body and its comments.
- A Jira comment, a workflow transition, a field change, a Confluence comment,
  and a page body edit each work. Without `--execute`, each one only reports
  what it would do.
- Every comment the agent writes starts with `[agent]`. Every transition,
  field change, and body edit comes with an `[agent]` comment that names the
  change.
- Running the same write twice produces one comment, not two.
- Two actions are at least the set minimum wait apart. On a `429` response,
  the skill waits for `Retry-After`, at most 120 seconds, and stops with a
  report after the set number of attempts.
- Every write adds one line to the local log, with the platform, the target,
  and the time in UTC.
- The skill does not run before the user has confirmed the platform terms and
  the company's automation policy.
- When a platform blocks the session, the skill reports the block and stops.
- A write longer than the maximum payload is not sent. The skill reports the
  length and the limit and asks the user to shorten the text.

## Guiding Rule

The agent may do in the browser what its user may do, at the user's pace, and
in the open.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                                         | Raised by                  |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| DEC-01 | 2026-11-20 | decision | stakeholder | The Playwright browser is the main channel. API and MCP are optional, because enterprise admins often narrow API scopes.                                                                                                                         | VIRGIL conversation        |
| DEC-02 | 2026-11-20 | decision | stakeholder | The agent acts in the open: every write carries `[agent]`, a local log records each write, and the skill has no detection-evasion code.                                                                                                          | VIRGIL conversation        |
| DEC-03 | 2026-11-20 | decision | stakeholder | Settings for minimum wait, maximum payload, and retry attempts keep the agent inside rate limits, and a `429` response is respected.                                                                                                             | VIRGIL conversation        |
| DEC-04 | 2026-11-20 | decision | stakeholder | The first release is pull only. Push needs a running service, which a skill does not provide.                                                                                                                                                    | VIRGIL conversation        |
| DEC-05 | 2026-11-20 | decision | stakeholder | Access control is not compliance. The user confirms platform terms and company automation policy; the skill makes no compliance claim.                                                                                                           | VIRGIL conversation        |
| DEC-06 | 2026-11-20 | decision | stakeholder | The first release supports Jira, Confluence, and Miro. The Miro MCP server works only with Claude and only in a private account, so it is no substitute.                                                                                         | Open question 1            |
| DEC-07 | 2026-11-20 | decision | stakeholder | Jira and Confluence use REST calls with `fetch()` from inside a signed-in page with the skill's own persistent profile. Copying cookies to a plain HTTP client is left out.                                                                      | Review of a migration tool |
| DEC-08 | 2026-11-20 | decision | stakeholder | Miro reading uses the accessibility outline, which gives item ID, text, type, box, parent, and comments. The WebSocket route is ruled out, because its messages are binary.                                                                      | Miro probes 1 to 7         |
| DEC-09 | 2026-11-20 | decision | stakeholder | Miro writing plans each item in an offline layout model, syncs before writing, opens a targeted view with `moveToViewport`, and places the item at its planned size. No resize.                                                                  | Miro probes 8 to 13        |
| DEC-10 | 2026-11-20 | decision | stakeholder | Jira writes cover comments, workflow transitions, and fields. Confluence writes cover comments and page bodies.                                                                                                                                  | Open question 1            |
| DEC-11 | 2026-11-20 | decision | stakeholder | Miro in the first release reads whole boards and writes sticky notes and thread replies. Composing boards and editing items move to a separate canvas composer (T-0416).                                                                         | Open question 1            |
| DEC-12 | 2026-11-20 | decision | stakeholder | Miro is out of this proposal. DEC-08, DEC-09, and DEC-11 move with the probe findings to `docs/research/miro-browser-access/probe-findings.md`.                                                                                                  | VIRGIL conversation        |
| DEC-13 | 2026-11-20 | decision | stakeholder | A Jira status or field change and a Confluence page body edit each come with an `[agent]` comment in the same run, so the team can tell agent changes from the user's own.                                                                       | Open question 1            |
| DEC-14 | 2026-11-20 | decision | stakeholder | The setup checks only the browser channel: Playwright, a browser, the site addresses, and the sign-in. It does not look for API tokens or MCP servers, because the skill is deliberately built around the browser.                               | Open question 1            |
| DEC-15 | 2026-11-20 | decision | stakeholder | The browser profile and the settings live per user under `~/.agent-factory/switchboard/`; the write log lives per project. Nothing from the user's session may be committed, and the skill refuses a profile inside a git work tree.             | Open question 1            |
| DEC-16 | 2026-11-20 | decision | stakeholder | Project settings are committed in `docs/switchboard.yaml` and checked by a schema of known keys. No allow list of write actions: it would bind only agents that use the skill's scripts, so the platform's permissions stay the only real limit. | VIRGIL conversation        |
| DEC-17 | 2026-11-20 | decision | stakeholder | Project and user settings share no key. The project file holds addresses and pacing; the user file holds the profile path and the browser channel.                                                                                               | VIRGIL conversation        |
| DEC-18 | 2026-11-20 | decision | stakeholder | A write above the maximum payload is not split. The skill stops and asks the user to shorten the text, because a very long comment usually belongs on a page.                                                                                    | VIRGIL conversation        |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
