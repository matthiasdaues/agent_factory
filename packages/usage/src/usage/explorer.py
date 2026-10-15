"""Web-based SQL explorer for persistent usage DuckDB files.

Usage::

    uv run python -m usage.explorer path/to/usage.duckdb
    uv run python -m usage.explorer path/to/usage.duckdb 9000  # custom port
"""

from __future__ import annotations

import json
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn

import duckdb

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Usage Explorer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#181926;--surface:#1e2030;--raised:#262840;
  --border:#353856;--border2:#434669;
  --fg:#cad3f5;--fg2:#a5adcb;--muted:#6e738d;
  --accent:#8aadf4;--accent2:#b7bdf8;
  --ok:#a6da95;--warn:#eed49f;--err:#ed8796;
  --cc:#d08860;--cx:#7498c8;--cp:#6aad6e;--pi:#c8a74a;
  --mono:'JetBrains Mono','SF Mono','Cascadia Code','Fira Code',
         'Menlo','Consolas',monospace;
  --sans:-apple-system,'Segoe UI',system-ui,sans-serif;
}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);
  height:100vh;display:grid;
  grid-template-columns:240px 1fr;grid-template-rows:46px 1fr;
  overflow:hidden}
a{color:var(--accent);text-decoration:none}

/* ── header ── */
.topbar{grid-column:1/-1;background:var(--surface);border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;padding:0 20px;
  font-family:var(--mono);font-size:.82rem;letter-spacing:.04em}
.topbar h1{font-size:.82rem;font-weight:600;text-transform:uppercase;color:var(--fg2)}
.topbar .db-name{color:var(--muted);font-weight:400}

/* ── sidebar ── */
.sidebar{background:var(--surface);border-right:1px solid var(--border);
  overflow-y:auto;padding:16px 0;font-size:.8rem}
.sidebar h3{padding:0 16px;font-size:.65rem;text-transform:uppercase;
  letter-spacing:.08em;color:var(--muted);font-weight:600;margin-bottom:8px}
.tbl-item{padding:6px 16px;cursor:pointer;display:flex;align-items:center;gap:8px;
  transition:background .1s}
.tbl-item:hover{background:var(--raised)}
.tbl-item.active{background:var(--border);color:var(--accent)}
.tbl-name{font-family:var(--mono);font-size:.78rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tbl-rows{font-family:var(--mono);font-size:.65rem;color:var(--muted);margin-left:auto;white-space:nowrap}
.col-list{padding:4px 16px 12px 36px;font-family:var(--mono);font-size:.7rem;
  color:var(--fg2);line-height:1.7;display:none}
.col-list.open{display:block}
.col-type{color:var(--muted);margin-left:4px}

/* ── main ── */
.main{display:flex;flex-direction:column;overflow:hidden}

/* ── editor ── */
.editor-wrap{padding:16px 20px 0;flex-shrink:0}
.editor-area{position:relative}
textarea#sql{width:100%;height:120px;resize:vertical;background:var(--raised);
  color:var(--fg);border:1px solid var(--border);border-radius:6px;
  font-family:var(--mono);font-size:.82rem;line-height:1.5;
  padding:12px 14px;outline:none;tab-size:2}
textarea#sql:focus{border-color:var(--accent)}
.toolbar{display:flex;align-items:center;gap:10px;margin-top:10px}
.btn{background:var(--accent);color:var(--bg);border:none;border-radius:4px;
  padding:6px 16px;font-family:var(--mono);font-size:.75rem;font-weight:600;
  cursor:pointer;letter-spacing:.02em}
.btn:hover{opacity:.9}
.btn-ghost{background:transparent;color:var(--fg2);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--raised);color:var(--fg)}
.status{font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-left:auto}
.status .ok{color:var(--ok)}
.status .err{color:var(--err)}
.hint{font-size:.7rem;color:var(--muted);margin-left:8px}

