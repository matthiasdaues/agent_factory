# UC-12 — Browse Story Backlog via TUI

Realizes: AG-12

## Scope

Orchestrator TUI

## Level

User goal

## Primary Actor

Operator

## Stakeholders & Interests

- **Operator** — wants to inspect the story backlog from the terminal without memorizing commands and without risking accidental edits.
- **Product and planning owners** — want backlog views to reflect the canonical Markdown stories exactly, including identifiers, dependencies, and execution traces.
- **Delivery phases and agents** — depend on story metadata being shown faithfully, so the operator can make correct planning and execution decisions from the displayed state.

## Preconditions

- The Operator is in menu mode and can reach the `backlog` node.
- The repository is available to the TUI process.

## Postconditions

**Success Guarantee**: The Operator sees the requested read-only backlog projection. The rendered data comes from the current backlog snapshot loaded through `MarkdownBacklogStore.list_stories()` and, for story detail, `MarkdownBacklogStore.get_story()`.

**Minimal Guarantee**: The system does not mutate backlog files, derived state, or story metadata while rendering any backlog view (BR-056). If the backlog cannot be read, the system reports the problem and leaves the backlog unchanged.

## Trigger

The Operator enters `backlog` from the root TUI and selects one of its display nodes.

## Main Success Scenario

1. The Operator opens `backlog`.
2. The system loads the current story backlog through `MarkdownBacklogStore.list_stories()`.
3. The system presents four read-only display paths: `list`, `by-epic`, `ready`, and `view story` (FR-U1).
4. The Operator selects a backlog view.
5. The system renders the selected view from the loaded backlog snapshot:
   - `list` shows every story with `id`, `title`, `epic`, `tier`, `status`, and `deps` (FR-U2).
   - `by-epic` groups stories under epic headings and retains each story's status indicator (FR-U3).
   - `ready` shows only stories whose `status` is `pending` and whose dependencies all resolve to stories with `status: done` (FR-U4).
   - `view story` presents a selectable story list; after selection, the system loads that story through `get_story()` and displays its full frontmatter and prose body (FR-U5).
6. The Operator reviews the displayed information.
7. The display returns to the parent menu on keypress.

## Extensions

- **2a. The backlog is empty**
  - 2a1. The system presents an explicit empty-state message for `list`, `by-epic`, or `ready`, as applicable (BR-058).
  - 2a2. `view story` presents no selectable story and returns to the parent menu without error (BR-058).
- **2b. The backlog store cannot be read**
  - 2b1. The system reports the read failure and renders no stale or partial mutation-prone state.
  - 2b2. The system returns to the parent menu; it changes nothing (BR-056).
- **5a. The Operator selects `by-epic`**
  - 5a1. The system groups every loaded story under its epic heading and shows each story's status indicator (BR-059).
- **5b. The Operator selects `ready`**
  - 5b1. The system evaluates readiness against the same loaded backlog snapshot.
  - 5b2. A story appears only if its `status` is `pending` and every dependency identifier resolves to a story whose status is `done` (BR-057).
  - 5b3. If no stories satisfy the rule, the system presents an explicit empty-state message (BR-058).
- **5c. The Operator selects `view story`**
  - 5c1. The system presents a selectable list of story identifiers with titles.
  - 5c2. The Operator selects a story.
  - 5c3. The system loads the selected story through `MarkdownBacklogStore.get_story()`.
  - 5c4. The system displays the story's full frontmatter and prose body, including `tier`, `status`, `deps`, `traces`, and `outputs` when present (BR-060).
- **5d. A selected story is no longer retrievable**
  - 5d1. The system reports that the story could not be loaded.
  - 5d2. The system returns to the story selector or parent menu; it modifies nothing (BR-056).

## Special Requirements

- All backlog views are observational display nodes; none may provide an edit, delete, create, reorder, or status-change action (FR-U6, BR-056).
- The TUI shall use the display semantics defined for read-only screens: render the requested information and return to the parent on keypress.
- The rendered story metadata shall use the canonical story fields: `id`, `title`, `epic`, `tier`, `status`, `deps`, `traces`, and `outputs`.
- Supported `tier` values are `economy`, `standard`, and `strong`.
- Supported `status` values are `pending`, `in-progress`, `done`, and `blocked`.

