# A1-SR-06: PostgreSQL 18 manual on constraints, triggers, privileges, row security, rules and multicolumn indexes

```json
{
  "source_identity": "PostgreSQL 18 manual: 5.5 Constraints (ddl-constraints.html), 37.1 Overview of Trigger Behavior (trigger-definition.html), CREATE TRIGGER (sql-createtrigger.html), 41.9 PL/pgSQL Errors and Messages (plpgsql-errors-and-messages.html), 5.8 Privileges (ddl-priv.html), 5.9 Row Security Policies (ddl-rowsecurity.html), CREATE RULE (sql-createrule.html), TRUNCATE (sql-truncate.html), 11.3 Multicolumn Indexes (indexes-multicolumn.html); all under https://www.postgresql.org/docs/current/",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for the current release. Same lineage as A1-SR-05, A1-SR-07 and A1-SR-08.",
  "precise_evidence_location": "5.5.1 Check Constraints, note on cross-row checks; 5.5.5 Foreign Keys; 37.1, paragraphs on BEFORE and AFTER row triggers; CREATE TRIGGER, Description, constraint triggers; 41.9.1 RAISE, level EXCEPTION; 5.8, opening paragraphs and privilege list; 5.9, opening paragraphs; CREATE RULE, Description; TRUNCATE, Notes; 11.3, B-tree paragraph",
  "method": "Project manual that states syntax and behaviour.",
  "limitations": "Same dating as A1-SR-05. The manual describes each mechanism on its own; it gives no recipe for an append-only table or for a trigger that checks node kinds. Those uses are inferred, and each inference is marked below.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text with pandoc. Re-verify at the URLs above or at /docs/18/."
}
```

## Evidence

- 5.5.1: "PostgreSQL does not support CHECK constraints that reference table data other than the new or updated row being checked."
- 5.5.1: "If what you desire is a one-time check against other rows at row insertion, rather than a continuously-maintained consistency guarantee, a custom trigger can be used to implement that."
- 5.5.1: "If possible, use UNIQUE, EXCLUDE, or FOREIGN KEY constraints to express cross-row and cross-table restrictions."
- 5.5.5: "A foreign key constraint specifies that the values in a column (or a group of columns) must match the values appearing in some row of another table."
- 37.1: "Row-level AFTER triggers are most sensibly used to propagate the updates to other tables, or make consistency checks against other tables."
- CREATE TRIGGER: "Constraint triggers are expected to raise an exception when the constraints they implement are violated."
- 41.9.1: "EXCEPTION raises an error (which normally aborts the current transaction); the other levels only generate messages of different priority levels."
- 5.8: "The right to modify or destroy an object is inherent in being the object's owner, and cannot be granted or revoked in itself."
- 5.8 lists UPDATE, DELETE and TRUNCATE as separate privileges on a table.
- 5.9: "Operations that apply to the whole table, such as TRUNCATE and REFERENCES, are not subject to row security."
- 5.9: "Superusers and roles with the BYPASSRLS attribute always bypass the row security system when accessing a table."
- TRUNCATE, Notes: "TRUNCATE will not fire any ON DELETE triggers that might exist for the tables."
- CREATE RULE: "If you actually want an operation that fires independently for each physical row, you probably want to use a trigger, not a rule."
- 11.3: "A multicolumn B-tree index can be used with query conditions that involve any subset of the index's columns, but the index is most efficient when there are constraints on the leading (leftmost) columns."
- Statement S2 (inferred): a foreign key from `edge.type` to `edge_type` is a plain constraint. The node-kind check reads two other rows of `node`, which a CHECK constraint must not do, so the manual points to a trigger. The trigger checks at insert time only. A later change to a node's kind is not checked unless a trigger on `node` checks it too.
- Statement S3 (inferred): a table can be made append-only for ordinary roles by granting INSERT and SELECT but not UPDATE, DELETE or TRUNCATE, or by BEFORE UPDATE and BEFORE DELETE triggers that raise an exception. Row-level triggers do not catch TRUNCATE; a statement-level TRUNCATE trigger or the missing privilege must. The table owner and superusers keep the right to change or drop the table.
- Statement S4 (inferred): an index on `(source_id, type)` serves lookups by `source_id`, with or without `type`; an index on `(target_id, type)` does the same in the other direction.
- What the source shows: the building blocks for S2, S3 and S4 and their limits.
- What the source does not show: a check that these mechanisms together stop every update. The owner and superuser exceptions remain.
