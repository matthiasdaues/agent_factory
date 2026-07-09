# Retrospective Report Format

## Metadata

```
# Session Retrospective — YYYY-MM-DD

**Session scope**: <one-line summary of what the session accomplished>
**Duration**: <approximate session length>
**Mode**: <interactive / autonomous / mixed>
```

## Sections

### ✅ Went Well

Bullet list. Each item: what happened, why it was good, concrete evidence.

```markdown
- **<Practice or event>** — <why it worked>. <Evidence: specific file, finding, or outcome>.
```

### ⚠️ Caused Friction

Table format. Every row must have a root cause and a cost.

```markdown
| Friction | Root cause | Cost |
|----------|-----------|------|
| <what happened> | <why it happened> | <time lost, rework, risk> |
```

### 🛑 Stop Doing

Bullet list. Each item: the practice to stop and why, citing this session's evidence.

```markdown
- **<Practice>**. <Why it's counterproductive>. Evidence: <what happened this session>.
```

### ▶️ Continue Doing

Bullet list. Each item: the practice to continue and why it works.

```markdown
- **<Practice>** — <why it works>. Evidence: <what happened this session>.
```

### 🆕 Start Doing

Bullet list. Each item: the new practice and how to adopt it.

```markdown
- **<Practice>** — <how to adopt>. Emerged from: <what happened this session>.
```

### Action Items

Table of confirmed action items extracted from Stop/Continue/Start.

```markdown
| # | Action | Category | Tracked in |
|---|--------|----------|-----------|
| 1 | <actionable task> | Start/Stop/Continue | <todo ID, issue #, or skill/agent update> |
```

Items not confirmed by the user are omitted.
