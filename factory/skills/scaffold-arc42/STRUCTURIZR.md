# Structurizr DSL Reference

Disclosed reference for the `scaffold-arc42` skill.

## Minimal workspace

The DSL file lives at `docs/arc42/architecture.dsl`.

```dsl
workspace "System Name" "One-line description" {

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

        theme default
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
factory/scripts/structurizr validate

# Export PNG to docs/assets/images/
factory/scripts/structurizr export-png

# Export SVG to docs/assets/images/
factory/scripts/structurizr export-svg

# Export both SVG and PNG
factory/scripts/structurizr export-all

# List all view keys defined in the workspace
factory/scripts/structurizr list-views
```

The script defaults to `docs/arc42/architecture.dsl` and outputs to `docs/assets/images/`. Override the docs directory with `STRUCTURIZR_DOCS=<path>`.

## Rules

- The DSL file `docs/arc42/architecture.dsl` is the versioned source of truth. Exported images are derived artifacts.
- One workspace per project. Multiple views within the same workspace.
- Use `autoLayout` unless manual positioning is needed for clarity.
- Tag elements for styling: `element "Tag" { ... }` in the `styles` block.
- Exported files are named `<ViewKey>.<format>` (the `structurizr-` prefix is stripped automatically by the script).
