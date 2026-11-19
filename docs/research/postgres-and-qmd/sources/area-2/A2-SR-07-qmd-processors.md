# A2-SR-07: qmd collection processors, docs/PROCESSORS.md and src/processor-store.ts

```json
{
  "source_identity": "docs/PROCESSORS.md and src/processor-store.ts of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: documentation and source code of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-06 and A2-SR-08 to A2-SR-12.",
  "precise_evidence_location": "docs/PROCESSORS.md lines 1-5, 25-31, 33-60; src/processor-store.ts lines 17-31",
  "method": "Read both files in the clone at the stated commit.",
  "limitations": "Processors are new in 2.9.0 (A2-SR-10). The record reads documented behaviour and the DDL; it does not trace processor execution code. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:docs/PROCESSORS.md."
}
```

## Evidence

- Line 3: "A processor converts each matched source file into zero or more Markdown index documents. This is useful for JSON exports, logs, or other formats containing several independent records. Generated documents live only in the index, not on disk."
- Callbacks must be idempotent: "Callbacks may be invoked again after failure or a crash: keep them idempotent and side-effect-free."
- CLI processors are argv commands gated by qmd trust; the doc warns: "**This is not an OS sandbox. A trusted command can read files and use the network with the operating-system user's authority.**"
- processor-store.ts: tables processor_specs, processor_modes, processor_sources(collection, source, fingerprint, output_count) and processor_outputs(collection, source, path, hash, current).
- Shows: the one documented extension point that turns non-markdown input into indexed documents, with a source-to-output mapping table. Inferred: processor_outputs records which source file produced which index document, which is file-level provenance for generated documents. Does not show: provenance below the file level, or any way for a processor to emit relations between documents other than metadata strings (A2-SR-06).
