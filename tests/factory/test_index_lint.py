"""Contract tests for index-lint gate script."""

from __future__ import annotations

from conftest import load_script

il = load_script("index-lint")


class TestCountTokens:
    def test_nonempty_string(self):
        result = il.count_tokens("hello world")
        assert result > 0

    def test_empty_string(self):
        result = il.count_tokens("")
        assert result >= 0


class TestParseFrontmatter:
    def test_scalar_keys(self):
        text = "---\nname: test-agent\ntitle: Test Agent\nphase: 1\n---\nBody"
        fm = il.parse_frontmatter(text)
        assert fm["name"] == "test-agent"
        assert fm["title"] == "Test Agent"
        assert fm["phase"] == "1"

    def test_no_frontmatter(self):
        assert il.parse_frontmatter("No frontmatter") == {}

    def test_list_keys(self):
        text = "---\nskills:\n  - grilling\n  - spec-feedback\n---\n"
        fm = il.parse_frontmatter(text)
        assert fm["skills"] == ["grilling", "spec-feedback"]

    def test_folded_scalar(self):
        text = "---\ndescription: >-\n  Long description\n  spanning lines\n---\n"
        fm = il.parse_frontmatter(text)
        assert "Long description" in fm["description"]

    def test_quoted_values(self):
        text = '---\ntitle: "Quoted Title"\n---\n'
        fm = il.parse_frontmatter(text)
        assert fm["title"] == "Quoted Title"

    def test_unknown_keys_skipped(self):
        text = "---\nname: x\nunknown_key: val\n---\n"
        fm = il.parse_frontmatter(text)
        assert "name" in fm
        assert "unknown_key" not in fm


class TestLoadAgents:
    def test_loads_from_directory(self, tmp_path):
        (tmp_path / "test-agent.md").write_text(
            "---\nname: test-agent\ntitle: Test\nphase: 1\nphase-name: Proposal\n---\nBody"
        )
        agents = il.load_agents(tmp_path)
        assert len(agents) == 1
        assert agents[0]["name"] == "test-agent"
        assert agents[0]["_tokens"] > 0

    def test_skips_files_without_name(self, tmp_path):
        (tmp_path / "no-name.md").write_text("---\ntitle: No Name\n---\n")
        agents = il.load_agents(tmp_path)
        assert agents == []

    def test_empty_dir(self, tmp_path):
        assert il.load_agents(tmp_path) == []


class TestLoadSkills:
    def test_loads_skill_directories(self, tmp_path):
        skill_dir = tmp_path / "grilling"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: grilling\ncategory: requirements\ndescription: Grill stakeholders\n---\nContent"
        )
        skills = il.load_skills(tmp_path)
        assert len(skills) == 1
        assert skills[0]["name"] == "grilling"

    def test_skips_without_name(self, tmp_path):
        skill_dir = tmp_path / "broken"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\ncategory: utility\n---\nNo name")
        assert il.load_skills(tmp_path) == []


class TestLoadPlaybooks:
    def test_loads_with_agent_sequence(self, tmp_path):
        (tmp_path / "feature-addition.md").write_text(
            "---\ntitle: Feature Addition\ncategory: implementation\n---\n"
            "**Agent**: `requirements-agent`\n**Agent**: `developer-agent`\n"
        )
        playbooks = il.load_playbooks(tmp_path)
        assert len(playbooks) == 1
        assert playbooks[0]["name"] == "feature-addition"
        assert playbooks[0]["agents"] == ["requirements-agent", "developer-agent"]

    def test_detects_fsm_file(self, tmp_path):
        (tmp_path / "test-pb.md").write_text("---\ntitle: Test\n---\nBody")
        (tmp_path / "test-pb.fsm.yml").write_text("states:\n  draft:\n")
        playbooks = il.load_playbooks(tmp_path)
        assert "_fsm_path" in playbooks[0]


class TestLoadRulebooks:
    def test_loads_nested(self, tmp_path):
        conv = tmp_path / "conventions"
        conv.mkdir()
        (conv / "naming.md").write_text("# Naming convention\nContent")
        rulebooks = il.load_rulebooks(tmp_path)
        assert len(rulebooks) == 1
        assert rulebooks[0]["name"] == "naming"
        assert rulebooks[0]["category"] == "conventions"

    def test_skips_templates(self, tmp_path):
        templates = tmp_path / "templates"
        templates.mkdir()
        (templates / "template.md").write_text("Template content")
        assert il.load_rulebooks(tmp_path) == []


