"""The ledger fields of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Rule: Contributor finds in the dispatch contract exactly the fields
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
        returned=True,
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


@pytest.mark.spec("RL-05-CT-08")
def test_RL_05_CT_08_mark_failed_without_a_class_writes_no_attempt(run):
    """ST-0431: an attempt without a failure class counts against no limit,
    so mark-failed requires --class and leaves the ledger as it was."""
    run.write(failed_entry(status=lib.StoryState.DISPATCHED))
    before = run.path.read_bytes()
    run.capsys.readouterr()

    with pytest.raises(SystemExit) as refused:
        run.dispatch.main(["--ledger", str(run.path), "mark-failed", "ST-0350"])

    assert refused.value.code != 0
    assert "--class" in run.capsys.readouterr().err
    assert run.path.read_bytes() == before


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


# --- RL-06: the User returns a stopped story to the backlog (ST-0419) ---------

S = lib.StoryState
# The edges of state-machines.md § Ledger Entry Lifecycle. Added is the
# self-edge of PENDING, which Ledger.transition accepts without an entry here.
LIFECYCLE_EDGES = {
    S.PENDING: {S.PREPARED, S.BLOCKED},
    S.PREPARED: {S.DISPATCHING, S.BLOCKED},
    S.DISPATCHING: {S.DISPATCHED, S.FAILED, S.BLOCKED},
    S.DISPATCHED: {S.DONE, S.FAILED, S.BLOCKED},
    S.DONE: set(),
    S.FAILED: {S.PREPARED, S.PENDING},
    # ResumeGates adds the edge from blocked to dispatched (ST-0444, BR-135).
    S.BLOCKED: {S.PREPARED, S.DISPATCHED, S.PENDING},
}
RETURNED_STORY = """---
id: ST-0350
tier: standard
status: {status}
---

