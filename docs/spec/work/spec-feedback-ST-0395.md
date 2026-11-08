# Spec feedback of ST-0395

| Artifact                        | Drift                                                                                                                                                          | Evidence                                     | Owner                   | Status |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------- | ------ |
| `docs/spec/validation-rules.md` | BR-089 does not say which version of `docs/factory-settings.yaml` a check with `--staged` reads; the lint reads the working-tree file, not the staged version. | `packages/factory/scripts/finding-lint:1319` | `domain-modeling-agent` | `open` |