class TestYamlScalar:
    def test_plain_string(self):
        assert il._yaml_scalar("hello") == "hello"

    def test_string_needing_quotes(self):
        result = il._yaml_scalar("value: with colon")
        assert result.startswith('"') and result.endswith('"')

    def test_boolean(self):
        assert il._yaml_scalar(True) == "true"
        assert il._yaml_scalar(False) == "false"

    def test_integer(self):
        assert il._yaml_scalar(42) == "42"

    def test_none(self):
        assert il._yaml_scalar(None) == "null"

    def test_empty_string_quoted(self):
        assert il._yaml_scalar("") == '""'


class TestBuildAgentsData:
    def test_computes_total_tokens(self):
        agents = [
            {
                "name": "test-agent",
                "title": "Test",
                "phase": "1",
                "phase-name": "Proposal",
                "_path": "factory/agents/test-agent.md",
                "_tokens": 100,
                "skills": ["grilling"],
                "inputs": ["factory/rulebooks/rules.md"],
            }
        ]
        skill_tokens = {"grilling": 200}
        rulebook_tokens = {"rules": 300}
        entries, _warnings = il.build_agents_data(agents, skill_tokens, rulebook_tokens)
        assert len(entries) == 1
        assert entries[0]["total_tokens"] == 600  # 100 + 200 + 300

    def test_warns_on_high_token_count(self):
        agents = [
            {
                "name": "big-agent",
                "title": "Big",
                "phase": "1",
                "phase-name": "X",
                "_path": "factory/agents/big-agent.md",
                "_tokens": 25000,
            }
        ]
        _, warnings = il.build_agents_data(agents, {}, {})
        assert any("exceeds" in w for w in warnings)


class TestBuildSkillsData:
    def test_warns_on_missing_category(self):
        skills = [{"name": "test", "_path": "skills/test/SKILL.md", "_tokens": 50}]
        _, warnings = il.build_skills_data(skills)
        assert any("category" in w for w in warnings)

    def test_orders_by_canonical_category(self):
        skills = [
            {"name": "b", "category": "quality", "_path": "b", "_tokens": 10},
            {"name": "a", "category": "requirements", "_path": "a", "_tokens": 10},
        ]
        entries, _ = il.build_skills_data(skills)
        assert entries[0]["name"] == "a"


class TestRenderIndex:
    def test_produces_yaml_output(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "test.md").write_text(
            "---\nname: test\ntitle: Test Agent\nphase: 1\nphase-name: Init\n---\nBody"
        )
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        playbooks_dir = tmp_path / "playbooks"
        playbooks_dir.mkdir()
        rulebooks_dir = tmp_path / "rulebooks"
        rulebooks_dir.mkdir()
        out = tmp_path / "INDEX.yaml"

        content, _warnings = il.render_index(
            agents_dir, skills_dir, playbooks_dir, rulebooks_dir, out
        )
        assert "agents:" in content
        assert "skills:" in content
        assert "playbooks:" in content
        assert "rulebooks:" in content
        assert "test" in content


class TestMainRoundTrip:
    """Integration: main() wires load → render → write/check → exit code."""

    def _make_factory_dirs(self, tmp_path):
        for name in ("agents", "skills", "playbooks", "rulebooks"):
            (tmp_path / name).mkdir()
        (tmp_path / "agents" / "test.md").write_text(
            "---\nname: test\ntitle: Test\nphase: 1\nphase-name: Init\n---\nBody"
        )
        return tmp_path

    def test_generates_index(self, tmp_path):
        base = self._make_factory_dirs(tmp_path)
        out = tmp_path / "INDEX.yaml"
        rc = il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
            ]
        )
        assert rc == 0
        assert out.exists()
        assert "test" in out.read_text()

    def test_check_passes_when_current(self, tmp_path):
        base = self._make_factory_dirs(tmp_path)
        out = tmp_path / "INDEX.yaml"
        il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
            ]
        )
        rc = il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
                "--check",
            ]
        )
        assert rc == 0

    def test_check_fails_when_stale(self, tmp_path):
        base = self._make_factory_dirs(tmp_path)
        out = tmp_path / "INDEX.yaml"
        out.write_text("stale content\n")
        rc = il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
                "--check",
            ]
        )
        assert rc == 1

    def test_idempotent_regeneration(self, tmp_path):
        base = self._make_factory_dirs(tmp_path)
        out = tmp_path / "INDEX.yaml"
        il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
            ]
        )
        first = out.read_text()
        il.main(
            [
                "--agents-dir",
                str(base / "agents"),
                "--skills-dir",
                str(base / "skills"),
                "--playbooks-dir",
                str(base / "playbooks"),
                "--rulebooks-dir",
                str(base / "rulebooks"),
                "--out",
                str(out),
            ]
        )
        assert out.read_text() == first
