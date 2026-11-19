# /// script
# requires-python = ">=3.11"
# ///
"""Extract decisions from a spans file with a local model through Ollama.

The spans go to the model in windows of whole spans; each window gets the same prompt.

Run: uv run --script extract_local.py [spans.jsonl] [model]   (defaults out/spans-2026-11-15.jsonl, qwen3:8b)
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

OLLAMA = "http://127.0.0.1:11434"
WINDOW = 10_000  # characters of span text per call
SCHEMA = {
    "type": "object",
    "properties": {"decisions": {"type": "array", "items": {
        "type": "object",
        "properties": {"statement": {"type": "string"}, "quote": {"type": "string"}, "span_id": {"type": "string"}},
        "required": ["statement", "quote", "span_id"]}}},
    "required": ["decisions"],
}


def call(path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(OLLAMA + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3600) as r:
        return json.loads(r.read())


def windows(spans: list[dict]) -> list[list[dict]]:
    out, current, size = [], [], 0
    for s in spans:
        if current and size + len(s["text"]) > WINDOW:
            out.append(current)
            current, size = [], 0
        current.append(s)
        size += len(s["text"])
    return out + ([current] if current else [])


def main() -> None:
    spans_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/spans-2026-11-15.jsonl")
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen3:8b"
    prompt = Path("extract-prompt.md").read_text(encoding="utf-8")
    spans = [json.loads(line) for line in spans_path.open(encoding="utf-8")]
    digest = next((m["digest"] for m in call("/api/tags")["models"] if m["name"] == model), None)
    started, decisions, calls = time.time(), [], []
    for n, w in enumerate(windows(spans), 1):
        text = "\n\n".join(f"[{s['span_id']}] {s['timestamp']} {s['role']}:\n{s['text']}" for s in w)
        t0 = time.time()
        reply = call("/api/chat", {
            "model": model, "stream": False, "think": False, "format": SCHEMA,
            "options": {"temperature": 0, "seed": 1, "num_ctx": 8192},
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}]})
        try:
            found = json.loads(reply["message"]["content"])["decisions"]
        except (KeyError, json.JSONDecodeError):
            found = []
        decisions += found
        calls.append({"window": n, "spans": [w[0]["span_id"], w[-1]["span_id"]], "found": len(found),
                      "seconds": round(time.time() - t0, 1), "prompt_tokens": reply.get("prompt_eval_count"),
                      "output_tokens": reply.get("eval_count")})
        print(f"window {n}: {w[0]['span_id']}..{w[-1]['span_id']}, {len(found)} decisions, {calls[-1]['seconds']}s", flush=True)
    result = {"extractor": f"ollama {model}", "model_digest": digest, "spans_file": str(spans_path),
              "seconds": round(time.time() - started, 1), "calls": calls, "decisions": decisions}
    Path("out/extraction-local.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"out/extraction-local.json: {len(decisions)} decisions in {result['seconds']}s")


if __name__ == "__main__":
    main()