/* ── presets ── */
.presets{display:flex;gap:6px;flex-wrap:wrap;padding:10px 20px 0;flex-shrink:0}
.preset{background:var(--surface);color:var(--fg2);border:1px solid var(--border);
  border-radius:4px;padding:4px 10px;font-family:var(--mono);font-size:.68rem;
  cursor:pointer;transition:all .12s}
.preset:hover{background:var(--raised);color:var(--fg);border-color:var(--border2)}

/* ── results ── */
.results-wrap{flex:1;overflow:auto;padding:16px 20px 20px;min-height:0}
.results-table{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:.75rem}
.results-table th{position:sticky;top:0;background:var(--surface);
  text-align:left;padding:8px 12px;font-weight:600;color:var(--accent2);
  border-bottom:2px solid var(--border);font-size:.7rem;text-transform:uppercase;
  letter-spacing:.04em;white-space:nowrap}
.results-table th.num{text-align:right}
.results-table td{padding:6px 12px;border-bottom:1px solid var(--border);
  white-space:nowrap;max-width:400px;overflow:hidden;text-overflow:ellipsis}
.results-table td.num{text-align:right;font-variant-numeric:tabular-nums}
.results-table tr:hover td{background:var(--raised)}
.results-table td.null{color:var(--muted);font-style:italic}
.empty-msg{color:var(--muted);font-size:.85rem;padding:40px 0;text-align:center}
.error-msg{color:var(--err);font-family:var(--mono);font-size:.82rem;
  padding:20px;background:var(--surface);border-radius:6px;
  border:1px solid var(--err);white-space:pre-wrap;line-height:1.5}
</style>
</head>
<body>

<div class="topbar">
  <h1>Usage Explorer</h1>
  <span class="db-name" id="db-name"></span>
  <span class="db-name" id="watch-indicator" style="color:var(--muted)"></span>
</div>

<div class="sidebar">
  <h3>Tables</h3>
  <div id="schema-list"></div>
</div>

<div class="main">
  <div class="editor-wrap">
    <div class="editor-area">
      <textarea id="sql" spellcheck="false" placeholder="SELECT ...">SELECT cli, count(*) AS sessions, sum(normalized_total) AS total_tokens
FROM session_usage
GROUP BY cli
ORDER BY total_tokens DESC</textarea>
    </div>
    <div class="toolbar">
      <button class="btn" id="run-btn" onclick="runQuery()">Run</button>
      <button class="btn btn-ghost" onclick="clearEditor()">Clear</button>
      <span class="hint">Ctrl+Enter to run</span>
      <span class="status" id="status"></span>
    </div>
  </div>
  <div class="presets" id="presets"></div>
  <div class="results-wrap"><div id="results"><div class="empty-msg">Run a query to see results</div></div></div>
</div>

<script>
const PRESETS = [
  ["Summary by CLI",
   "SELECT cli,\n       count(*) AS sessions,\n       sum(normalized_input) AS input_tokens,\n       sum(normalized_output) AS output_tokens,\n       sum(normalized_total) AS total_tokens\nFROM session_usage\nGROUP BY cli\nORDER BY total_tokens DESC"],
  ["Top 20 sessions",
   "SELECT session_id, cli, normalized_total\nFROM session_usage\nORDER BY normalized_total DESC\nLIMIT 20"],
  ["I/O ratio",
   "SELECT cli,\n       round(sum(normalized_input)*100.0 / nullif(sum(normalized_total),0), 1) AS input_pct,\n       round(sum(normalized_output)*100.0 / nullif(sum(normalized_total),0), 1) AS output_pct\nFROM session_usage\nGROUP BY cli"],
  ["Session size buckets",
   "SELECT cli,\n       count(*) FILTER (WHERE normalized_total = 0) AS zero,\n       count(*) FILTER (WHERE normalized_total BETWEEN 1 AND 10000) AS tiny,\n       count(*) FILTER (WHERE normalized_total BETWEEN 10001 AND 100000) AS small,\n       count(*) FILTER (WHERE normalized_total BETWEEN 100001 AND 1000000) AS medium,\n       count(*) FILTER (WHERE normalized_total > 1000000) AS large\nFROM session_usage\nGROUP BY cli"],
  ["Preflight records",
   "SELECT cli, count(*) AS records, count(DISTINCT session_id) AS sessions\nFROM preflight_valid\nGROUP BY cli"],
  ["Schema",
   "SELECT table_name, column_name, data_type\nFROM information_schema.columns\nWHERE table_schema = 'main'\nORDER BY table_name, ordinal_position"],
];