# ST-0350
"""


@pytest.mark.spec("RL-06-CT-01")
def test_RL_06_CT_01_the_transitions_are_the_edges_of_the_lifecycle():
    """Scenario Outline: return-story sets a stopped story back to pending.

    Return adds the edges from failed and blocked to pending, and no state."""
    assert lib.VALID_TRANSITIONS == LIFECYCLE_EDGES
    assert set(lib.StoryState) == set(LIFECYCLE_EDGES)


@pytest.mark.spec("RL-06-CT-01")
@pytest.mark.parametrize("state", list(lib.StoryState), ids=lambda s: s.value)
def test_RL_06_CT_01_return_story_reaches_pending_only_from_failed_and_blocked(
    run, state
):
    """Scenario Outline: return-story sets a stopped story back to pending."""
    story = run.root / "backlog" / "ST-0350.md"
    story.parent.mkdir()
    story.write_text(RETURNED_STORY.format(status="open"))
    run.write(failed_entry(status=state, classes=(AU,)))
    returns = state in {S.FAILED, S.BLOCKED}

    code, out, err = run("return-story", "ST-0350")

    entry = run.entry()
    if returns:
        assert code == 0, err
        assert (entry.status, entry.returned) == (S.PENDING, True)
        assert story.read_text() == RETURNED_STORY.format(status="pending")
        assert "ST-0350" in out
    else:
        assert code == 1
        assert (entry.status, entry.returned) == (state, False)
        assert story.read_text() == RETURNED_STORY.format(status="open")
        assert f"ST-0350 is {state.value}" in err
        assert "failed or blocked" in err


@pytest.mark.spec("RL-06-CT-01")
def test_RL_06_CT_01_return_story_refuses_a_story_without_a_backlog_file(run):
    """The return changes the ledger only together with the backlog file."""
    run.write(failed_entry(classes=(AU,)))

    code, _, err = run("return-story", "ST-0350")

    assert code == 1
    assert "backlog/ST-0350.md" in err
    assert (run.entry().status, run.entry().returned) == (S.FAILED, False)


@pytest.mark.spec("RL-06-CT-01")
def test_RL_06_CT_01_returned_is_written_only_when_true(tmp_path):
    """The field `returned` appears in the ledger once it holds a value."""
    ledger = lib.Ledger()
    ledger.stories["ST-0350"] = failed_entry()

    assert "returned" not in written(ledger, tmp_path / "a.yaml")["stories"]["ST-0350"]
    ledger.stories["ST-0350"].returned = True
    data = written(ledger, tmp_path / "b.yaml")
    assert data["stories"]["ST-0350"]["returned"] is True
    assert lib.Ledger.load(tmp_path / "b.yaml").stories["ST-0350"].returned is True


@pytest.mark.spec("RL-06-CT-01")
@pytest.mark.parametrize("record", sorted(lib.ESCALATE_REFUSED_RECORDS))
def test_RL_06_CT_01_the_stdlib_writer_keeps_a_record_with_a_colon_valid(
    tmp_path, monkeypatch, record
):
    """dispatch runs without PyYAML, so its own writer must write YAML that
    PyYAML reads: the record of an escalate refusal holds ": "."""
    ledger = lib.Ledger()
    ledger.stories["ST-0350"] = failed_entry(reason=record, returned=True)
    monkeypatch.setattr(lib, "yaml", None)
    path = tmp_path / "dispatch-ledger.yaml"

    ledger.save(path)

    assert yaml.safe_load(path.read_text())["stories"]["ST-0350"]["reason"] == record
    assert lib.Ledger.load(path).stories["ST-0350"].reason == record


# --- RL-07: a returned story holds back the stories behind it (ST-0420) ------


def pending_entry(story_id: str, wave: int, *deps: str, **fields) -> lib.StoryEntry:
    fields.setdefault("status", S.PENDING)
    return lib.StoryEntry(
        id=story_id, wave=wave, deps=list(deps), feature_branch="feature/login",
        **fields,
    )


def returned_chain() -> list[lib.StoryEntry]:
    """The Demo Data of ST-0420: ST-0350 is returned, ST-0351 and ST-0352 wait
    on it, ST-0353 depends on none of them, and ST-0354 closes a diamond."""
    return [
        pending_entry("ST-0350", 1, returned=True),
        pending_entry("ST-0353", 1),
        pending_entry("ST-0351", 2, "ST-0350"),
        pending_entry("ST-0352", 3, "ST-0351"),
        pending_entry("ST-0354", 3, "ST-0353", "ST-0351"),
    ]


@pytest.fixture
def started(run, monkeypatch) -> list[str]:
    """Stub the branch and worktree of a started story; list the started ids."""
    ids: list[str] = []
    dispatch = run.dispatch

    def create(branch, worktree, base):
        ids.append(branch.removeprefix("story/"))
        return dispatch._StoryWorkspace(True, True, "")

    # prepare-wave reads the tip of the feature branch as the base (ST-0431).
    git = dispatch._git
    monkeypatch.setattr(
        dispatch, "_git",
        lambda *args: (0, SHA, "") if args[:1] == ("rev-parse",) else git(*args),
    )
    monkeypatch.setattr(dispatch, "_main_worktree_root", lambda: run.root)
    monkeypatch.setattr(dispatch, "_create_story_workspace", create)
    monkeypatch.setattr(dispatch, "_verify_worktree_registration", lambda path: True)
    monkeypatch.setattr(dispatch, "_write_story_manifest", lambda *args: (0, ""))
    return ids


def write_run(run: Run, entries: list[lib.StoryEntry], *, record: bool = False) -> None:
    ledger = lib.Ledger()
    ledger.feature_branch = "feature/login"
    ledger.branch_root = SHA
    ledger.branch_head = SHA
    for entry in entries:
        ledger.stories[entry.id] = entry
    if record:
        ledger.waves.append(lib.WaveCloseout(number=1, branch_head=SHA))
    ledger.save(run.path)


@pytest.mark.spec("RL-07-CT-01")
def test_RL_07_CT_01_a_returned_story_holds_back_the_chain_behind_it(run, started):
    """Scenario: A returned story holds back the chain behind it."""
    write_run(run, returned_chain())

    wave_one = run("prepare-wave", "1")
    merged = lib.Ledger.load(run.path)
    merged.stories["ST-0353"].status = S.DONE
    # The held-back entries let waves 1 and 2 close (BR-113, ST-0421).
    merged.waves += [lib.WaveCloseout(number=n, branch_head=SHA) for n in (1, 2)]
    merged.save(run.path)
    wave_two = run("prepare-wave", "2")
    direct = run("prepare-story", "ST-0351")
    chain = run("prepare-story", "ST-0352")
    diamond = run("prepare-story", "ST-0354")

    assert started == ["ST-0353"]
    assert wave_two[0] == 0, wave_two[2]
    assert "ST-0351 depends on ST-0350" in wave_two[1] + wave_two[2]
    assert "returned" in wave_two[1] + wave_two[2]
    for code, _, err in (direct, chain, diamond):
        assert code == 1
        assert "a dependency inside the run is not done" in err
        assert "returned ST-0350" in err or "ST-0350, which is pending and returned" in err
    assert "ST-0352 depends on ST-0351" in chain[2]
    assert "ST-0354 depends on ST-0351" in diamond[2]
    for story_id in ("ST-0350", "ST-0351", "ST-0352", "ST-0354"):
        assert run.entry(story_id).status == S.PENDING
    assert wave_one[0] == 1


@pytest.mark.spec("RL-07-CT-01")
def test_RL_07_CT_01_the_dependency_check_reads_only_the_ledger():
    """BR-113: the check names each returned story behind a dependency,
    directly or through another story, and nothing for a free story."""
    ledger = lib.Ledger()
    for entry in returned_chain():
        ledger.stories[entry.id] = entry

    assert lib.returned_dependencies(ledger, "ST-0352") == ["ST-0350"]
    assert lib.returned_dependencies(ledger, "ST-0354") == ["ST-0350"]
    assert lib.returned_dependencies(ledger, "ST-0353") == []
    assert lib.dependency_refusals(ledger, ledger.stories["ST-0353"]) == []
    assert lib.dependency_refusals(ledger, ledger.stories["ST-0352"]) == [
        "ST-0352 depends on ST-0351, which is pending and waits on the returned ST-0350"
    ]
    assert lib.held_back(ledger, ledger.stories["ST-0352"])
    assert not lib.held_back(ledger, ledger.stories["ST-0353"])


@pytest.mark.spec("RL-07-CT-02")
def test_RL_07_CT_02_every_dependency_inside_the_run_is_checked(run, started):
    """Scenario: Every dependency inside the run is checked."""
    write_run(run, [
        pending_entry("ST-0350", 1, status=S.DONE, commit_sha=SHA),
        pending_entry("ST-0351", 1, status=S.DISPATCHED),
        pending_entry("ST-0352", 2, "ST-0350", "ST-0351"),
    ])

    code, _, err = run("prepare-story", "ST-0352")

    assert code == 1
    assert "ST-0352 depends on ST-0351, which is dispatched" in err
    assert "ST-0350" not in err.replace("ST-0352", "")
    assert started == []
    assert run.entry("ST-0352").status == S.PENDING


@pytest.mark.spec("RL-07-CT-03")
@pytest.mark.parametrize("mode", lib.LEDGER_MODES)
def test_RL_07_CT_03_prepare_story_refuses_a_returned_story_and_names_the_return(
    run, started, mode
):
    """Scenario: prepare-story refuses a returned story and names the return."""
    write_run(run, [pending_entry("ST-0351", 1, returned=True)], record=True)
    lib_ledger = lib.Ledger.load(run.path)
    lib_ledger.mode = mode
    lib_ledger.save(run.path)

    code, _, err = run("prepare-story", "ST-0351")

    assert code == 1
    assert "ST-0351 was returned and waits for the end of the run" in err
    assert started == []
    assert (run.entry("ST-0351").status, run.entry("ST-0351").returned) == (
        S.PENDING, True,
    )


@pytest.mark.spec("RL-07-CT-03")
def test_RL_07_CT_03_prepare_story_names_the_return_of_a_seams_first_story(run, started):
    """IMPL-0037: an orchestrated prepare-story of a returned seams-first story
    names the return, not the seam session."""
    (run.root / "backlog").mkdir(exist_ok=True)
    (run.root / "backlog" / "ST-0351.md").write_text(
        SEAMS_FIRST_STORY.replace("ST-0350", "ST-0351")
    )
    write_run(run, [pending_entry("ST-0351", 1, returned=True)], record=True)

    code, _, err = run("prepare-story", "ST-0351")

    assert code == 1
    assert "ST-0351 was returned and waits for the end of the run" in err
    assert "seam session" not in err
    assert started == []
    assert (run.entry("ST-0351").status, run.entry("ST-0351").returned) == (
        S.PENDING, True,
    )


@pytest.mark.spec("RL-07-CT-03")
def test_RL_07_CT_03_prepare_wave_refuses_a_returned_story_and_starts_the_others(
    run, started
):
    """prepare-wave names the return, exits non-zero, and still starts the
    stories of the wave that wait on nothing, also after the wave record."""
    write_run(run, [
        pending_entry("ST-0351", 1, returned=True),
        pending_entry("ST-0353", 1),
    ], record=True)

    code, _, err = run("prepare-wave", "1")

    assert code == 1
    assert "ST-0351 was returned and waits for the end of the run" in err
    assert started == ["ST-0353"]
    assert run.entry("ST-0351").status == S.PENDING
    assert run.entry("ST-0353").status == S.PREPARED


# --- RL-11-CT: the five states that let a wave close (ST-0421) ---------------


def wave_one(state_of_st_0351: lib.StoryEntry, *more: lib.StoryEntry) -> lib.Ledger:
    """Wave 1 holds the done ST-0350 and *state_of_st_0351*."""
    ledger = lib.Ledger()
    ledger.feature_branch = "feature/login"
    ledger.stories["ST-0350"] = pending_entry(
        "ST-0350", 1, status=S.DONE, commit_sha=SHA
    )
    for entry in (state_of_st_0351, *more):
        ledger.stories[entry.id] = entry
    return ledger


def st_0351(**fields) -> lib.StoryEntry:
    fields.setdefault("status", S.PENDING)
    return lib.StoryEntry(
        id="ST-0351", wave=1, feature_branch="feature/login",
        deps=fields.pop("deps", []), **fields,
    )


KEEPS_THE_WAVE_OPEN = {
    "dispatched": st_0351(status=S.DISPATCHED),
    "failed after its first counted attempt": st_0351(
        status=S.FAILED, tier="standard", attempts=[attempt(AU)]
    ),
    "pending without a returned dependency": st_0351(),
    "prepared": st_0351(status=S.PREPARED),
    "dispatching": st_0351(status=S.DISPATCHING),
    "failed without an attempt": st_0351(status=S.FAILED, tier="standard"),
}

LETS_THE_WAVE_CLOSE = {
    "done": st_0351(status=S.DONE, commit_sha=SHA),
    "blocked": st_0351(status=S.BLOCKED, reason="red suite"),
    "failed and stopped": st_0351(
        status=S.FAILED, tier="strong", attempts=[attempt(AU, "strong")] * 3
    ),
    "failed after two contract_violation attempts": st_0351(
        status=S.FAILED, tier="standard",
        attempts=[attempt("contract_violation")] * 2,
    ),
    "pending after a return": st_0351(returned=True),
}


@pytest.mark.spec("RL-11-CT-01")
@pytest.mark.parametrize("state", list(KEEPS_THE_WAVE_OPEN), ids=lambda s: s.replace(" ", "-"))
def test_RL_11_CT_01_close_wave_refuses_while_a_unit_of_work_can_still_go_on(state):
    """Scenario Outline: close-wave refuses while a unit of work of the wave can still go on."""
    ledger = wave_one(KEEPS_THE_WAVE_OPEN[state])

    with pytest.raises(lib.TransitionError) as refusal:
        ledger.close_wave(1, SHA, limits=lib.AttemptLimits(3, 3))

    assert "ST-0351" in str(refusal.value)
    assert "ST-0350" not in str(refusal.value)
    assert ledger.waves == []


@pytest.mark.spec("RL-11-CT-01")
@pytest.mark.parametrize("state", list(LETS_THE_WAVE_CLOSE), ids=lambda s: s.replace(" ", "-"))
def test_RL_11_CT_01_close_wave_accepts_each_state_that_lets_the_wave_close(state):
    """A unit of work lets its wave close when it is done, blocked, failed and
    stopped, or pending after a return (BR-062, BR-113)."""
    ledger = wave_one(LETS_THE_WAVE_CLOSE[state])

    _record, created = ledger.close_wave(1, SHA, limits=lib.AttemptLimits(3, 3))

    assert created
    assert [record.number for record in ledger.waves] == [1]
    assert ledger.stories["ST-0351"].status == LETS_THE_WAVE_CLOSE[state].status


@pytest.mark.spec("RL-11-CT-01")
def test_RL_11_CT_01_the_refusal_names_every_open_unit_of_work_with_its_state():
    ledger = wave_one(
        st_0351(status=S.DISPATCHED),
        lib.StoryEntry(id="ST-0352", wave=1, status=S.FAILED, tier="standard",
                       attempts=[attempt(AU)]),
    )

    with pytest.raises(lib.TransitionError) as refusal:
        ledger.close_wave(1, SHA, limits=lib.AttemptLimits(3, 3))

    assert "ST-0351 (dispatched)" in str(refusal.value)
    assert "ST-0352 (failed with a retry left)" in str(refusal.value)


@pytest.mark.spec("RL-11-CT-01")
def test_RL_11_CT_01_close_wave_records_a_wave_without_entries():
    """ST-0431: a wave whose only entry add moved to a later wave holds no
    unit of work that can go on, so close-wave records it with empty lists."""
    ledger = lib.Ledger()
    ledger.feature_branch = "feature/login"
    ledger.stories["ST-0350"] = pending_entry("ST-0350", 1, status=S.DONE, commit_sha=SHA)
    ledger.stories["BUG-0090"] = pending_entry("BUG-0090", 3)
    ledger.waves.append(lib.WaveCloseout(number=1, branch_head=SHA))

    record, created = ledger.close_wave(2, "b" * 40, limits=lib.AttemptLimits(3, 3))

    assert created
    assert (record.number, record.completed, record.blocked, record.failed) == (2, [], [], [])
    assert record.next_ready == ["BUG-0090"]
    assert [r.number for r in ledger.waves] == [1, 2]
    assert ledger.branch_head == "b" * 40


@pytest.mark.spec("RL-11-CT-02")
def test_RL_11_CT_02_a_wave_closes_while_its_stories_wait_on_a_returned_dependency():
    """Scenario: A wave closes while its stories wait on a returned dependency."""
    ledger = lib.Ledger()
    ledger.feature_branch = "feature/login"
    for entry in (
        pending_entry("ST-0350", 1, returned=True),
        pending_entry("ST-0351", 1, "ST-0350"),
        pending_entry("ST-0352", 1, "ST-0351"),
    ):
        ledger.stories[entry.id] = entry

    _record, created = ledger.close_wave(1, SHA, limits=lib.AttemptLimits())

    assert created
    assert [record.number for record in ledger.waves] == [1]
    for story_id in ("ST-0350", "ST-0351", "ST-0352"):
        assert ledger.stories[story_id].status == S.PENDING
        assert ledger.stories[story_id].wave == 1
    assert [ledger.stories[s].returned for s in ("ST-0351", "ST-0352")] == [False, False]


@pytest.mark.spec("RL-11-CT-03")
def test_RL_11_CT_03_a_wave_closes_when_escalate_refused_a_failed_story_for_its_scope(
    run, monkeypatch
):
    """Scenario: A wave closes when dispatch escalate refused a failed story for
    its scope. close-wave reads only the ledger and docs/testing.yaml: a git
    command on the story branch, or a read of its diff, fails the test."""
    run.gates(attempts=3, attempts_escalated=3)
    run.write(
        failed_entry(classes=[AU, AU, AU], reason=lib.ESCALATE_REFUSED_SCOPE),
        pending_entry("ST-0351", 1, status=S.DONE, commit_sha=SHA),
    )

    def git(*args: str) -> tuple[int, str, str]:
        assert not any("story/" in arg for arg in args), args
        if args[0] == "rev-parse":
            return 0, SHA, ""
        if args[0] == "cat-file":
            return 1, "", ""
        raise AssertionError(f"close-wave ran git {args}")

    def no_diff(*args):
        raise AssertionError("close-wave read the diff of the story branch")

    monkeypatch.setattr(run.dispatch, "_git", git)
    monkeypatch.setattr(run.dispatch, "_story_scope_violation", no_diff)

    code, _, err = run("close-wave", "1")

    assert code == 0, err
    assert [record.number for record in lib.Ledger.load(run.path).waves] == [1]
    entry = run.entry()
    assert (entry.status, entry.tier) == (S.FAILED, "standard")


# --- RL-17-CT-01: the stdlib writer writes YAML that PyYAML reads (IMPL-0032) --

FREE_TEXT_REASONS = [
    "[WIP] waits on ST-0418",
    "- see the CI log",
    "no",
    "2026-11-19",
    "1:30",
    "`uv sync` fails",
    "*.lock conflict",
    "@reviewer asked",
    "on",
    "Yes",
    "~",
    "0x1F",
    "1_000",
    ".inf",
    "1.5",
    "0755",
    "a #b",
    "% done",
    "!tag",
    "&anchor",
    "{a: b}",
    "? key",
    "| pipe",
    "> fold",
    "'quoted'",
    '"double"',
    "ends with:",
    "x: y",
    "tab\there",
    "Umlaut ä",
    "design question",
]


@pytest.mark.spec("RL-17-CT-01")
@pytest.mark.parametrize("reason", FREE_TEXT_REASONS)
def test_RL_17_CT_01_the_stdlib_writer_writes_free_text_that_pyyaml_reads(
    tmp_path, monkeypatch, reason
):
    """IMPL-0032: dispatch runs without PyYAML, so a `mark-blocked --reason`
    text must read back through yaml.safe_load as the same string."""
    ledger = lib.Ledger()
    ledger.stories["ST-0350"] = failed_entry(status=S.BLOCKED, reason=reason)
    ledger.waves.append(lib.WaveCloseout(
        number=1, blocked=[{"id": "ST-0350", "reason": reason}], branch_head=SHA,
    ))
    monkeypatch.setattr(lib, "yaml", None)
    path = tmp_path / "dispatch-ledger.yaml"

    ledger.save(path)

    data = yaml.safe_load(path.read_text())
    assert data["stories"]["ST-0350"]["reason"] == reason
    assert data["waves"][0]["blocked"][0]["reason"] == reason
    loaded = lib.Ledger.load(path)
    assert loaded.stories["ST-0350"].reason == reason
    assert loaded.waves[0].blocked == [{"id": "ST-0350", "reason": reason}]


@pytest.mark.spec("RL-17-CT-01")
@pytest.mark.parametrize(
    "value", ["feature/login", "story/ST-0350", SHA, "pending", "/tmp/w", "design question"]
)
def test_RL_17_CT_01_the_stdlib_writer_keeps_plain_values_plain(value):
    """A branch, a path, a state, and plain words stay unquoted."""
    assert lib._scalar(value) == value


@pytest.mark.spec("RL-17-CT-01")
def test_RL_17_CT_01_a_wave_record_of_an_older_writer_still_loads(tmp_path):
    """A ledger written before IMPL-0032 holds a wave list as a Python repr."""
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(
        "---\nmode: orchestrated\nstories: {}\nwaves:\n  - number: 1\n"
        "    blocked: [{'id': 'ST-0350', 'reason': 'design question'}]\n"
        "    next_ready: ['ST-0351']\n"
    )

    wave = lib._stdlib_load(path.read_text())["waves"][0]
    record = lib.WaveCloseout.from_dict(wave)

    assert record.blocked == [{"id": "ST-0350", "reason": "design question"}]
    assert record.next_ready == ["ST-0351"]


# --- RL-12: dispatch add accepts only an open blocking finding (ST-0422) ---

FINDING = """---
id: {id}
category: {category}
severity: {severity}
status: {status}
story:
run: feature/login
---

