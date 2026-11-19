"""The ledger fields of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Rule: Factory maintainer finds in the dispatch contract exactly the fields
the ledger holds.
"""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

import pytest
import yaml
from conftest import SOURCE_SCRIPTS_DIR, load_script

import dispatch_lib as lib

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
SHA = "a" * 40

OLD_LEDGER = f"""---
mode: automated
closed: false
invocation_branch: feature/login
branch_root: {SHA}
branch_head: {SHA}
stories:
  ST-0350:
    id: ST-0350
    wave: 1
    status: dispatched
    deps: []
    branch: story/ST-0350
    worktree: null
    feature_branch: feature/login
    base_sha: {SHA}
    tier: economy
    reason: null
    gate_results: {{}}
"""


def full_ledger() -> lib.Ledger:
    """A ledger in which every field the code can write holds a value."""
    ledger = lib.Ledger()
    ledger.mode = "by-hand"
    ledger.feature_branch = "feature/login"
    ledger.branch_root = SHA
    ledger.branch_head = SHA
    ledger.stories["ST-0350"] = lib.StoryEntry(
        id="ST-0350",
        wave=1,
        status=lib.StoryState.DONE,
        deps=["ST-0349"],
        branch="story/ST-0350",
        worktree="/tmp/w",
        feature_branch="feature/login",
        base_sha=SHA,
        tier="economy",
        reason="merged",
        attempts=[{"tier": "economy"}],
        escalation_granted=True,
        attempt_grants=[{"tier": "economy", "attempt_count": 1}],
        verify_base="pass",
        commit_sha=SHA,
        failure_class="acceptance_unmet",
        evidence="report.json",
        manifest_recoveries=[{"at": "now"}],
        active_session="impl",
        active_tier="economy",
    )
    ledger.waves.append(lib.WaveCloseout(number=1, branch_head=SHA))
    return ledger


def written(ledger: lib.Ledger, path: Path) -> dict:
    ledger.save(path)
    return yaml.safe_load(path.read_text())


@pytest.mark.spec("RL-17-CT-01")
@pytest.mark.parametrize("mode", lib.LEDGER_MODES)
def test_RL_17_CT_01_the_ledger_uses_the_names_of_the_run(tmp_path, mode):
    """Scenario: The ledger uses the run's names.
    Scenario: The ledger holds no field that no command reads."""
    ledger = full_ledger()
    ledger.mode = mode

    data = written(ledger, tmp_path / "dispatch-ledger.yaml")

    assert data["mode"] == mode
    assert data["feature_branch"] == "feature/login"
    assert "invocation_branch" not in data
    assert "closed" not in data
    assert all("gate_results" not in entry for entry in data["stories"].values())


@pytest.mark.spec("RL-17-CT-01")
def test_RL_17_CT_01_a_new_ledger_is_orchestrated():
    """dispatch init without --mode writes orchestrated (BR-111)."""
    assert lib.Ledger().mode == "orchestrated"
    assert lib.LEDGER_MODES == ("orchestrated", "by-hand")


@pytest.mark.spec("RL-17-CT-02")
def test_RL_17_CT_02_the_old_names_load_as_the_new_ones(tmp_path):
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(OLD_LEDGER)

    ledger = lib.Ledger.load(path)

    assert ledger.mode == "orchestrated"
    assert ledger.feature_branch == "feature/login"


