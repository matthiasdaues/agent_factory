---
title: "Comparison Note: Named Views"
---

# Comparison Note: Named Views

**Tools:** `@dbml/core` 11.0.0 and `@softwaretechnik/dbml-renderer` 1.0.31 in
the volume `dsl-poc-dbml-node`; `linkml` 1.12.1 in the volume
`dsl-poc-linkml-venv`; `minlag/mermaid-cli` 12.0.0. **Gigacron:** `40954f18`.
**Run on:** 2026-10-29. Exit codes of all four steps:
[exit-codes.txt](../views/runs/exit-codes.txt).

## Result in short

DBML names the view in the model, and a thin wrapper renders it with keys,
the composite reference, and the enum values. LinkML renders a class subset
natively, but the model cannot name the view, the composite reference to
`attempt` is missing, and lines lead to classes outside the view.

## Definition of Done

**1. Plain renderer on the DBML view.** The model
[acid-slice-views.dbml](../views/acid-slice-views.dbml) is the DBML slice plus:

```text
DiagramView runtime {
  Tables {
    task_instance
    attempt
    outbox
  }
}
```

`dbml-renderer` exits 1 on it, even with the `checks` blocks removed:
`Could not parse input at line 268:1. Expected "/*", "//", "Enum", "Note", "Project", "Ref", "Table", "TableGroup", "\n", "\r", end of input, or space but "D" found.` ([1-dbml-renderer-on-view.out](../views/runs/1-dbml-renderer-on-view.out)).
The renderer does not know `DiagramView`.

**2. Wrapper for the DBML view.** [dbml-views.sh](../views/dbml-views.sh) asks
`@dbml/core` for each view's tables, copies those `Table` blocks, the `Enum`
blocks they use, and the `Ref` lines between them from the source, removes
`checks` blocks, and runs `dbml-renderer`:

```bash
views/dbml-views.sh views/acid-slice-views.dbml out/views
```

Exit 0. The generated input is
[dbml-runtime.generated.dbml](../views/runs/dbml-runtime.generated.dbml): three
tables, four enums, and two references, `attempt_task_instance_fk` and the
composite `outbox_attempt_fk`. Output: [dbml-runtime.svg](../out/views/dbml-runtime.svg).

A first attempt rebuilt the view through `@dbml/core`'s own JSON export and
import. The import rejected the exported JSON with
`[{"location":{"start":{"line":1,"column":1}},"error":"error"}]`, so the
wrapper copies text blocks instead.

**3. LinkML subset.**

```bash
gen-erdiagram -f mermaid -c TaskInstance -c Attempt -c Outbox \
  --no-follow-references acid-slice.yaml > out/views/linkml-runtime.mmd
mmdc -i linkml-runtime.mmd -o linkml-runtime.svg
```

Both exit 0. Output: [linkml-runtime.mmd](../out/views/linkml-runtime.mmd) and
[linkml-runtime.svg](../out/views/linkml-runtime.svg).

**4. What each SVG shows.**

| Aspect                                   | DBML view                   | LinkML subset                                                                             |
| ---------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------- |
| View named in the model                  | yes, `DiagramView runtime`  | no; the class list lives in the command line                                              |
| Tool support                             | wrapper around the renderer | native option `-c`                                                                        |
| Tables or classes drawn                  | exactly the three           | the three plus a box `Any` for the JSON slots                                             |
| Lines to entities outside the view       | none                        | `TaskInstance` → `Plan`, `TaskInstance` → `TaskVersion`, despite `--no-follow-references` |
| Composite reference `outbox` → `attempt` | drawn                       | missing; LinkML cannot express it                                                         |
| Keys marked                              | yes                         | no                                                                                        |
| Enum values                              | drawn as separate boxes     | type names only                                                                           |

## Wrapper cost

`dbml-views.sh` copies text blocks with regular expressions and depends on
the source layout: one block per `Table`, `Enum`, and `Ref` line, each starting
in column 1. It goes away when a renderer reads `DiagramView` itself. LinkML
needs a convention outside the language to store view names, for example a
class annotation, and a loop that calls `gen-erdiagram` once per view.