// Presets
const presetsEl = document.getElementById("presets");
PRESETS.forEach(([name, sql]) => {
  const btn = document.createElement("button");
  btn.className = "preset";
  btn.textContent = name;
  btn.onclick = () => { document.getElementById("sql").value = sql; runQuery(); };
  presetsEl.appendChild(btn);
});

// Keyboard
document.getElementById("sql").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runQuery(); }
  if (e.key === "Tab") {
    e.preventDefault();
    const ta = e.target;
    const start = ta.selectionStart;
    ta.value = ta.value.substring(0, start) + "  " + ta.value.substring(ta.selectionEnd);
    ta.selectionStart = ta.selectionEnd = start + 2;
  }
});

function isNumeric(v) {
  return typeof v === "number" || (typeof v === "string" && /^-?\d+(\.\d+)?$/.test(v));
}

function fmtNum(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === "number") {
    if (Number.isInteger(v)) return v.toLocaleString("en-US");
    return v.toLocaleString("en-US", {maximumFractionDigits: 4});
  }
  return v;
}

async function runQuery() {
  const sql = document.getElementById("sql").value.trim();
  if (!sql) return;
  const statusEl = document.getElementById("status");
  const resultsEl = document.getElementById("results");
  statusEl.innerHTML = "running...";
  try {
    const resp = await fetch("/query", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({sql})
    });
    const data = await resp.json();
    if (data.error) {
      resultsEl.innerHTML = '<div class="error-msg">' + escHtml(data.error) + "</div>";
      statusEl.innerHTML = '<span class="err">error</span>';
      return;
    }
    const {columns, rows, time_ms} = data;
    if (!rows.length) {
      resultsEl.innerHTML = '<div class="empty-msg">Query returned 0 rows</div>';
      statusEl.innerHTML = '<span class="ok">' + rows.length + " rows</span> · " + time_ms + "ms";
      return;
    }
    const numCols = new Set();
    columns.forEach((c, i) => { if (rows.length && isNumeric(rows[0][i])) numCols.add(i); });

    let html = '<table class="results-table"><thead><tr>';
    columns.forEach((c, i) => {
      html += "<th" + (numCols.has(i) ? ' class="num"' : "") + ">" + escHtml(c) + "</th>";
    });
    html += "</tr></thead><tbody>";
    const limit = Math.min(rows.length, 2000);
    for (let r = 0; r < limit; r++) {
      html += "<tr>";
      columns.forEach((_, i) => {
        const v = rows[r][i];
        if (v === null || v === undefined) {
          html += '<td class="null">null</td>';
        } else if (numCols.has(i)) {
          html += '<td class="num">' + fmtNum(v) + "</td>";
        } else {
          html += "<td>" + escHtml(String(v)) + "</td>";
        }
      });
      html += "</tr>";
    }
    html += "</tbody></table>";
    if (rows.length > limit) html += '<div class="empty-msg">Showing ' + limit + " of " + rows.length + " rows</div>";
    resultsEl.innerHTML = html;
    statusEl.innerHTML = '<span class="ok">' + rows.length + " rows</span> · " + time_ms + "ms";
  } catch (e) {
    resultsEl.innerHTML = '<div class="error-msg">' + escHtml(e.message) + "</div>";
    statusEl.innerHTML = '<span class="err">error</span>';
  }
}

function clearEditor() { document.getElementById("sql").value = ""; document.getElementById("results").innerHTML = '<div class="empty-msg">Run a query to see results</div>'; }

