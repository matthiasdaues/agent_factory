# A2-SR-12: qmd MCP and HTTP server, src/mcp/server.ts, and DESIGN.md

```json
{
  "source_identity": "src/mcp/server.ts and DESIGN.md of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: source code and design note of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-11.",
  "precise_evidence_location": "src/mcp/server.ts registerTool calls at lines 335, 513, 590, 663, 706; HTTP routes at lines 2085, 2095, 2283; DESIGN.md lines 1-5; package.json fields bin, dependencies, engines",
  "method": "Read the tool registrations and route checks in the clone; read DESIGN.md and package.json in full.",
  "limitations": "The tool handlers were not traced. The record lists interfaces; it does not test them. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:src/mcp/server.ts."
}
```

## Evidence

- DESIGN.md lines 3-5: "QMD is a command-line search tool, library, and MCP server. This change has no graphical surface."
- server.ts registers five tools, in order: "query", "get", "multi_get", "status", "metadata". All five read the index; none writes documents.
- HTTP routes: GET "/health", POST "/query" and "/search", and "/mcp".
- package.json: bin qmd; runtime dependencies @modelcontextprotocol/server 2.4.0, better-sqlite3 13.2.0, node-llama-cpp 3.22.3, sqlite-vec 0.1.9, four tree-sitter grammars, web-tree-sitter, yaml, zod, fast-glob, picomatch; engines node >=22.0.0; license MIT.
- Shows: three interfaces (CLI, SDK, MCP over stdio or HTTP) over one SQLite file. Does not show: a write interface through MCP; writes go through the files on disk and qmd update, or the SDK.
