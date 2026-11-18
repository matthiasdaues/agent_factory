# Spec feedback for ST-0408

| Artifact                    | Drift                                                                                                                                                                                                       | Evidence                                | Owner                   | Status      |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ----------------------- | ----------- |
| `docs/spec/entity-model.md` | `DISPATCH_LEDGER` says an entry's `deps` holds the stories it depends on inside the run, but `init` and `plan` write every dependency of the backlog, so a `done` dependency outside the run is listed too. | `packages/factory/scripts/dispatch:718` | `domain-modeling-agent` | `confirmed` |
