---
title: Review Finding Table Template
version: 1.1.0
---

# Review Finding Table Template

Row skeleton for the finding table in any review report. Governed by [report-format.md](../conventions/report-format.md).

| Finding                      | Artifact                | Category                              | Severity                        | Filed as                                                         |
| ---------------------------- | ----------------------- | ------------------------------------- | ------------------------------- | ---------------------------------------------------------------- |
| [what is wrong + what to do] | [file:line or doc path] | Defect / Risk / Suggestion / Question | critical / major / minor / note | \[finding file ID, register file ID, `report only`, or todo ID\] |

The severity is the one that the rule of the finding's class computes, as [finding-classification.md](../conventions/finding-classification.md) describes. A `note` stays a row of this table only.

## Referenced from

- [report-format.md § Finding table](../conventions/report-format.md#finding-table)
