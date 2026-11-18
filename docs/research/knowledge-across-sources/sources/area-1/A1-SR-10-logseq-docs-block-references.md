# A1-SR-10: Logseq documentation, block references and block embeds

```json
{
  "source_identity": "Logseq documentation pages 'Block Reference', 'Page and block references', 'The difference between block embeds and block references' and 'Linked References', repository logseq/docs, branch master, folder pages/",
  "author_or_issuing_body": "Logseq project, documentation contributors",
  "publisher": "Logseq, via GitHub repository logseq/docs (published at docs.logseq.com)",
  "publication_date": "2026-10-21T12:49:12Z",
  "relevant_event_date": "2023-02-22",
  "source_family": "Primary for the features the project documents. Logseq documentation lineage.",
  "precise_evidence_location": "pages/Block Reference.md (description and 'Functionality'); pages/Page and block references.md ('Usage'); pages/The difference between block embeds and block references.md (first bullet); pages/Linked References.md (whole page)",
  "method": "Project user documentation that states product features.",
  "limitations": "Tool documentation; it states features, not use or adoption. publication_date is the latest commit to the repository, not to these files. relevant_event_date is the date in a screenshot file name on the Block Reference page and is approximate. The 'Linked References' page is a stub, so this record has no documented statement of how Logseq computes linked references.",
  "provenance": "Raw markdown files downloaded with curl from raw.githubusercontent.com on 2026-11-18; the latest commit date read from the GitHub commits API the same day. Re-verify in the repository history."
}
```

## Evidence

- Block Reference.md, description: "Clickable link to a particular Logseq block e.g. `((123e4567-e89b-12d3-a456-426614174000))`. Produced by putting a unique [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) inside parenthesis `(())`"
- Block Reference.md: "A block that has references will have a reference counter to its right."
- Block Reference.md: "Clicking on that reference counter will expand all of its block linked references and group them by page"
- Page and block references.md: "Type `[[]]` to create or reference any other page." and "Type `(())` to reference a block on any page."
- Embeds page: "If a block reference is a window to another part of your database, a block embed is a portal. Embeds allow you to edit the source directly".
- Linked References.md: "TODO Document this feature #docs"

What the source shows: Logseq links target pages or single blocks by UUID, counts incoming references on the target block, and offers embeds that show and edit the source block in place. The embed is a re-use connection close to transclusion in A1-SR-03, inside one graph.

What it does not show: how linked references are computed, any record of who made a reference, or references across graphs.
