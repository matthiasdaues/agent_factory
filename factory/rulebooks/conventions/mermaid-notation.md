---
title: Mermaid Notation
category: implementation
enforcement: mermaid-lint
version: 1.0.0
---

# Mermaid Notation

## Rule

Canonical statement: [rules.md § Mermaid notation](../rules.md#mermaid-notation).

Mermaid blocks must use one statement per line. They must not use raw
semicolons as statement separators or punctuation. Mermaid interprets a raw
semicolon in prose as a statement boundary in diagram types such as sequence
diagrams, which can prevent the block from rendering.

Use a period, comma, colon, or em dash in prose instead. If the rendered text
genuinely requires a semicolon, encode it as the Mermaid entity `#59;`.

## Examples

Invalid:

```text
Note over D,DB: The Task Result remains undecided; it is never aggregated.
```

Valid:

```text
Note over D,DB: The Task Result remains undecided. It is never aggregated.
```

Also valid when a literal semicolon is essential to the rendered text:

```text
Note over D,DB: The first clause#59; the second clause
```

## Enforcement

The `factory/scripts/mermaid-lint` pre-commit gate inspects fenced Mermaid
blocks in Markdown. It reports each raw semicolon with its file, line, and
column while allowing valid named and numeric Mermaid entity escapes.
