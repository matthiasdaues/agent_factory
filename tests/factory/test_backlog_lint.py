"""Contract tests for backlog-lint gate script."""

from __future__ import annotations

from pathlib import Path

from conftest import load_script

bl = load_script("backlog-lint")


def _write_story(backlog: Path, story_id: str, **fm_fields):
    """Build a minimal valid story file inside a backlog directory."""
    defaults = {
        "id": story_id,
        "epic": "EPIC-1",
        "title": "Test",
        "tier": "standard",
        "status": "pending",
        "touches": ["src/"],
    }
    defaults.update(fm_fields)
    lines = ["---"]
    for k, v in defaults.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.extend(["---", "Body text."])
    (backlog / f"{story_id}.md").write_text("\n".join(lines))


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        text = "---\nid: ST-0001\ntitle: Test story\ntier: standard\n---\nBody"
        fm, body = bl.parse_frontmatter(text)
        assert fm["id"] == "ST-0001"
        assert fm["title"] == "Test story"
        assert fm["tier"] == "standard"
        assert body == "Body"

    def test_no_frontmatter(self):
        fm, body = bl.parse_frontmatter("Just body text")
        assert fm is None
        assert body == "Just body text"

    def test_missing_closing_delimiter(self):
        fm, _body = bl.parse_frontmatter("---\nid: ST-0001\n")
        assert fm is None

    def test_block_sequence(self):
        text = "---\ntouches:\n  - src/orchestrator/\n  - tests/\n---\n"
        fm, _ = bl.parse_frontmatter(text)
        assert fm["touches"] == ["src/orchestrator/", "tests/"]

    def test_inline_flow_sequence(self):
        text = "---\ndeps: [ST-0001, ST-0002]\n---\n"
        fm, _ = bl.parse_frontmatter(text)
        assert fm["deps"] == ["ST-0001", "ST-0002"]

    def test_boolean_values(self):
        text = "---\nflag: true\n---\n"
        fm, _ = bl.parse_frontmatter(text)
        assert fm["flag"] is True

    def test_null_values(self):
        text = "---\nfield: ~\n---\n"
        fm, _ = bl.parse_frontmatter(text)
        assert fm["field"] is None

    def test_quoted_values(self):
        text = '---\ntitle: "My Story"\n---\n'
        fm, _ = bl.parse_frontmatter(text)
        assert fm["title"] == "My Story"


