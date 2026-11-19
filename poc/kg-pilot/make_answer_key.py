# /// script
# requires-python = ">=3.11"
# ///
"""Recover the twenty run-lifecycle decisions from the session file, as the answer key.

The handoff on disk was overwritten; the session still holds the Write call that made it.

Run: uv run --script make_answer_key.py <path-to-session.jsonl>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MESSAGE = "ba9d6bda-9d76-4e2a-869b-de65384fe6de"
FILE = "handoff-run-lifecycle-decisions-2026-11-16.md"
ITEM = re.compile(r"^(\d+)\. ", re.M)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: make_answer_key.py <path-to-session.jsonl>")
    text = None
    for line in Path(sys.argv[1]).open(encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict) or record.get("uuid") != MESSAGE:
            continue
        for b in (record.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("name") == "Write" and str(b["input"].get("file_path", "")).endswith(FILE):
                text = b["input"]["content"]
    if text is None:
        sys.exit(f"no Write of {FILE} in message {MESSAGE}")
    starts = [m for m in ITEM.finditer(text)]
    decisions = []
    for m, nxt in zip(starts, starts[1:] + [None]):
        body = text[m.end(): nxt.start() if nxt else len(text)]
        # Decision 1 is followed by an inventory paragraph that is not a decision.
        body = body.split("\n\nInventory of the current process", 1)[0]
        decisions.append({"number": int(m.group(1)), "text": " ".join(body.split())})
    numbers = [d["number"] for d in decisions]
    if numbers != list(range(1, 21)):
        sys.exit(f"expected decisions 1 to 20, found {numbers}")
    key = {"source": {"message_uuid": MESSAGE, "file": f"docs/handoffs/{FILE}"}, "decisions": decisions}
    Path("answer-key.json").write_text(json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"answer-key.json: {len(decisions)} decisions from message {MESSAGE}")


if __name__ == "__main__":
    main()
