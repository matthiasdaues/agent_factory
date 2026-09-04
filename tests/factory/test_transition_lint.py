"""Contract tests for transition-lint gate script."""

from __future__ import annotations

from conftest import load_script

tl = load_script("transition-lint")


class TestParseMarker:
    def test_parses_flat_key_value(self):
        text = "playbook: feature-addition\nstate: implementation\n"
        result = tl.parse_marker(text)
        assert result == {"playbook": "feature-addition", "state": "implementation"}

    def test_strips_comments(self):
        text = "playbook: feature-addition  # the active playbook\nstate: spec\n"
        result = tl.parse_marker(text)
        assert result["playbook"] == "feature-addition"

    def test_skips_blank_lines(self):
        text = "\nplaybook: x\n\nstate: y\n"
        result = tl.parse_marker(text)
        assert result == {"playbook": "x", "state": "y"}

    def test_empty_returns_empty(self):
        assert tl.parse_marker("") == {}


class TestParseFsm:
    MINIMAL_FSM = """\
states:
  proposal:
    outputs:
      - docs/proposals/*.md
    on:
      approve:
        transitions:
          to: spec
  spec:
    outputs:
      - docs/spec/**/*.md
"""

    def test_parses_states(self):
        fsm = tl.parse_fsm(self.MINIMAL_FSM)
        assert "proposal" in fsm["states"]
        assert "spec" in fsm["states"]

    def test_parses_outputs(self):
        fsm = tl.parse_fsm(self.MINIMAL_FSM)
        assert fsm["states"]["proposal"]["outputs"] == ["docs/proposals/*.md"]

    def test_parses_transitions(self):
        fsm = tl.parse_fsm(self.MINIMAL_FSM)
        trans = fsm["states"]["proposal"]["on"]["approve"]["transitions"]
        assert trans["to"] == "spec"


class TestStateOutputs:
    def test_extracts_output_globs(self):
        fsm = {
            "states": {
                "spec": {"outputs": ["docs/spec/*.md"]},
                "impl": {"outputs": ["src/*.py", "tests/*.py"]},
            }
        }
        result = tl.state_outputs(fsm)
        assert result == {
            "spec": ["docs/spec/*.md"],
            "impl": ["src/*.py", "tests/*.py"],
        }

    def test_skips_states_without_outputs(self):
        fsm = {"states": {"idle": {}}}
        assert tl.state_outputs(fsm) == {}


class TestSuccessors:
    def test_returns_transition_targets(self):
        fsm = {
            "states": {
                "a": {
                    "on": {
                        "advance": {"transitions": {"to": "b"}},
                        "skip": {"transitions": {"to": "c"}},
                    }
                }
            }
        }
        assert tl.successors(fsm, "a") == ["b", "c"]

    def test_unknown_state_returns_empty(self):
        fsm = {"states": {"a": {}}}
        assert tl.successors(fsm, "nonexistent") == []


class TestStatesForFile:
    def test_matches_glob(self):
        outputs = {"spec": ["docs/spec/*.md"], "impl": ["src/*.py"]}
        assert tl.states_for_file("docs/spec/prd.md", outputs) == ["spec"]

    def test_no_match_returns_empty(self):
        outputs = {"spec": ["docs/spec/*.md"]}
        assert tl.states_for_file("README.md", outputs) == []

    def test_multi_state_match(self):
        outputs = {"a": ["docs/*.md"], "b": ["docs/*.md"]}
        result = tl.states_for_file("docs/readme.md", outputs)
        assert sorted(result) == ["a", "b"]


