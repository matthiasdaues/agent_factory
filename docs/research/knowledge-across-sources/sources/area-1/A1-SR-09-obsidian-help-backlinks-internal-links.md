# A1-SR-09: Obsidian Help, Backlinks and Internal links pages

```json
{
  "source_identity": "Obsidian Help, pages 'Backlinks' (en/Plugins/Backlinks.md) and 'Internal links' (en/Linking notes and files/Internal links.md), repository obsidianmd/obsidian-help, branch master; published at https://help.obsidian.md/plugins/backlinks",
  "author_or_issuing_body": "Obsidian, documentation team (as maintainers of the obsidianmd/obsidian-help repository)",
  "publisher": "Obsidian, via GitHub repository obsidianmd/obsidian-help",
  "publication_date": "2026-11-16T15:49:12Z",
  "relevant_event_date": "2026-03-24",
  "source_family": "Primary for the features the vendor documents. Obsidian documentation lineage.",
  "precise_evidence_location": "Backlinks.md: opening paragraphs and section 'Show backlinks'. Internal links.md: opening paragraphs, section 'Link to a block in a note', and the 'Interoperability' warning",
  "method": "Vendor user documentation that states product features.",
  "limitations": "Tool documentation; it states features, not use or adoption. publication_date is the last commit to Internal links.md; relevant_event_date is the last commit to Backlinks.md, per the GitHub commits API. The documentation does not describe how the backlink index is built or stored.",
  "provenance": "Raw markdown files downloaded with curl from raw.githubusercontent.com on 2026-11-18; commit dates read from the GitHub commits API the same day. Re-verify in the repository history."
}
```

## Evidence

- Backlinks.md: "A backlink for a note is a link from another note to that note."
- Backlinks.md: "**Linked mentions** are backlinks to the notes that contain an internal link to the active note."
- Backlinks.md: "**Unlinked mentions** are backlinks to any unlinked occurrence of the name of the active note."
- Backlinks.md: "Just imagine if you could list the backlinks for any website on the internet."
- Internal links.md: "Obsidian can automatically update internal links in your vault when you rename a file."
- Internal links.md: "You can link to a block by adding `#^` at the end of your link destination, followed by a unique block identifier."
- Internal links.md: "Block references are specific to Obsidian and not part of the standard Markdown format. Links containing block references won't work outside of Obsidian."

What the source shows: the link is written one-way in the source note, and the tool shows the reverse direction as a computed backlink list. That matches the background-process option in A1-SR-07, inside one vault. Rename updates keep links from breaking inside the vault. Block identifiers give links a target finer than a note.

What it does not show: any record of who made a link or when, or backlinks across separate vaults.
