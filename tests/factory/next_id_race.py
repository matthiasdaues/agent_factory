"""next_id_race — run two next-id claims at the same moment, round after round.

The harness seeds a remote with `next-id --seed 1000`, makes two clones of
that remote, and runs one `next-id` call in each clone at the same moment. Odd
rounds claim `ST` twice. Even rounds claim `ST` and `FAGAN`, so both the same
prefix and two prefixes share the one counter ref. The round plan comes from
poc/counters/ref-claim-race.sh.

The run passes when every call exits 0, no ID appears twice, the `ST` and
`FAGAN` numbers run from 1001 without a gap, and the lines `ST` and `FAGAN` of
the counter equal the highest number printed.

Without `--remote`, the harness creates its own local bare repository and
deletes it at the end.

Usage
  uv run python tests/factory/next_id_race.py [--rounds <n>] [--remote <url>]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

NEXT_ID = (
    Path(__file__).resolve().parents[2] / "packages" / "factory" / "scripts" / "next-id"
)
COUNTER_REF = "refs/ids/counters"
SEED = 1000
USAGE_NOTE = (
    "A run with --remote seeds refs/ids/counters on that remote. So the remote\n"
    "must be a repository without a counter in use, such as a scratch\n"
    "repository. After the run, delete refs/ids/counters there:\n"
    "  git push <url> :refs/ids/counters"
)


@dataclass
class Call:
    round: int
    clone: str
    prefix: str
    code: int
    out: str
    err: str


@dataclass
class RaceResult:
    calls: list[Call] = field(default_factory=list)
    counter: dict[str, int] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def round_plan(round_number: int) -> tuple[str, str]:
    """Return the prefixes of clone a and clone b in this round."""
    return ("ST", "ST") if round_number % 2 else ("ST", "FAGAN")


def _git(args: list[str], env: dict[str, str]) -> str:
    return subprocess.run(
        ["git", *args], env=env, capture_output=True, text=True, check=True
    ).stdout.strip()


def _next_id(args: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(NEXT_ID), *args],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _read_counter(url: str, work: Path, env: dict[str, str]) -> dict[str, int]:
    reader = work / "reader.git"
    _git(["init", "--quiet", "--bare", str(reader)], env)
    _git(
        [
            "--git-dir",
            str(reader),
            "fetch",
            "--quiet",
            url,
            f"+{COUNTER_REF}:{COUNTER_REF}",
        ],
        env,
    )
    message = _git(
        ["--git-dir", str(reader), "show", "--no-patch", "--format=%B", COUNTER_REF],
        env,
    )
    lines = {}
    for line in message.splitlines():
        key, _, value = line.partition("=")
        if key != "token" and value.isdigit():
            lines[key] = int(value)
    return lines


def check(result: RaceResult) -> None:
    """Fill result.problems from the calls and the counter."""
    for call in result.calls:
        if call.code != 0:
            result.problems.append(
                f"round {call.round}, clone {call.clone}: {call.prefix} exited {call.code}: "
                f"{call.err.strip()}"
            )
    ids = [call.out.strip() for call in result.calls if call.code == 0]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        result.problems.append(f"IDs handed out twice: {', '.join(duplicates)}")
    for prefix in ("ST", "FAGAN"):
        numbers = sorted(
            int(i.split("-")[1]) for i in ids if i.startswith(f"{prefix}-")
        )
        expected = list(range(SEED + 1, SEED + 1 + len(numbers)))
        if numbers != expected:
            missing = sorted(set(expected) - set(numbers))
            result.problems.append(f"{prefix} numbers skipped: {missing}")
        if numbers and result.counter.get(prefix) != numbers[-1]:
            result.problems.append(
                f"the counter holds {prefix}={result.counter.get(prefix)}, "
                f"the highest {prefix} printed is {numbers[-1]}"
            )


def run_race(
    rounds: int, remote: str | None = None, env: dict[str, str] | None = None
) -> RaceResult:
    """Seed the remote, run the rounds, and check the IDs."""
    env = dict(os.environ if env is None else env)
    result = RaceResult()
    with tempfile.TemporaryDirectory(prefix="next-id-race-") as tmp:
        work = Path(tmp)
        url = remote
        if url is None:
            url = str(work / "remote.git")
            _git(["init", "--quiet", "--bare", url], env)
        seed = _next_id(["--seed", str(SEED), "--remote", url], work, env)
        _, err = seed.communicate()
        if seed.returncode != 0:
            result.problems.append(f"the seed failed: {err.strip()}")
            return result
        clones = {}
        for name in ("a", "b"):
            clones[name] = work / name
            _git(["clone", "--quiet", "--no-checkout", url, str(clones[name])], env)
        for number in range(1, rounds + 1):
            started = [
                (name, prefix, _next_id([prefix], clones[name], env))
                for name, prefix in zip(("a", "b"), round_plan(number), strict=True)
            ]
            for name, prefix, proc in started:
                out, err = proc.communicate()
                result.calls.append(
                    Call(number, name, prefix, proc.returncode, out, err)
                )
        result.counter = _read_counter(url, work, env)
    check(result)
    return result


def report(result: RaceResult) -> str:
    """Write the result as lines for a person."""
    lines = [
        f"Round {call.round}, clone {call.clone}: {call.prefix} -> "
        f"{call.out.strip() or 'nothing'} (exit {call.code})"
        for call in result.calls
    ]
    ok_calls = sum(call.code == 0 for call in result.calls)
    lines.append(f"Calls with exit 0: {ok_calls} of {len(result.calls)}")
    lines.append(
        "Counter: " + " ".join(f"{k}={v:04d}" for k, v in result.counter.items())
    )
    if result.ok:
        lines.append(
            "Result: OK, no ID was handed out twice and no number was skipped."
        )
    else:
        lines.extend(f"Problem: {problem}" for problem in result.problems)
        lines.append("Result: FAIL")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="next_id_race.py",
        description=__doc__.split("\n")[0],
        epilog=USAGE_NOTE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--rounds", type=int, default=20, help="the number of rounds; default 20"
    )
    parser.add_argument(
        "--remote",
        help="the remote URL; without it, a local bare repository is created",
    )
    ns = parser.parse_args(argv)
    result = run_race(ns.rounds, ns.remote)
    print(report(result))
    if ns.remote is not None:
        print(USAGE_NOTE)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