## Technology and Data Variations List

- Story lists come from `MarkdownBacklogStore.list_stories()`.
- Story detail comes from `MarkdownBacklogStore.get_story()`.
- `deps` may be empty; an empty dependency list satisfies the dependency portion of the ready filter.
- `ready` is computed in memory from the loaded backlog snapshot, not from external state.

## Frequency of Occurrence

Likely frequent during planning, triage, and before execution phases that depend on backlog order or readiness.

## Business Rules

- **BR-056**: Backlog TUI views are strictly read-only. They never write, reorder, edit, or delete backlog files or derived story state.
- **BR-057**: The `ready` view includes only stories with `status: pending` whose every dependency identifier resolves, within the same loaded backlog snapshot, to a story with `status: done`. Any unresolved or non-done dependency excludes the story from `ready`.
- **BR-058**: Empty backlog conditions shall be explicit. When no stories are available for a requested display, the system shall show an empty-state message; `view story` shall not fabricate a selectable item.
- **BR-059**: Backlog summary projections shall preserve story identity and planning metadata. `list` shows `id`, `title`, `epic`, `tier`, `status`, and `deps` for every loaded story; `by-epic` groups the same stories under epic headings while retaining status indicators.
- **BR-060**: Story detail is authoritative only when loaded through `MarkdownBacklogStore.get_story()`, and it shall display the story's full frontmatter and prose body.

## Activity Diagram

```mermaid
flowchart TD
    A[Operator opens backlog menu] --> B[Load stories via list_stories()]
    B --> C{Load succeeded?}
    C -->|no| D[Report read failure<br/>modify nothing — BR-056]
    C -->|yes| E{Any stories loaded?}
    E -->|no| F[Show explicit empty state<br/>BR-058]
    E -->|yes| G[Show read-only options:<br/>list / by-epic / ready / view story]
    G --> H{Selected view}
    H -->|list| I[Render table:<br/>id, title, epic, tier, status, deps]
    H -->|by-epic| J[Group stories under epic headings<br/>retain status]
    H -->|ready| K[Filter pending stories<br/>with all deps done — BR-057]
    H -->|view story| L[Show selectable story list]
    L --> M{Story selected?}
    M -->|no| N[Return to parent menu]
    M -->|yes| O[Load story via get_story()]
    O --> P{Story retrieved?}
    P -->|no| Q[Report retrieval failure<br/>modify nothing — BR-056]
    P -->|yes| R[Display full frontmatter<br/>and prose body]
    I --> S[Any key returns to parent]
    J --> S
    K --> S
    R --> S
    F --> S
    D --> S
    Q --> S
```

## Acceptance Criteria

```gherkin
Feature: Browse story backlog through the TUI

  Scenario: List view shows every story in tabular form
    Given the backlog contains multiple stories
    When the Operator selects backlog > list
    Then the system displays every story returned by list_stories()
    And each row shows id, title, epic, tier, status, and dependencies
    And the view does not modify backlog data

  Scenario: By-epic view groups stories under epic headings
    Given the backlog contains stories from more than one epic
    When the Operator selects backlog > by-epic
    Then the system groups stories under epic headings
    And each displayed story retains a visible status indicator
    And the view is read-only

  Scenario: Ready view filters by pending status and completed dependencies
    Given a story with status pending whose dependencies are all done
    And a different story with status pending whose dependency is not done
    When the Operator selects backlog > ready
    Then the first story appears in the ready view
    And the second story does not appear in the ready view

  Scenario: Story detail shows full frontmatter and prose body
    Given the backlog contains a story with frontmatter and prose body
    When the Operator selects backlog > view story
    And selects that story from the story list
    Then the system loads the story through get_story()
    And the display shows the full frontmatter and prose body
    And the display remains read-only

  Scenario: Empty backlog is handled explicitly
    Given the backlog contains no stories
    When the Operator selects backlog > list
    Then the system shows an explicit empty-state message
    When the Operator selects backlog > view story
    Then the system offers no selectable story
    And it returns safely without mutation

  Scenario: Read failure does not alter backlog state
    Given the backlog store cannot be read
    When the Operator opens a backlog view
    Then the system reports the read failure
    And it does not modify backlog files or derived state
```
