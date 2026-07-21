"""Tests for `factory/scripts/policy-validate`.

policy-validate is stage 2 of the research validation order (schema -> policy ->
semantic): a deterministic, stdlib-only policy validator (ST-0025). It enforces
the *enforceable* half of the four research policies over a related set of
artifacts and hands the semantic questions to stage 3.

Like `test_schema_validate.py`, every test drives the real process seam —
`subprocess.run([sys.executable, "factory/scripts/policy-validate", ...])` over
JSON fixtures written into `tmp_path` — and asserts the CLI's exit code and
message. Each named test below is a passing proof of one required behaviour from
the story's "Required Tests" list, plus a happy-path set that passes cleanly.

Fixture convention: a claim's whole lifecycle (conjecture, sources, tests,
reviews, votes, register, report) is written to `tmp_path` as JSON files named
after their kind (the validator infers kind from the file-name prefix). The
`build_run` helper produces a clean, admissible baseline; each test mutates one
facet of it to prove the corresponding rule bites.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "policy-validate"

_HASH_A = "a" * 64
_HASH_B = "b" * 64


def _write_run(tmp_path: Path, run: dict) -> None:
    """Write one research run's artifacts to `tmp_path` as kind-named JSON files.

    `run` maps a file stem (whose prefix names the artifact kind) to the JSON
    body. Directories are not needed: the validator globs the flat set.
    """
    for stem, body in run.items():
        (tmp_path / f"{stem}.json").write_text(json.dumps(body), encoding="utf-8")


def _run(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *extra_args, str(tmp_path)],
        capture_output=True,
        text=True,
    )


def build_run() -> dict:
    """A clean, admissible single-claim research run — the happy-path baseline.

    CLAIM-0001, authored by researcher-1, has two independent sources, two run
    tests (one SURVIVED, one INCONCLUSIVE kept visible), three distinct reviewers
    with no blocker, and three current-hash SURVIVE votes. The register lists it
    surviving with its qualification preserved, and the report cites it.
    """
    return {
        "conjecture-CLAIM-0001": {
            "claim_id": "CLAIM-0001",
            "author": "researcher-1",
            "claim": "Widget sales rose in 2024.",
            "scope": "Region A, calendar year 2024.",
            "assumptions": ["figures are inflation-adjusted"],
            "supporting_evidence": ["src-A", "src-B"],
            "contrary_evidence": [],
            "possible_refuting_evidence": "Audited figures showing no rise.",
            "planned_tests": ["q1", "q2"],
            "qualifications": ["current as of 2024 filings"],
            "content_hash": _HASH_A,
        },
        "source-A": {
            "source_identity": "src-A",
            "author_or_issuing_body": "Agency X",
            "publisher": "Agency X Press",
            "publication_date": "2025-01-10T00:00:00Z",
            "relevant_event_date": "2024-12-31",
            "source_family": "family-1",
            "precise_evidence_location": "Table 3",
            "method": "audit",
            "limitations": "region A only",
            "provenance": "downloaded from agency portal",
        },
        "source-B": {
            "source_identity": "src-B",
            "author_or_issuing_body": "Firm Y",
            "publisher": "Firm Y",
            "publication_date": "2025-02-01T00:00:00Z",
            "relevant_event_date": "2024-12-31",
            "source_family": "family-2",
            "precise_evidence_location": "p. 12",
            "method": "survey",
            "limitations": "self-reported",
            "provenance": "vendor report",
        },
        "test-CLAIM-0001-q1": {
            "claim_id": "CLAIM-0001",
            "claim_version": 1,
            "test_id": "T1",
            "test_question": "q1",
            "refuting_result": "no rise",
            "method": "recompute",
            "evidence_examined": ["src-A"],
            "observed_result": "rise confirmed",
            "limitations": "none",
            "outcome": "SURVIVED",
        },
        "test-CLAIM-0001-q2": {
            "claim_id": "CLAIM-0001",
            "claim_version": 1,
            "test_id": "T2",
            "test_question": "q2",
            "refuting_result": "no rise in survey",
            "method": "survey cross-check",
            "evidence_examined": ["src-B"],
            "observed_result": "unclear",
            "limitations": "small sample",
            "outcome": "INCONCLUSIVE",
        },
        "review-1": {
            "review_id": "REV-1",
            "claim_id": "CLAIM-0001",
            "reviewer": "reviewer-1",
            "claim_hash": _HASH_A,
            "checks": _CHECKS,
            "defect_level": "NOTE",
        },
        "review-2": {
            "review_id": "REV-2",
            "claim_id": "CLAIM-0001",
            "reviewer": "reviewer-2",
            "claim_hash": _HASH_A,
            "checks": _CHECKS,
            "defect_level": "MINOR",
        },
        "review-3": {
            "review_id": "REV-3",
            "claim_id": "CLAIM-0001",
            "reviewer": "reviewer-3",
            "claim_hash": _HASH_A,
            "checks": _CHECKS,
            "defect_level": "NOTE",
        },
        "vote-1": {
            "review_ref": "REV-1",
            "claim_hash": _HASH_A,
            "reviewer": "reviewer-1",
            "value": "SURVIVE",
        },
        "vote-2": {
            "review_ref": "REV-2",
            "claim_hash": _HASH_A,
            "reviewer": "reviewer-2",
            "value": "SURVIVE",
        },
        "vote-3": {
            "review_ref": "REV-3",
            "claim_hash": _HASH_A,
            "reviewer": "reviewer-3",
            "value": "SURVIVE",
        },
        "claim-register": {
            "orchestrator": "orchestrator-1",
            "surviving_claims": [
                {
                    "claim_id": "CLAIM-0001",
                    "claim_text": "Widget sales rose in 2024.",
                    "scope": "Region A, 2024.",
                    "assumptions": ["figures are inflation-adjusted"],
                    "evidence": ["src-A", "src-B"],
                    "tests": ["T1", "T2"],
                    "failed_tests": ["T2"],
                    "reviews": ["REV-1", "REV-2", "REV-3"],
                    "vote_result": "SURVIVE",
                    "qualifications": ["current as of 2024 filings"],
                    "remaining_possible_refuters": ["a later audit"],
                    "applicable_date": "2025-03-01T00:00:00Z",
                }
            ],
            "refuted_claims": [],
            "unresolved_claims": [],
            "superseded_claims": [],
        },
        "final-report": {
            "findings": [
                {
                    "title": "Sales",
                    "summary": "Sales rose within the tested scope.",
                    "surviving_claim_refs": ["CLAIM-0001"],
                }
            ],
            "refuted_conjectures": [],
            "unresolved_alternatives": [],
            "recommendations": [],
            "evidence_gaps": [],
            "limitations": ["region A only"],
        },
    }


# All ten review checks assessed — the shape the review schema requires.
_CHECKS = {
    "testable": True,
    "alternatives_considered": True,
    "tests_severe": True,
    "survived_unchanged": True,
    "sources_support_wording": True,
    "sources_independent": True,
    "assumptions_explicit": True,
    "within_tested_scope": True,
    "contrary_evidence_addressed": True,
    "possible_overturning_evidence": True,
}


class TestHappyPath:
    """A clean, fully admissible run passes every enforceable check (exit 0)."""

    def test_clean_run_passes(self, tmp_path):
        _write_run(tmp_path, build_run())
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "[FAIL]" not in r.stdout

    def test_pipeline_passes_and_hands_off(self, tmp_path):
        _write_run(tmp_path, build_run())
        r = _run(tmp_path, "--pipeline")
        assert r.returncode == 0, r.stdout + r.stderr
        assert "HANDOFF" in r.stdout
        assert "semantic review" in r.stdout.lower()


class TestRoleSeparation:
    def test_author_cannot_review_or_vote_on_own_claim(self, tmp_path):
        run = build_run()
        # researcher-1 authored the claim; make it also cast review-1's vote.
        run["review-1"]["reviewer"] = "researcher-1"
        run["vote-1"]["reviewer"] = "researcher-1"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "role-separation" in r.stdout
        assert "researcher-1" in r.stdout


class TestEvidenceIndependence:
    def test_copied_sources_are_not_independent_evidence(self, tmp_path):
        run = build_run()
        # src-B is now a copy of src-A's family: repetition, not corroboration.
        run["source-B"]["source_family"] = "family-1"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "source-family-independence" in r.stdout


class TestTestOutcomes:
    def test_failed_severe_test_blocks_survival(self, tmp_path):
        run = build_run()
        run["test-CLAIM-0001-q2"]["outcome"] = "REFUTED"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "REFUTED" in r.stdout

    def test_invalid_test_does_not_support_a_claim(self, tmp_path):
        run = build_run()
        # The only record for planned test q2 is invalid, so a planned test was
        # never validly run.
        run["test-CLAIM-0001-q2"]["outcome"] = "INVALID_TEST"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "INVALID_TEST" in r.stdout


class TestClaimVersioning:
    def test_changed_claim_invalidates_prior_reviews_and_votes(self, tmp_path):
        run = build_run()
        # The conjecture was revised: new content hash. Prior reviews and votes
        # still reference the old hash and must no longer count.
        run["conjecture-CLAIM-0001"]["content_hash"] = _HASH_B
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "claim-admission" in r.stdout

    def test_new_assumption_starts_a_new_review_cycle(self, tmp_path):
        run = build_run()
        # Adding an assumption is a semantic change -> new hash. Old reviews and
        # votes (old hash) drop out; no current review or vote remains.
        run["conjecture-CLAIM-0001"]["assumptions"].append("no seasonal effect")
        run["conjecture-CLAIM-0001"]["content_hash"] = _HASH_B
        for stem in ("review-1", "review-2", "review-3"):
            run[stem]["claim_hash"] = _HASH_A  # still on the old version
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "claim-admission" in r.stdout


class TestVoteTally:
    def test_a_tie_does_not_produce_survival(self, tmp_path):
        run = build_run()
        # Two SURVIVE, two REFUTE: a tie of decisive votes is not a majority.
        run["review-4"] = {
            "review_id": "REV-4",
            "claim_id": "CLAIM-0001",
            "reviewer": "reviewer-4",
            "claim_hash": _HASH_A,
            "checks": _CHECKS,
            "defect_level": "NOTE",
        }
        run["vote-2"]["value"] = "REFUTE"
        run["vote-4"] = {
            "review_ref": "REV-4",
            "claim_hash": _HASH_A,
            "reviewer": "reviewer-4",
            "value": "REFUTE",
        }
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "strict majority" in r.stdout

    def test_abstentions_do_not_create_a_majority(self, tmp_path):
        run = build_run()
        # One SURVIVE, two ABSTAIN: only one decisive vote — quorum unmet, the
        # abstentions cannot be counted to manufacture a majority.
        run["vote-2"]["value"] = "ABSTAIN"
        run["vote-3"]["value"] = "ABSTAIN"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "quorum" in r.stdout


class TestBlocker:
    def test_a_blocker_prevents_survival(self, tmp_path):
        run = build_run()
        run["review-2"]["defect_level"] = "BLOCKER"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "BLOCKER" in r.stdout


class TestReportStage:
    def test_refuted_or_unresolved_claim_cannot_enter_report_as_fact(self, tmp_path):
        run = build_run()
        # Move the claim to unresolved; the report still cites it as a finding.
        register = run["claim-register"]
        register["unresolved_claims"] = [{"claim_id": "CLAIM-0001"}]
        register["surviving_claims"] = []
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "report-traceability" in r.stdout
        assert "refuted/unresolved" in r.stdout

    def test_unsupported_report_statement_fails_validation(self, tmp_path):
        run = build_run()
        # The finding cites a claim that is nowhere in the register.
        run["final-report"]["findings"][0]["surviving_claim_refs"] = ["CLAIM-0099"]
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "unsupported report statement" in r.stdout

    def test_failed_tests_remain_visible(self, tmp_path):
        run = build_run()
        # The register hides the inconclusive test T2 from failed_tests.
        run["claim-register"]["surviving_claims"][0]["failed_tests"] = []
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "register-integrity" in r.stdout
        assert "T2" in r.stdout

    def test_required_qualifications_remain(self, tmp_path):
        run = build_run()
        # The register drops the conjecture's material qualification.
        run["claim-register"]["surviving_claims"][0]["qualifications"] = []
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "qualification" in r.stdout


class TestPipelineStaging:
    def test_pipeline_stops_at_schema_stage_on_malformed_artifact(self, tmp_path):
        run = build_run()
        # Break the conjecture's content_hash pattern: schema stage must catch it
        # and the run must never reach policy validation.
        run["conjecture-CLAIM-0001"]["content_hash"] = "not-a-valid-hash"
        _write_run(tmp_path, run)
        r = _run(tmp_path, "--pipeline")
        assert r.returncode != 0
        assert "schema" in r.stdout
        assert "stopped at schema stage" in r.stdout

    def test_pipeline_reaches_policy_stage_when_schema_passes(self, tmp_path):
        run = build_run()
        run["review-2"]["defect_level"] = "BLOCKER"  # a policy failure, not schema
        _write_run(tmp_path, run)
        r = _run(tmp_path, "--pipeline")
        assert r.returncode != 0
        assert "stopped at policy stage" in r.stdout


class TestReferenceIntegrity:
    def test_vote_referencing_unknown_review_fails(self, tmp_path):
        run = build_run()
        run["vote-1"]["review_ref"] = "REV-NONE"
        _write_run(tmp_path, run)
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "reference-integrity" in r.stdout


def test_baseline_is_deep_copied_between_tests():
    """Guard: build_run returns a fresh tree so mutations don't leak."""
    a = build_run()
    b = build_run()
    a["conjecture-CLAIM-0001"]["claim_id"] = "MUTATED"
    assert b["conjecture-CLAIM-0001"]["claim_id"] == "CLAIM-0001"
    # copy is imported for callers that need to branch a run mid-test.
    assert copy.deepcopy(b) is not b