# {id}
"""


def write_finding(run: Run, finding_id: str, *, category: str = "defect",
                  severity: str = "major", status: str = "open") -> None:
    folder = run.root / "docs" / "findings"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{finding_id}.md").write_text(
        FINDING.format(id=finding_id, category=category, severity=severity, status=status)
    )


@pytest.mark.spec("RL-12-CT-01")
@pytest.mark.parametrize(
    "state", [s for s in lib.StoryState if s != lib.StoryState.PENDING], ids=lambda s: s.value
)
def test_RL_12_CT_01_add_refuses_an_id_in_any_state_but_pending(run, state):
    """Scenario: dispatch add refuses an ID in any state but pending."""
    write_finding(run, "BUG-0090")
    run.write(failed_entry("BUG-0090", tier=None, status=state))
    before = run.path.read_text()

    code, _, err = run("add", "BUG-0090")

    assert code == 1
    assert f"BUG-0090 is {state.value}" in err
    assert run.path.read_text() == before


@pytest.mark.spec("RL-12-CT-01")
def test_RL_12_CT_01_add_reuses_a_pending_entry_in_the_next_free_wave(run):
    """A pending entry goes into the wave after every entry and wave record,
    with its attempts and tier reset, and keeps its branch (BR-117)."""
    write_finding(run, "BUG-0090")
    returned = failed_entry(
        "BUG-0090", tier="standard", classes=(AU, AU), status=lib.StoryState.PENDING,
        returned=True, escalation_granted=True, active_tier="standard",
        attempt_grants=[{"tier": "standard", "attempt_count": 1}], reason="merge conflict",
    )
    run.write(returned, failed_entry("ST-0350", status=lib.StoryState.DONE))
    ledger = lib.Ledger.load(run.path)
    ledger.waves.append(lib.WaveCloseout(number=4))
    ledger.save(run.path)

    code, out, err = run("add", "BUG-0090")

    assert code == 0, err
    entry = run.entry("BUG-0090")
    assert (entry.status, entry.wave, entry.returned) == (S.PENDING, 5, False)
    assert (entry.tier, entry.active_tier, entry.escalation_granted) == (None, None, False)
    assert (entry.attempts, entry.attempt_grants, entry.reason) == ([], [], None)
    assert entry.branch == "story/BUG-0090"
    assert lib.counted_tier(entry) == "economy"
    assert "BUG-0090 is pending in wave 5" in out


CASES = {
    "a story of the backlog": ("ST-0351", "ST-0351 is a story, and add takes only a finding"),
    "a finding ID with a backlog file": ("BUG-0097", "BUG-0097 is a story, and add takes only a finding"),
    "a resolved finding": ("BUG-0093", "the status resolved"),
    "a minor finding": ("BUG-0094", "BUG-0094 does not block"),
    "a suggestion": ("BUG-0095", "BUG-0095 does not block"),
    "no finding file": ("BUG-0096", "docs/findings/BUG-0096.md does not exist"),
}


@pytest.mark.spec("RL-12-CT-02")
@pytest.mark.parametrize("case", list(CASES))
def test_RL_12_CT_02_add_accepts_only_an_open_blocking_finding(run, case):
    """Scenario Outline: dispatch add accepts only an open blocking finding."""
    (run.root / "backlog").mkdir()
    (run.root / "backlog" / "ST-0351.md").write_text("---\nid: ST-0351\nstatus: open\n---\n")
    (run.root / "backlog" / "BUG-0097.md").write_text("---\nid: BUG-0097\nstatus: open\n---\n")
    write_finding(run, "BUG-0097")
    write_finding(run, "BUG-0093", status="resolved")
    write_finding(run, "BUG-0094", severity="minor")
    write_finding(run, "BUG-0095", category="suggestion")
    run.write(failed_entry("ST-0350", status=lib.StoryState.DONE))
    unit_id, reason = CASES[case]

    code, _, err = run("add", unit_id)

    assert code == 1
    assert reason in err
    assert unit_id not in lib.Ledger.load(run.path).stories


@pytest.mark.spec("RL-12-CT-02")
@pytest.mark.parametrize(("category", "severity"), [("defect", "major"), ("risk", "major")])
def test_RL_12_CT_02_add_accepts_each_blocking_class(run, category, severity):
    """A defect or risk finding at the severity critical or major blocks (BR-085)."""
    write_finding(run, "BUG-0090", category=category, severity=severity)
    run.write(failed_entry("ST-0350", status=lib.StoryState.DONE))

    code, _, err = run("add", "BUG-0090")

    assert code == 0, err
    entry = run.entry("BUG-0090")
    assert (entry.status, entry.wave, entry.deps, entry.tier) == (S.PENDING, 2, [], None)
    assert entry.feature_branch == "feature/login"
