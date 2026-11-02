# Structurizr DSL Reference

Disclosed reference for the `scaffold-arc42` skill.

## Minimal workspace

The DSL file lives at `docs/spec/architecture.dsl`.

```dsl
workspace "System Name" "One-line description" {

    properties {
        "arc42.projected" "false"
    }

    model {
        user = person "User" "Role description"

        system = softwareSystem "System Name" "What it does" {
            api = container "API" "Handles requests" "Python/FastAPI"
            db  = container "Database" "Stores data" "PostgreSQL"
        }

        user -> api "Uses" "HTTPS"
        api -> db "Reads/writes" "SQL"
    }

    views {
        systemContext system "SystemContext" {
            include *
            autoLayout
        }

        container system "Containers" {
            include *
            autoLayout
        }

        theme ../assets/themes/default/theme.json
    }
}
```

## Key elements

| Element         | Syntax                                        | Notes                         |
| --------------- | --------------------------------------------- | ----------------------------- |
| Person          | `person "Name" "Description"`                 | External actor                |
| Software System | `softwareSystem "Name" "Description"`         | The system or an external one |
| Container       | `container "Name" "Description" "Technology"` | Inside a softwareSystem block |
| Component       | `component "Name" "Description" "Technology"` | Inside a container block      |
| Relationship    | `source -> dest "Label" "Technology"`         | Technology is optional        |

## CLI commands

All operations run inside Docker via the project wrapper script — no local Structurizr install needed.

```bash
# Validate the DSL
.agent-factory/factory/scripts/structurizr validate

# Export PNG to docs/assets/images/
.agent-factory/factory/scripts/structurizr export-png

# Export SVG to docs/assets/images/
.agent-factory/factory/scripts/structurizr export-svg

# Export both SVG and PNG
.agent-factory/factory/scripts/structurizr export-all

# List all view keys defined in the workspace
.agent-factory/factory/scripts/structurizr list-views
```

The script mounts `docs/`, reads `docs/spec/architecture.dsl`, and outputs to `docs/assets/images/`. The theme at `docs/assets/themes/` sits inside the mount, so the DSL reaches it as `../assets/themes/default/theme.json`. Override the docs directory with `STRUCTURIZR_DOCS=<path>` and the DSL path inside it with `STRUCTURIZR_WORKSPACE=<path>` (default `spec/architecture.dsl`).

## Rules

- The DSL file `docs/spec/architecture.dsl` is the versioned source of truth. Exported images are derived artifacts.
- One workspace per project. Multiple views within the same workspace.
- Use `autoLayout` unless manual positioning is needed for clarity.
- Tag elements for styling: `element "Tag" { ... }` in the `styles` block.
- Exported files are named `<ViewKey>.<format>` (the `structurizr-` prefix is stripped automatically by the script).