class TestCheckStory:
    def _make_fm(self, **overrides):
        base = {
            "id": "ST-0001",
            "epic": "EPIC-1",
            "title": "Test story",
            "tier": "standard",
            "status": "pending",
            "touches": ["src/"],
        }
        base.update(overrides)
        return base

    def test_valid_story_no_errors(self, tmp_path):
        fm = self._make_fm()
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_id_filename_mismatch(self, tmp_path):
        fm = self._make_fm(id="ST-9999")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001", "ST-9999"}, tmp_path)
        assert any(f.code == "BL-ID" for f in findings)

    def test_missing_required_fields(self, tmp_path):
        fm = {"id": "ST-0001"}
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        missing = [f for f in findings if f.code == "BL-MISSING"]
        assert len(missing) >= 4

    def test_invalid_tier(self, tmp_path):
        fm = self._make_fm(tier="huge")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-ENUM" and "tier" in f.message for f in findings)

    def test_invalid_status(self, tmp_path):
        fm = self._make_fm(status="wip")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-ENUM" and "status" in f.message for f in findings)

    def test_removed_fields_are_extra(self, tmp_path):
        """Fields moved out of frontmatter are now flagged as unknown."""
        fm = self._make_fm(strategy="direct", risk_domains=["security"], notes="x")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        extras = [f for f in findings if f.code == "BL-EXTRA"]
        extra_fields = {f.message.split("'")[1] for f in extras}
        assert "strategy" in extra_fields
        assert "risk_domains" in extra_fields
        assert "notes" in extra_fields

    def test_extra_field_warns(self, tmp_path):
        fm = self._make_fm(bogus="value")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-EXTRA" for f in findings)

    def test_dep_missing_story_warns(self, tmp_path):
        fm = self._make_fm(deps=["ST-9999"])
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-DEP" and f.severity == "warning" for f in findings)

    def test_dep_bad_pattern_errors(self, tmp_path):
        fm = self._make_fm(deps=["not-a-story"])
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-DEP" and f.severity == "error" for f in findings)

    def test_machine_field_in_body_warns(self, tmp_path):
        fm = self._make_fm()
        path = tmp_path / "ST-0001.md"
        path.touch()
        body = "## tier\nThe tier is standard."
        findings = bl.check_story(path, fm, body, {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-DUP" for f in findings)

    def test_touches_empty_warns(self, tmp_path):
        fm = self._make_fm(touches=[])
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-EMPTY" and "touches" in f.message for f in findings)

    def test_touches_not_array_errors(self, tmp_path):
        fm = self._make_fm(touches="src/")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-TYPE" and "touches" in f.message for f in findings)

    def test_risk_level_valid_values(self, tmp_path):
        for level in ("low", "medium", "high"):
            fm = self._make_fm(risk_level=level)
            path = tmp_path / "ST-0001.md"
            path.touch()
            findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
            assert not any(f.code == "BL-ENUM" and "risk_level" in f.message for f in findings)

    def test_risk_level_invalid_value(self, tmp_path):
        fm = self._make_fm(risk_level="extreme")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-ENUM" and "risk_level" in f.message for f in findings)

    def test_risk_level_absent_ok(self, tmp_path):
        fm = self._make_fm()
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert not any(f.code == "BL-ENUM" and "risk_level" in f.message for f in findings)


class TestCheckBacklog:
    def test_empty_dir_returns_info(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        findings, count = bl.check_backlog(backlog)
        assert count == 0
        assert any(f.code == "BL-EMPTY" for f in findings)

    def test_nonexistent_dir_returns_error(self, tmp_path):
        findings, _count = bl.check_backlog(tmp_path / "missing")
        assert any(f.code == "BL-DIR" for f in findings)

    def test_valid_stories_pass(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        _write_story(backlog, "ST-0001")
        _write_story(backlog, "ST-0002", deps=["ST-0001"])
        findings, count = bl.check_backlog(backlog)
        assert count == 2
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_duplicate_ids_detected(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        _write_story(backlog, "ST-0001")
        (backlog / "ST-0002.md").write_text(
            "---\nid: ST-0001\nepic: E\ntitle: T\ntier: standard\n"
            "status: pending\ntouches: [src/]\n---\n"
        )
        findings, _ = bl.check_backlog(backlog)
        assert any(f.code == "BL-DUP-ID" for f in findings)


class TestConcernsField:
    """The concerns field is optional and accepted without BL-EXTRA warning.

    Structure: concerns: {domain: [string], technical: [string]}, both keys
    optional.
    """

    def _make_fm(self, **overrides):
        base = {
            "id": "ST-0001",
            "epic": "EPIC-1",
            "title": "Test story",
            "tier": "standard",
            "status": "pending",
            "touches": ["src/"],
        }
        base.update(overrides)
        return base

    def test_concerns_field_accepted(self, tmp_path):
        """A story with a valid concerns field produces no BL-EXTRA warning."""
        fm = self._make_fm(concerns={"domain": ["billing"], "technical": ["backend"]})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        extra = [f for f in findings if f.code == "BL-EXTRA"]
        assert extra == []

    def test_concerns_field_optional(self, tmp_path):
        """A story without concerns produces no error."""
        fm = self._make_fm()
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_concerns_domain_only(self, tmp_path):
        """Concerns with only domain key is valid."""
        fm = self._make_fm(concerns={"domain": ["billing"]})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        extra = [f for f in findings if f.code == "BL-EXTRA"]
        assert extra == []

    def test_concerns_technical_only(self, tmp_path):
        """Concerns with only technical key is valid."""
        fm = self._make_fm(concerns={"technical": ["backend"]})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        extra = [f for f in findings if f.code == "BL-EXTRA"]
        assert extra == []

    def test_concerns_invalid_type_errors(self, tmp_path):
        """Concerns must be a mapping, not a string."""
        fm = self._make_fm(concerns="backend")
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-TYPE" and "concerns" in f.message for f in findings)

    def test_concerns_domain_not_list_errors(self, tmp_path):
        """concerns.domain must be a list of strings."""
        fm = self._make_fm(concerns={"domain": "billing"})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-TYPE" and "domain" in f.message for f in findings)

    def test_concerns_technical_not_list_errors(self, tmp_path):
        """concerns.technical must be a list of strings."""
        fm = self._make_fm(concerns={"technical": 42})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-TYPE" and "technical" in f.message for f in findings)

    def test_concerns_unknown_subkey_warns(self, tmp_path):
        """Keys other than domain/technical in concerns trigger a warning."""
        fm = self._make_fm(concerns={"domain": ["billing"], "other": ["x"]})
        path = tmp_path / "ST-0001.md"
        path.touch()
        findings = bl.check_story(path, fm, "", {"ST-0001"}, tmp_path)
        assert any(f.code == "BL-TYPE" and "other" in f.message for f in findings)


class TestDetectCycles:
    def test_no_cycle(self):
        graph = {"A": ["B"], "B": ["C"], "C": []}
        assert bl._detect_cycles(graph) == []

    def test_simple_cycle(self):
        graph = {"A": ["B"], "B": ["A"]}
        cycles = bl._detect_cycles(graph)
        assert len(cycles) >= 1

    def test_self_loop(self):
        graph = {"A": ["A"]}
        cycles = bl._detect_cycles(graph)
        assert len(cycles) >= 1

    def test_three_node_cycle(self):
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        cycles = bl._detect_cycles(graph)
        assert len(cycles) >= 1


class TestMainRoundTrip:
    """Integration: main() wires parsing → checking → exit code."""

    def test_clean_backlog_exits_zero(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        _write_story(backlog, "ST-0001")
        rc = bl.main(["--backlog-dir", str(backlog)])
        assert rc == 0

    def test_bad_backlog_exits_nonzero(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text("---\nid: ST-0001\n---\nNo fields.")
        rc = bl.main(["--backlog-dir", str(backlog)])
        assert rc > 0

    def test_report_only_always_exits_zero(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text("---\nid: ST-0001\n---\nNo fields.")
        rc = bl.main(["--backlog-dir", str(backlog), "--report-only"])
        assert rc == 0

    def test_json_format_outputs_json(self, tmp_path, capsys):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        _write_story(backlog, "ST-0001")
        bl.main(["--backlog-dir", str(backlog), "--format", "json"])
        import json

        output = json.loads(capsys.readouterr().out)
        assert "findings" in output
        assert "summary" in output

    def test_missing_frontmatter_end_to_end(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text("No frontmatter at all.")
        rc = bl.main(["--backlog-dir", str(backlog)])
        assert rc > 0

    def test_cycle_detected_end_to_end(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        _write_story(backlog, "ST-0001", deps=["ST-0002"])
        _write_story(backlog, "ST-0002", deps=["ST-0001"])
        rc = bl.main(["--backlog-dir", str(backlog)])
        assert rc > 0
