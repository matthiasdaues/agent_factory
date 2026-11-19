# A2-SR-21: pgvectorscale source code at commit 3ae6fcc

```json
{
  "source_identity": "timescale/pgvectorscale source at commit 3ae6fccff8fe451f55825752e46a60b42dfdfa0d: pgvectorscale/vectorscale.control, pgvectorscale/Cargo.toml, pgvectorscale/src/util/page.rs, pgvectorscale/src/access_method/mod.rs, pgvectorscale/src/access_method/labels/mod.rs, .github/workflows/pgrx_test.yaml, LICENSE, NOTICE; https://github.com/timescale/pgvectorscale",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), pgvectorscale maintainers",
  "publisher": "GitHub",
  "publication_date": "2026-10-14T19:56:37Z",
  "relevant_event_date": "2026-10-14",
  "source_family": "Primary: source code of the extension. Same lineage as A2-SR-20 and A2-SR-22.",
  "precise_evidence_location": "vectorscale.control lines 1 to 6; Cargo.toml [features] lines 13 to 19; page.rs lines 104 to 125, 172 to 175, 230 and 241; access_method/mod.rs function amhandler, lines 46 to 80; labels/mod.rs type Label (line 11) and LabeledVector::from_scan_key_data (lines 209 to 238); pgrx_test.yaml matrix lines 15 to 25; LICENSE line 1; NOTICE lines 1 to 5",
  "method": "Code reading by the researcher. The code was not built or run. Statements about runtime behaviour are inferences from the code.",
  "limitations": "Code reading only: no crash, standby, rollback, or pg_dump test was run. The grep for GenericXLog found every write path in page.rs; a write path outside that file was not searched for beyond a grep for XLogInsert and log_newpage, which found none. The behaviour of a scan with several label conditions is inferred from one function. The repository has no text on replication or pg_dump; a case-insensitive grep for 'pg_dump', 'replica', and 'standby' over the whole tree found nothing.",
  "provenance": "Shallow clone with `git clone --depth 1` on 2026-11-19; HEAD 3ae6fccff8fe451f55825752e46a60b42dfdfa0d. sha256: page.rs a4a733bc5e9d8c707a3694e2a878a5a2ccf2c2eac1056398123c2902842d8c24, access_method/mod.rs 951a293cb1eba8443ccf33b1fa1028226410401da74917788c80645ed73367ad, labels/mod.rs c9e95b36a1b0ebea878fd2ce387760020a1c5ca615471c71641c1910c8e467d8, vectorscale.control 288b13e760b1818e22f85b7566b1c1af72295cc422bf734ea5a053412667495f, Cargo.toml 5490ded4aba0838cff19f1eb8fe5e6fa2ec61daa2b74a7479a4d45d93bb4b3b2, LICENSE 1fb31b095ba8b0188bc2c7eaff8d69028c2f4cfb19aaf8bd463121e7008f1e83. Re-verify at the commit above."
}
```

## Evidence

The quotes are copied from the files. My notes stand outside the quotes.

- Control file: "comment = 'diskann access method for vector search'", "superuser = true", and "requires = 'vector'". My reading: the extension depends on pgvector, and creating it needs a superuser, because the file does not mark it as trusted.
- PostgreSQL versions, Cargo.toml: the `[features]` table has one entry per version from `pg14 = ["pgrx/pg14", "pgrx-tests/pg14"]` to `pg18 = ["pgrx/pg18", "pgrx-tests/pg18"]`, and `default = ["pg18", "build_parallel"]`. These are code, copied exactly. The test workflow runs PostgreSQL 14, 15, 16, 17, and 18 against pgvector 0.8.1. No pg19 feature exists.
- WAL, page.rs: "/// WritablePage implements and RAII-guarded Page that you can write to." and "/// All writes will be WAL-logged." Every writable page starts with "pg_sys::GenericXLogStart(index.as_ptr());" and ends with "pg_sys::GenericXLogFinish(self.state);"; a dropped page calls "pg_sys::GenericXLogAbort(self.state);". My reading: index writes use PostgreSQL generic WAL, with no custom resource manager, so a physical standby replays them with core code. The same reading for pg_textsearch v1.3.0 is in A2-SR-01. No test confirms it here.
- Access method flags, amhandler: "amroutine.amcanorderbyop = true;", "amroutine.amcanmulticol = true;", "amroutine.amcanunique = false;", "amroutine.ampredlocks = false;", and "amroutine.amcanparallel = false; //TODO". The handler sets "amroutine.ambulkdelete = Some(vacuum::ambulkdelete);". My reading: the index returns heap pointers and the executor checks visibility, as for any index type, so rolled-back rows stay invisible and vacuum removes their entries. The flag ampredlocks = false means the index takes no page-level predicate locks under `SERIALIZABLE`; what PostgreSQL does instead is not recorded here.
- Label type, labels/mod.rs: "pub type Label = i16;" and "LabelSet is a set of labels. It is stored as a sorted array of labels."
- Label conditions in a scan, from_scan_key_data: "let arr = unsafe { Array::<i16>::from_datum(keys[0].sk_argument, false).unwrap() };". My reading: the index scan reads only the first label condition. A second `&&` condition in the same `WHERE` is checked after the scan. Issue #257 asked for conjunctive conditions and was closed as not planned (A2-SR-22).
- Licence: LICENSE starts "The PostgreSQL License". NOTICE: "Copyright (c) 2023-2026 Timescale, Inc. d/b/a Tiger Data. All Rights Reserved." and "Licensed under the PostgreSQL License".
- Not shown: a test of crash recovery, standby replay, `ROLLBACK`, or `pg_dump`, and any check that a partial diskann index with a `WHERE` predicate works.
