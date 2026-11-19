---
id: FAGAN-0002
source: fagan-review
artifact: packages/server/backend/src/gigacron_server/bootstrap/routes.py:37
traces: []
---

# The frontend static-file route allows path traversal

**What is wrong:** `GET /ui/{asset_path:path}` joins the unvalidated `asset_path` path parameter
directly onto `static_dir` with `static_dir / asset_path` and serves whatever file results. A
literal `../` in the URL is rejected by routing (404), but a URL-encoded traversal sequence such as
`GET /ui/..%2f..%2fsecret%2fsecret.txt` bypasses that and reaches a `FileResponse` for a path outside
`static_dir`. This was reproduced with a `TestClient` against the exact route logic: the encoded
request returned status 200 with the contents of a file placed outside the served directory. Because
uvicorn serves this route directly with no normalizing reverse proxy in front of it, any file
readable by the server process (for example `.env`, source code, or credentials mounted into the
container) can be read by an unauthenticated client. This is a Path Traversal vulnerability (CWE-22,
OWASP A01:2021 — Broken Access Control). No test exists for this route.

**Fix:** Resolve `requested_file` and confirm it stays inside `static_dir` before checking
`exists()`/`is_file()`, e.g.:

```python
static_root = static_dir.resolve()
requested_file = (static_dir / asset_path).resolve()
if requested_file.is_relative_to(static_root) and requested_file.is_file():
    return FileResponse(requested_file)
return FileResponse(static_dir / "index.html")
```

Add a regression test that requests an encoded traversal sequence (e.g. `/ui/..%2f..%2fetc%2fpasswd`
or an out-of-tree fixture file) and asserts the response is the `index.html` fallback, not the
external file.