@pytest.mark.spec("RL-17-CT-02")
def test_RL_17_CT_02_mark_blocked_writes_only_the_new_names(tmp_path):
    """Scenario: dispatch reads the old names of a ledger and writes only the new ones."""
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(OLD_LEDGER)

    result = subprocess.run(
        [str(DISPATCH), "--ledger", str(path), "mark-blocked", "ST-0350",
         "--reason", "design question"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(path.read_text())
    assert data["feature_branch"] == "feature/login"
    assert data["mode"] == "orchestrated"
    assert "invocation_branch" not in data
    assert "closed" not in data
    assert "gate_results" not in data["stories"]["ST-0350"]
    assert data["stories"]["ST-0350"]["status"] == "blocked"


# --- RL-05, RL-06, RL-03: the attempt cap of escalate and re-dispatch (ST-0418) ---

AU = "acceptance_unmet"


def attempt(failure_class: str = AU, tier: str = "standard") -> dict:
    return {
        "session": "impl",
        "tier": tier,
        "failure_class": failure_class,
        "evidence": None,
        "commit_sha": None,
        "normalized_total": 0,
    }


def failed_entry(story_id: str = "ST-0350", tier: str = "standard", classes=(), **fields):
    fields.setdefault("status", lib.StoryState.FAILED)
    return lib.StoryEntry(
        id=story_id,
        wave=1,
        branch=f"story/{story_id}",
        feature_branch="feature/login",
        base_sha=SHA,
        tier=tier,
        attempts=[attempt(c, tier) for c in classes],
        **fields,
    )


def seams_first_entry(active_tier: str = "economy", classes=(), **fields):
    """A seams-first story declared `standard`: `tier` is unset until `escalate`
    writes it, and the implementation session runs on *active_tier*."""
    entry = failed_entry(tier=None, active_session="impl", active_tier=active_tier,
                         **fields)
    entry.attempts = [attempt(c, active_tier) for c in classes]
    return entry


SEAMS_FIRST_STORY = """---
id: ST-0350
tier: standard
strategy: seams-first
---

# A seams-first story
"""


class Run:
    """A ledger in tmp_path and the dispatch script, called in this process.

    The checks of the branch are stubs: verify-base and the scope pass until
    a test sets `verify_base_fails` or `scope_violation`.
    """

    def __init__(self, tmp_path: Path, monkeypatch, capsys):
        self.root = tmp_path
        self.path = tmp_path / "dispatch-ledger.yaml"
        self.capsys = capsys
        self.verify_base_fails = False
        self.scope_violation = False
        self.dispatch = load_script("dispatch")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(self.dispatch, "_project_root", lambda: tmp_path)
        monkeypatch.setattr(self.dispatch, "_git", lambda *args: (1, "", "no git"))
        monkeypatch.setattr(
            self.dispatch, "_run_verify_base",
            lambda *args: (1, "verify-base: stale") if self.verify_base_fails else (0, ""),
        )
        monkeypatch.setattr(
            self.dispatch, "_story_scope_violation", lambda *args: self.scope_violation
        )

    def gates(self, **values) -> None:
        body = "".join(f"  {key}: {value}\n" for key, value in values.items())
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "docs" / "testing.yaml").write_text(f"gates:\n{body}")

    def write(self, *entries: lib.StoryEntry, mode: str = "orchestrated") -> None:
        ledger = lib.Ledger()
        ledger.mode = mode
        ledger.feature_branch = "feature/login"
        for entry in entries:
            ledger.stories[entry.id] = entry
        ledger.save(self.path)

    def entry(self, story_id: str = "ST-0350") -> lib.StoryEntry:
        return lib.Ledger.load(self.path).stories[story_id]

    def __call__(self, *argv: str) -> tuple[int, str, str]:
        self.capsys.readouterr()
        code = self.dispatch.main(["--ledger", str(self.path), *argv])
        out, err = self.capsys.readouterr()
        return code, out, err

    def limits(self) -> lib.AttemptLimits:
        return self.dispatch._read_attempt_limits(self.root)

    def gate_loop(self, story_id: str = "ST-0350") -> None:
        """Run the gate-check step of the implementation agent with a gate that always fails."""
        for _ in range(30):
            assert self("mark-dispatching", story_id)[0] == 0
            assert self("mark-dispatched", story_id)[0] == 0
            assert self("mark-failed", story_id, "--class", AU)[0] == 0
            if lib.has_stopped(self.entry(story_id), self.limits()):
                return
            if self("re-dispatch", story_id)[0] == 0:
                continue
            assert self("escalate", story_id)[0] == 0
            assert self("re-dispatch", story_id)[0] == 0
        raise AssertionError("the gate-check step did not stop")

    def tiers_of_attempts(self, story_id: str = "ST-0350") -> Counter:
        return Counter(a["tier"] for a in self.entry(story_id).attempts)


@pytest.fixture
def run(tmp_path, monkeypatch, capsys) -> Run:
    return Run(tmp_path, monkeypatch, capsys)


@pytest.mark.spec("RL-05-CT-01")
def test_RL_05_CT_01_escalate_refuses_before_the_attempts_on_the_tier_are_used(run):
    """Scenario: dispatch escalate refuses before the attempts on the tier are used."""
    run.gates(attempts=3)
    run.write(failed_entry(classes=[AU, AU]))

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "2 of 3 counted attempts on the tier standard" in err
    assert run.entry().tier == "standard"
    assert run.entry().escalation_granted is False


@pytest.mark.spec("RL-05-CT-01")
def test_RL_05_CT_01_escalate_grants_after_the_attempts_on_the_tier_are_used(run):
    """Scenario: dispatch escalate grants after the attempts on the tier are used."""
    run.gates(attempts=3)
    run.write(failed_entry(classes=[AU, "contradictory_evidence", AU]))

    code, out, err = run("escalate", "ST-0350")

    assert code == 0, err
    assert "standard -> strong" in out
    assert run.entry().tier == "strong"
    assert run.entry().escalation_granted is True


@pytest.mark.spec("RL-05-CT-01")
def test_RL_05_CT_01_an_attempt_of_another_failure_class_does_not_count(run):
    """Scenario: An attempt of another failure class does not count toward gates.attempts."""
    run.gates(attempts=3)
    run.write(failed_entry(classes=[AU, "spend_death", AU]))

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "2 of 3" in err
    entry = run.entry()
    assert entry.tier == "standard"
    assert lib.counted_attempts_on_tier(entry, "standard") == 2


@pytest.mark.spec("RL-05-CT-02")
@pytest.mark.parametrize(
    ("mode", "settings", "expected"),
    [
        ("orchestrated", {}, {"standard": 3, "strong": 3}),
        ("orchestrated", {"attempts_escalated": 0}, {"standard": 3}),
        ("orchestrated", {"attempts_escalated": 1}, {"standard": 3, "strong": 1}),
        ("by-hand", {"attempts": 2}, {"standard": 2, "strong": 3}),
    ],
    ids=["defaults", "escalation-off", "one-escalated", "by-hand-two-attempts"],
)
def test_RL_05_CT_02_a_failing_story_gets_the_attempts_of_each_tier_and_is_then_failed(
    run, mode, settings, expected
):
    """Scenario: With the defaults, a failing story gets three attempts on each tier and is then failed.
    Scenario: A value of 0 turns escalation off.
    Scenario: The same counts apply in a run by hand (`gates.attempts: 2`)."""
    if settings:
        run.gates(**settings)
    run.write(failed_entry(status=lib.StoryState.PREPARED), mode=mode)

    run.gate_loop()

    assert run.tiers_of_attempts() == Counter(expected)
    entry = run.entry()
    assert entry.status == lib.StoryState.FAILED
    assert lib.has_stopped(entry, run.limits())


@pytest.mark.spec("RL-05-CT-02")
def test_RL_05_CT_02_the_attempt_counts_default_to_three_and_keep_zero():
    assert lib.attempt_limits(None) == lib.AttemptLimits(3, 3)
    assert lib.attempt_limits({"crap-score": {"enabled": True}}) == lib.AttemptLimits(3, 3)
    assert lib.attempt_limits({"attempts_escalated": 0}) == lib.AttemptLimits(3, 0)
    for bad in ({"attempts": 0}, {"attempts": "3"}, {"attempts_escalated": -1},
                {"attempts_escalated": True}):
        with pytest.raises(ValueError, match="gates.attempts"):
            lib.attempt_limits(bad)


@pytest.mark.spec("RL-05-CT-02")
def test_RL_05_CT_02_escalate_refuses_an_unreadable_attempt_count(run):
    run.gates(attempts="many")
    run.write(failed_entry(classes=[AU, AU, AU]))

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "gates.attempts" in err
    assert run.entry().tier == "standard"


@pytest.mark.spec("RL-05-CT-03")
def test_RL_05_CT_03_a_story_on_strong_does_not_escalate_and_fails_after_its_attempts(run):
    """Scenario: A story on the tier strong does not escalate and fails after its attempts."""
    run.write(failed_entry(tier="strong", status=lib.StoryState.PREPARED))

    run.gate_loop()

    assert run.tiers_of_attempts() == Counter({"strong": 3})
    code, _, err = run("escalate", "ST-0350")
    assert code != 0
    assert "tier strong" in err
    entry = run.entry()
    assert entry.tier == "strong"
    assert entry.status == lib.StoryState.FAILED
    assert entry.escalation_granted is False


@pytest.mark.spec("RL-05-CT-03")
def test_RL_05_CT_03_escalate_refuses_a_second_escalation(run):
    entry = failed_entry(tier="standard", classes=[AU, AU, AU], escalation_granted=True)
    entry.attempts = [attempt(AU, "economy")] * 3 + entry.attempts
    run.write(entry)

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "already escalated" in err
    assert run.entry().tier == "standard"
    assert run.entry().reason is None


@pytest.mark.spec("RL-05-CT-04")
def test_RL_05_CT_04_two_stories_of_one_wave_both_escalate(run):
    """Scenario: Two stories of one wave both escalate."""
    run.write(
        failed_entry("ST-0350", classes=[AU, AU, AU]),
        failed_entry("ST-0351", tier="economy", classes=[AU, AU, AU]),
    )

    assert run("escalate", "ST-0350")[0] == 0
    code, _, err = run("escalate", "ST-0351")

    assert code == 0, err
    assert run.entry("ST-0350").tier == "strong"
    assert run.entry("ST-0351").tier == "standard"
    assert run.entry("ST-0351").status == lib.StoryState.FAILED


@pytest.mark.spec("RL-05-CT-05")
def test_RL_05_CT_05_escalate_refuses_when_attempts_escalated_is_0(run):
    """Scenario: dispatch escalate refuses when gates.attempts_escalated is 0."""
    run.gates(attempts=3, attempts_escalated=0)
    run.write(failed_entry(classes=[AU, AU, AU]))

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "gates.attempts_escalated is 0" in err
    assert run.entry().tier == "standard"
    assert run.entry().reason is None


@pytest.mark.spec("RL-05-CT-06")
def test_RL_05_CT_06_re_dispatch_refuses_when_the_attempts_on_the_tier_are_used_up(run):
    """Scenario: dispatch re-dispatch refuses when the attempts on the tier are used up.
    Scenario: After the User's fix, re-dispatch refuses a failed story that can still escalate."""
    run.gates(attempts=3, attempts_escalated=3)
    run.write(failed_entry(classes=[AU, AU, AU]))

    code, _, err = run("re-dispatch", "ST-0350")

    assert code != 0
    assert "ST-0350 requires escalation before re-dispatch" in err
    assert "dispatch escalate ST-0350" in err
    entry = run.entry()
    assert entry.status == lib.StoryState.FAILED
    assert entry.tier == "standard"
    assert entry.attempt_grants == []


@pytest.mark.spec("RL-05-CT-06")
def test_RL_05_CT_06_re_dispatch_refuses_two_contract_violation_attempts(run):
    run.write(failed_entry(classes=["contract_violation", AU, "contract_violation"]))

    code, _, err = run("re-dispatch", "ST-0350")

    assert code != 0
    assert "terminal after two contract_violation" in err
    assert run.entry().status == lib.StoryState.FAILED


@pytest.mark.spec("RL-05-CT-07")
@pytest.mark.parametrize("classes", [[AU, AU], [AU, "spend_death", AU]], ids=["two", "spend-death"])
def test_RL_05_CT_07_re_dispatch_keeps_the_tier_while_attempts_on_it_remain(run, classes):
    """Scenario: dispatch re-dispatch keeps the tier while attempts on it remain."""
    run.gates(attempts=3)
    run.write(failed_entry(classes=classes))

    code, out, err = run("re-dispatch", "ST-0350")

    assert code == 0, err
    entry = run.entry()
    assert entry.status == lib.StoryState.PREPARED
    assert entry.tier == "standard"
    assert entry.attempt_grants == []
    assert "new counted attempts" not in out


@pytest.mark.spec("RL-06-CT-02")
def test_RL_06_CT_02_re_dispatch_grants_new_attempts_after_both_tiers(run):
    """Scenario: After the User's fix, re-dispatch grants new attempts to a failed
    story whose attempts are used up."""
    entry = failed_entry(tier="strong", classes=[AU, AU, AU], escalation_granted=True)
    entry.attempts = [attempt(AU, "standard")] * 3 + entry.attempts
    run.write(entry)

    code, out, err = run("re-dispatch", "ST-0350")

    assert code == 0, err
    assert "ST-0350 gets 3 new counted attempts on the tier strong" in out
    entry = run.entry()
    assert entry.status == lib.StoryState.PREPARED
    assert entry.tier == "strong"
    assert entry.attempt_grants == [{"tier": "strong", "attempt_count": 6}]
    assert lib.counted_attempts_on_tier(entry, "strong") == 0


@pytest.mark.spec("RL-06-CT-02")
def test_RL_06_CT_02_re_dispatch_grants_new_attempts_when_escalation_is_off(run):
    """Scenario: After the User's fix, re-dispatch grants new attempts when escalation is off."""
    run.gates(attempts=3, attempts_escalated=0)
    run.write(failed_entry(classes=[AU, AU, AU]))

    code, _, err = run("re-dispatch", "ST-0350")

    assert code == 0, err
    entry = run.entry()
    assert entry.status == lib.StoryState.PREPARED
    assert entry.tier == "standard"
    assert entry.attempt_grants == [{"tier": "standard", "attempt_count": 3}]


@pytest.mark.spec("RL-06-CT-02")
def test_RL_06_CT_02_only_the_attempts_after_the_last_grant_count(run):
    """Gap: no Scenario uses up the attempts of a grant. The third failure after
    a grant leads to the next grant, and the list then holds two items."""
    run.write(failed_entry(tier="strong", status=lib.StoryState.PREPARED))
    run.gate_loop()
    assert run("re-dispatch", "ST-0350")[0] == 0
    assert run.entry().attempt_grants == [{"tier": "strong", "attempt_count": 3}]

    run.gate_loop()

    entry = run.entry()
    assert run.tiers_of_attempts() == Counter({"strong": 6})
    assert lib.has_stopped(entry, run.limits())
    assert run("re-dispatch", "ST-0350")[0] == 0
    assert run.entry().attempt_grants == [
        {"tier": "strong", "attempt_count": 3},
        {"tier": "strong", "attempt_count": 6},
    ]


@pytest.mark.spec("RL-06-CT-02")
def test_RL_06_CT_02_re_dispatch_checks_the_scope_again(run):
    """A refusal for the scope leads to a grant while the diff leaves the scope,
    and to a refusal that names escalate once the User moved it back (BR-116)."""
    run.write(failed_entry(classes=[AU, AU, AU], reason=lib.ESCALATE_REFUSED_SCOPE))
    run.scope_violation = False

    code, _, err = run("re-dispatch", "ST-0350")

    assert code != 0
    assert "dispatch escalate ST-0350" in err
    assert run.entry().reason == lib.ESCALATE_REFUSED_SCOPE

    run.scope_violation = True
    code, _, err = run("re-dispatch", "ST-0350")

    assert code == 0, err
    entry = run.entry()
    assert entry.status == lib.StoryState.PREPARED
    assert entry.reason is None
    assert entry.attempt_grants == [{"tier": "standard", "attempt_count": 3}]


@pytest.mark.spec("RL-03-CT-01")
@pytest.mark.parametrize(
    ("case", "entry", "limits", "stopped"),
    [
        ("first counted attempt on standard",
         failed_entry(classes=[AU]), lib.AttemptLimits(), False),
        ("last counted attempt on standard with an escalation left",
         failed_entry(classes=[AU, AU, AU]), lib.AttemptLimits(), False),
        ("last counted attempt on strong",
         failed_entry(tier="strong", classes=[AU, AU, AU]), lib.AttemptLimits(), True),
        ("used up after an escalation",
         failed_entry(tier="strong", classes=[AU, AU], escalation_granted=True),
         lib.AttemptLimits(3, 2), True),
        ("used up with escalation off",
         failed_entry(classes=[AU, AU, AU]), lib.AttemptLimits(3, 0), True),
        ("used up with a failing verify-base",
         failed_entry(classes=[AU, AU, AU], reason=lib.ESCALATE_REFUSED_VERIFY_BASE),
         lib.AttemptLimits(), True),
        ("used up with a diff outside the scope",
         failed_entry(classes=[AU, AU, AU], reason=lib.ESCALATE_REFUSED_SCOPE),
         lib.AttemptLimits(), True),
        ("an escalate record with attempts left",
         failed_entry(classes=[AU], reason=lib.ESCALATE_REFUSED_SCOPE),
         lib.AttemptLimits(), False),
        ("two contract_violation attempts",
         failed_entry(classes=["contract_violation", "contract_violation"]),
         lib.AttemptLimits(), True),
        ("an attempt of another class on strong",
         failed_entry(tier="strong", classes=["spend_death"] * 4), lib.AttemptLimits(), False),
        ("last counted attempt of a seams-first session with an escalation left",
         seams_first_entry(classes=[AU, AU, AU]), lib.AttemptLimits(), False),
        ("seams-first session used up after an escalation",
         seams_first_entry(active_tier="standard", classes=[AU, AU, AU],
                           escalation_granted=True),
         lib.AttemptLimits(), True),
        ("blocked", failed_entry(status=lib.StoryState.BLOCKED), lib.AttemptLimits(), True),
        ("dispatched", failed_entry(status=lib.StoryState.DISPATCHED, classes=[AU] * 3,
                                    tier="strong"), lib.AttemptLimits(), False),
    ],
    ids=lambda value: value.replace(" ", "-") if isinstance(value, str) else None,
)
def test_RL_03_CT_01_has_stopped(case, entry, limits, stopped):
    """Scenario: A failed attempt with a retry left is no decision point."""
    assert lib.has_stopped(entry, limits) is stopped


@pytest.mark.spec("RL-03-CT-01")
def test_RL_03_CT_01_mark_failed_says_a_retry_is_left(run):
    """Scenario: A failed attempt with a retry left is no decision point."""
    run.gates(attempts=3)
    run.write(failed_entry(status=lib.StoryState.DISPATCHED))

    code, out, err = run("mark-failed", "ST-0350", "--class", AU)

    assert code == 0, err
    assert "ST-0350 has a retry left (1 of 3 counted attempts on the tier standard)" in out
    assert "dispatch re-dispatch ST-0350" in out
    entry = run.entry()
    assert entry.status == lib.StoryState.FAILED
    assert entry.attempts[-1]["failure_class"] == AU
    assert entry.attempts[-1]["tier"] == "standard"
    assert not lib.has_stopped(entry, run.limits())


@pytest.mark.spec("RL-03-CT-01")
def test_RL_03_CT_01_mark_failed_names_escalate_after_the_last_attempt_on_the_tier(run):
    """After the third counted attempt on a tier that can still escalate, the
    next step is `dispatch escalate`, not a retry (BR-115, BR-116)."""
    run.write(failed_entry(status=lib.StoryState.DISPATCHED, classes=[AU, AU]))

    code, out, err = run("mark-failed", "ST-0350", "--class", AU)

    assert code == 0, err
    assert "has a retry left" not in out
    assert "ST-0350 has used up its 3 of 3 counted attempts on the tier standard" in out
    assert "dispatch escalate ST-0350" in out
    assert not lib.has_stopped(run.entry(), run.limits())


def write_seams_first_story(run: Run) -> None:
    (run.root / "backlog").mkdir(exist_ok=True)
    (run.root / "backlog" / "ST-0350.md").write_text(SEAMS_FIRST_STORY)


@pytest.mark.spec("RL-05-CT-01")
def test_RL_05_CT_01_a_seams_first_session_counts_its_attempts_on_its_own_tier(run):
    """mark-failed records an attempt on the tier that dispatch counts: a
    seams-first implementation session declared `standard` runs on `economy`,
    and its third counted attempt there names escalate (IMPL-0030)."""
    write_seams_first_story(run)
    run.write(seams_first_entry(status=lib.StoryState.DISPATCHED, classes=[AU, AU]))

    code, out, err = run("mark-failed", "ST-0350", "--class", AU)

    assert code == 0, err
    entry = run.entry()
    assert entry.attempts[-1]["tier"] == "economy"
    assert lib.counted_tier(entry, "standard") == "economy"
    assert lib.counted_attempts_on_tier(entry, "economy") == 3
    assert "3 of 3 counted attempts on the tier economy" in out
    assert "dispatch escalate ST-0350" in out
    assert not lib.has_stopped(entry, run.limits())

    code, _, err = run("re-dispatch", "ST-0350")
    assert code != 0
    assert "dispatch escalate ST-0350" in err

    code, out, err = run("escalate", "ST-0350")
    assert code == 0, err
    assert "economy -> standard" in out
    entry = run.entry()
    assert entry.tier == "standard"
    assert entry.active_tier == "standard"


@pytest.mark.spec("RL-05-CT-02")
def test_RL_05_CT_02_the_gate_loop_of_a_seams_first_story_stops(run):
    """A seams-first story gets the attempts of each tier and then stops, as
    any other story does (BR-114, BR-116, IMPL-0030)."""
    write_seams_first_story(run)
    run.write(seams_first_entry(status=lib.StoryState.PREPARED))

    run.gate_loop()

    assert run.tiers_of_attempts() == Counter({"economy": 3, "standard": 3})
    entry = run.entry()
    assert entry.status == lib.StoryState.FAILED
    assert lib.has_stopped(entry, run.limits())


@pytest.mark.spec("RL-03-CT-01")
@pytest.mark.parametrize(
    ("field", "record"),
    [("verify_base_fails", lib.ESCALATE_REFUSED_VERIFY_BASE),
     ("scope_violation", lib.ESCALATE_REFUSED_SCOPE)],
)
def test_RL_03_CT_01_escalate_records_a_refusal_of_the_branch(run, field, record):
    """escalate writes the record that HasStopped reads, and a later grant clears it (BR-115)."""
    run.write(failed_entry(classes=[AU, AU, AU]))
    setattr(run, field, True)

    code, _, err = run("escalate", "ST-0350")

    assert code != 0
    assert "has stopped and waits for the User" in err
    entry = run.entry()
    assert entry.reason == record
    assert entry.tier == "standard"
    assert lib.has_stopped(entry, run.limits())

    setattr(run, field, False)
    assert run("escalate", "ST-0350")[0] == 0
    entry = run.entry()
    assert entry.reason is None
    assert entry.tier == "strong"
    assert not lib.has_stopped(entry, run.limits())


@pytest.mark.spec("RL-02-CT-01")
def test_RL_02_CT_01_dispatch_has_no_mark_done_subcommand(tmp_path):
    """Scenario: dispatch has no mark-done subcommand (BR-118)."""
    ledger = tmp_path / "dispatch-ledger.yaml"
    ledger.write_text(OLD_LEDGER)

    result = subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), "mark-done", "ST-0350"],
        capture_output=True, text=True, check=False,
    )
    usage = subprocess.run(
        [str(DISPATCH), "--help"], capture_output=True, text=True, check=False,
    )

    assert result.returncode != 0
    assert "invalid choice: 'mark-done'" in result.stderr
    assert usage.returncode == 0
    assert "mark-done" not in usage.stdout
    assert "mark-done" not in lib.STOP_SUBCOMMANDS | lib.READ_SUBCOMMANDS
    assert yaml.safe_load(ledger.read_text())["stories"]["ST-0350"]["status"] == "dispatched"
