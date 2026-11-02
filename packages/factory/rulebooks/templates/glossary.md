---
title: Glossary Template
version: 2.0.0
---

# Glossary Template

Skeleton for `docs/spec/glossary.md`, the one file that holds a project's domain terms. Governed by [context-format.md](../conventions/context-format.md).

Each `##` section covers one bounded context or one topic, such as acronyms. Each section holds one table with the columns Term, Definition, and Avoid, in this order. A term appears at most once inside one section. Avoid lists the words not to use for the term and may be empty.

```md
# Glossary

## {Context or topic name}

| Term     | Definition                                               | Avoid                  |
| -------- | -------------------------------------------------------- | ---------------------- |
| Order    | {One or two sentences that say what the term is.}        | Purchase, transaction  |
| Invoice  | A request for payment sent to a customer after delivery. | Bill, payment request  |
| Customer | A person or organization that places orders.             | Client, buyer, account |

## Acronyms and Abbreviations

| Term | Definition               | Avoid |
| ---- | ------------------------ | ----- |
| SLA  | Service level agreement. |       |
```

## Referenced from

- [context-format.md § Structure](../conventions/context-format.md#structure)
- [domain-modeling § Update docs/spec/glossary.md inline](../../skills/domain-modeling/SKILL.md#update-docsspecglossarymd-inline)
