from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIENTATION = ROOT / "factory" / "config" / "AGENTS.md"


def test_rulebook_ingestion_is_the_first_top_level_must() -> None:
    text = ORIENTATION.read_text(encoding="utf-8")
    rules = text.split("## Rules\n", 1)[1]
    first_must = next(
        line for line in rules.splitlines() if line.startswith("- **MUST")
    )

    assert "TOP-LEVEL SESSION INSTRUCTION" in first_must
    assert "factory/rulebooks/rules.md" in first_must
    assert "before answering the first prompt" in first_must
    assert "read and ingest" in first_must


def test_first_prompt_acknowledges_rulebook_ingestion() -> None:
    text = ORIENTATION.read_text(encoding="utf-8")

    assert "acknowledge that you have ingested `factory/rulebooks/rules.md`" in text
