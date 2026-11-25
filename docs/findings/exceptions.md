# Exceptions register

## CRAP score

| File                                      | Function   | Accepted score | Reason                                                                                                                                                | Accepted by    |
| ----------------------------------------- | ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| `packages/factory/scripts/init-factory`   | `do_add`   | 343            | Complexity 25 with 20 % coverage: no test passes --add yet. Accepted 2026-11-24 until init-factory moves into the Python package (IMPL-0117, DEC-87). | Matthias Daues |
| `packages/factory/scripts/init-factory`   | `_install` | 39             | Complexity 30 with 79 % coverage; fails on complexity. Accepted 2026-11-24 until the split of large functions (IMPL-0117, DEC-87).                    | Matthias Daues |
| `packages/factory/scripts/update-factory` | `main`     | 62             | Complexity 57 with 89 % coverage; fails on complexity. Accepted 2026-11-24 until the split of large functions (IMPL-0117, DEC-87).                    | Matthias Daues |