function escHtml(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// Schema
async function loadSchema() {
  const resp = await fetch("/schema");
  const data = await resp.json();
  document.getElementById("db-name").textContent = data.db_name;
  const list = document.getElementById("schema-list");
  list.innerHTML = "";
  data.tables.forEach(t => {
    const item = document.createElement("div");
    item.className = "tbl-item";
    item.innerHTML = '<span class="tbl-name">' + escHtml(t.name) + '</span><span class="tbl-rows">' + t.row_count.toLocaleString() + "</span>";
    const cols = document.createElement("div");
    cols.className = "col-list";
    cols.innerHTML = t.columns.map(c => escHtml(c.name) + '<span class="col-type">' + escHtml(c.type) + "</span>").join("<br>");
    item.onclick = () => {
      document.querySelectorAll(".tbl-item").forEach(el => el.classList.remove("active"));
      item.classList.toggle("active");
      cols.classList.toggle("open");
      document.getElementById("sql").value = "SELECT *\nFROM " + t.name + "\nLIMIT 100";
    };
    list.appendChild(item);
    list.appendChild(cols);
  });
}
loadSchema();
// Auto-run initial query
setTimeout(runQuery, 300);

// ── Live watch ──
let _knownVersion = 0;
async function pollVersion() {
  try {
    const resp = await fetch("/api/version");
    const data = await resp.json();
    const ind = document.getElementById("watch-indicator");
    if (data.version === 0) { ind.textContent = ""; return; }
    if (_knownVersion === 0) { _knownVersion = data.version; ind.textContent = "watching"; ind.style.color = "var(--ok)"; return; }
    if (data.version !== _knownVersion) {
      _knownVersion = data.version;
      ind.textContent = "refreshed (v" + data.version + ")";
      ind.style.color = "var(--warn)";
      await loadSchema();
      await runQuery();
      setTimeout(() => { ind.textContent = "watching"; ind.style.color = "var(--ok)"; }, 3000);
    }
  } catch(e) {}
}
setInterval(pollVersion, 5000);
setTimeout(pollVersion, 500);
</script>
</body>
</html>"""


def _send(handler, code, content_type, body):
    handler.send_response(code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class _EvidenceWatcher:
    """Polls the evidence spool and rebuilds the .duckdb file on change."""

    def __init__(self, usage_dir: Path, db_path: Path, interval: float = 5.0):
        self.usage_dir = usage_dir
        self.db_path = db_path
        self.interval = interval
        self.version = 1
        self._fingerprint = self._snapshot()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _snapshot(self) -> tuple:
        try:
            entries = []
            for f in sorted(self.usage_dir.iterdir()):
                if f.suffix == ".jsonl":
                    st = f.stat()
                    entries.append((f.name, st.st_size, st.st_mtime_ns))
            return tuple(entries)
        except OSError:
            return ()

    def _loop(self) -> None:
        while True:
            time.sleep(self.interval)
            current = self._snapshot()
            if current != self._fingerprint:
                self._fingerprint = current
                self._rebuild()

    def _rebuild(self) -> None:
        from usage import accounting, contract_check, input_snapshot, preflight
        from usage.persist import persist_to_duckdb

        paths, _digest = input_snapshot.snapshot(self.usage_dir)
        if not paths:
            return

        file_args = [str(p) for p in paths]
        if contract_check.main(file_args) != 0:
            print("[watch] contract check failed, skipping rebuild", file=sys.stderr)
            return

        result = preflight.run_preflight(paths)
        try:
            accounting.select_latest_snapshots(result.conn)
            accounting.build_session_roots(result.conn)
            accounting.build_session_contributions(result.conn)
            accounting.compute_session_usage(result.conn)

            persist_to_duckdb(result.conn, self.db_path)

            with self._lock:
                self.version += 1
            print(
                f"[watch] rebuilt ({self.version}) from {len(paths)} file(s)",
                file=sys.stderr,
            )
        # The watcher is a long-running boundary. A failed rebuild must not
        # terminate later rebuild attempts.
        except Exception as exc:  # noqa: BLE001
            print(f"[watch] rebuild failed: {exc}", file=sys.stderr)
        finally:
            result.conn.close()


def _make_handler(db_path, db_name, watcher=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *a):
            pass

        def _conn(self):
            return duckdb.connect(str(db_path), read_only=True)

        def do_GET(self):
            if self.path == "/":
                _send(self, 200, "text/html; charset=utf-8", _HTML.encode())
            elif self.path == "/api/version":
                v = watcher.version if watcher else 0
                payload = json.dumps({"version": v}).encode()
                _send(self, 200, "application/json", payload)
            elif self.path == "/schema":
                conn = self._conn()
                try:
                    tables = conn.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'main' ORDER BY table_name"
                    ).fetchall()
                    result = []
                    for (name,) in tables:
                        cols = conn.execute(
                            "SELECT column_name, data_type "
                            "FROM information_schema.columns "
                            "WHERE table_schema = 'main' AND table_name = ? "
                            "ORDER BY ordinal_position",
                            [name],
                        ).fetchall()
                        row_count = conn.execute(
                            f'SELECT count(*) FROM "{name}"'
                        ).fetchone()[0]
                        result.append(
                            {
                                "name": name,
                                "columns": [{"name": c[0], "type": c[1]} for c in cols],
                                "row_count": row_count,
                            }
                        )
                    payload = json.dumps(
                        {"db_name": db_name, "tables": result}
                    ).encode()
                    _send(self, 200, "application/json", payload)
                finally:
                    conn.close()
            else:
                _send(self, 404, "text/plain", b"not found")

        def do_POST(self):
            if self.path == "/query":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                sql = body.get("sql", "").strip()
                if not sql:
                    _send(
                        self,
                        400,
                        "application/json",
                        json.dumps({"error": "empty query"}).encode(),
                    )
                    return
                conn = self._conn()
                t0 = time.monotonic()
                try:
                    result = conn.execute(sql)
                    columns = (
                        [desc[0] for desc in result.description]
                        if result.description
                        else []
                    )
                    rows = result.fetchall() if columns else []
                    elapsed = round((time.monotonic() - t0) * 1000, 1)
                    payload = json.dumps(
                        {
                            "columns": columns,
                            "rows": [list(r) for r in rows],
                            "time_ms": elapsed,
                        },
                        default=str,
                    ).encode()
                    _send(self, 200, "application/json", payload)
                # The HTTP boundary returns DuckDB execution failures as a
                # structured response instead of terminating the server.
                except Exception as exc:  # noqa: BLE001
                    elapsed = round((time.monotonic() - t0) * 1000, 1)
                    payload = json.dumps(
                        {
                            "error": str(exc),
                            "time_ms": elapsed,
                        }
                    ).encode()
                    _send(self, 200, "application/json", payload)
                finally:
                    conn.close()
            else:
                _send(self, 404, "text/plain", b"not found")

    return Handler


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="usage-explore",
        description="Web-based SQL explorer for persistent usage DuckDB files.",
    )
    parser.add_argument("db", help="Path to the .duckdb file")
    parser.add_argument("port", nargs="?", type=int, default=8642)
    parser.add_argument(
        "--watch",
        metavar="DIR",
        default=None,
        help="Evidence spool directory to watch for live refresh",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"file not found: {db_path}", file=sys.stderr)
        sys.exit(2)

    port = args.port

    watcher = None
    if args.watch:
        watch_dir = Path(args.watch)
        if watch_dir.is_dir():
            watcher = _EvidenceWatcher(watch_dir, db_path)
            print(f"Watching: {watch_dir}", file=sys.stderr)
        else:
            print(f"watch directory not found: {watch_dir}", file=sys.stderr)
            sys.exit(2)

    db_name = db_path.name

    handler_cls = _make_handler(db_path, db_name, watcher=watcher)
    server = _ThreadingHTTPServer(("127.0.0.1", port), handler_cls)

    url = f"http://localhost:{port}"
    print(f"Usage Explorer: {url}", file=sys.stderr)
    print(f"Database: {db_path}", file=sys.stderr)
    print("Ctrl+C to stop", file=sys.stderr)

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", file=sys.stderr)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