class TestCheckTransitions:
    def test_no_marker_returns_info(self, tmp_path):
        marker = tmp_path / "missing-marker.yml"
        findings = tl.check_transitions(["any.py"], marker, tmp_path)
        assert len(findings) == 1
        assert findings[0].code == "TL-NOMARKER"
        assert findings[0].severity == "info"

    def test_marker_missing_fields_returns_error(self, tmp_path):
        marker = tmp_path / "marker.yml"
        marker.write_text("playbook: x\n")
        findings = tl.check_transitions(["any.py"], marker, tmp_path)
        assert any(f.code == "TL-MARKER" and f.severity == "error" for f in findings)

    def test_missing_fsm_returns_error(self, tmp_path):
        marker = tmp_path / "marker.yml"
        marker.write_text("playbook: test-pb\nstate: draft\n")
        playbooks = tmp_path / "playbooks"
        playbooks.mkdir()
        findings = tl.check_transitions(["any.py"], marker, playbooks)
        assert any(f.code == "TL-NOFSM" for f in findings)

    def test_current_state_file_passes(self, tmp_path):
        playbooks = tmp_path / "playbooks"
        playbooks.mkdir()
        fsm = playbooks / "test-pb.fsm.yml"
        fsm.write_text(
            "states:\n"
            "  draft:\n"
            "    outputs:\n"
            "      - docs/draft/*.md\n"
            "    on:\n"
            "      approve:\n"
            "        transitions:\n"
            "          to: final\n"
            "  final:\n"
            "    outputs:\n"
            "      - docs/final/*.md\n"
        )
        marker = tmp_path / "marker.yml"
        marker.write_text("playbook: test-pb\nstate: draft\n")
        findings = tl.check_transitions(["docs/draft/x.md"], marker, playbooks)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_wrong_state_file_blocked(self, tmp_path):
        playbooks = tmp_path / "playbooks"
        playbooks.mkdir()
        fsm = playbooks / "test-pb.fsm.yml"
        fsm.write_text(
            "states:\n"
            "  draft:\n"
            "    outputs:\n"
            "      - docs/draft/*.md\n"
            "  final:\n"
            "    outputs:\n"
            "      - docs/final/*.md\n"
        )
        marker = tmp_path / "marker.yml"
        marker.write_text("playbook: test-pb\nstate: draft\n")
        findings = tl.check_transitions(["docs/final/x.md"], marker, playbooks)
        errors = [f for f in findings if f.code == "TL-ORDER"]
        assert len(errors) == 1

    def test_ungoverned_file_passes(self, tmp_path):
        playbooks = tmp_path / "playbooks"
        playbooks.mkdir()
        fsm = playbooks / "test-pb.fsm.yml"
        fsm.write_text("states:\n  draft:\n    outputs:\n      - docs/*.md\n")
        marker = tmp_path / "marker.yml"
        marker.write_text("playbook: test-pb\nstate: draft\n")
        findings = tl.check_transitions(["README.md"], marker, playbooks)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []


class TestMainRoundTrip:
    """Integration: main() wires staged files → check_transitions → exit code."""

    def _setup_playbook(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        import subprocess

        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        playbooks = repo / "factory" / "playbooks"
        playbooks.mkdir(parents=True)
        fsm = playbooks / "test-pb.fsm.yml"
        fsm.write_text(
            "states:\n"
            "  draft:\n"
            "    outputs:\n"
            "      - docs/draft/*.md\n"
            "  final:\n"
            "    outputs:\n"
            "      - docs/final/*.md\n"
        )
        return repo

    def test_no_marker_exits_zero(self, tmp_path, monkeypatch):
        repo = self._setup_playbook(tmp_path)
        monkeypatch.chdir(repo)
        rc = tl.main(["--repo-root", str(repo)])
        assert rc == 0

    def test_report_only_always_exits_zero(self, tmp_path, monkeypatch):
        repo = self._setup_playbook(tmp_path)
        cw = repo / ".current-work"
        cw.mkdir()
        (cw / "playbook-state.yml").write_text("playbook: test-pb\nstate: draft\n")
        monkeypatch.chdir(repo)
        rc = tl.main(
            [
                "--repo-root",
                str(repo),
                "--playbooks-dir",
                str(repo / "factory" / "playbooks"),
                "--report-only",
            ]
        )
        assert rc == 0

    def test_json_format(self, tmp_path, monkeypatch, capsys):
        import json

        repo = self._setup_playbook(tmp_path)
        monkeypatch.chdir(repo)
        tl.main(["--repo-root", str(repo), "--format", "json"])
        output = json.loads(capsys.readouterr().out)
        assert "findings" in output
        assert "summary" in output
