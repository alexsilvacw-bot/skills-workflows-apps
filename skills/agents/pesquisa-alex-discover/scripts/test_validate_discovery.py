#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validate_discovery import validate


class DiscoveryValidatorTests(unittest.TestCase):
    def make_package(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        discovery = Path(temporary.name)
        corpus = discovery / "corpus"
        corpus.mkdir()
        source_text = "Evidence for candidate one.\n"
        (corpus / "s1.txt").write_text(source_text, encoding="utf-8")

        config = {
            "topic": "Example market",
            "geography": "Brazil",
            "current_date": "2026-07-18",
            "eligibility": "Recorded rule",
            "required_capabilities": ["CAP01"],
            "budget_mode": "adaptive",
            "corpus_revision": 1,
            "budget": {
                "max_queries": 1,
                "max_pages_opened": 1,
                "max_elapsed_minutes": 10,
            },
            "minimum_retained_candidates": 1,
            "saturation_reached": True,
            "discovery_status": "saturated",
        }
        (discovery / "run-config.json").write_text(
            json.dumps(config), encoding="utf-8"
        )
        query = {
            "query_id": "Q01",
            "iteration_id": "R01",
            "query_family": "broad_category",
            "query": "example candidate",
            "searched_at": "2026-07-18T10:00:00-03:00",
            "result_urls_considered": ["https://example.com/c1"],
            "urls_opened": ["https://example.com/c1"],
            "new_candidate_ids": ["C01"],
        }
        (discovery / "search-log.jsonl").write_text(
            json.dumps(query) + "\n", encoding="utf-8"
        )
        candidates = {
            "status": "saturated",
            "saturation_reached": True,
            "candidates": [
                {
                    "candidate_id": "C01",
                    "name": "Candidate One",
                    "normalized_name": "Candidate One",
                    "classification": "direct",
                    "rationale": "Supported candidate",
                    "source_ids": ["S01"],
                }
            ],
        }
        (discovery / "candidates.json").write_text(
            json.dumps(candidates), encoding="utf-8"
        )
        coverage = {
            "candidates": [
                {
                    "candidate_id": "C01",
                    "capabilities": {
                        "CAP01": {"status": "supported", "source_ids": ["S01"]}
                    },
                }
            ]
        }
        (discovery / "coverage.json").write_text(
            json.dumps(coverage), encoding="utf-8"
        )
        manifest = {
            "sources": [
                {
                    "source_id": "S01",
                    "title": "Candidate page",
                    "publisher": "Example",
                    "url": "https://example.com/c1",
                    "source_type": "official",
                    "candidate_ids": ["C01"],
                    "coverage": ["CAP01"],
                    "accessed_at": "2026-07-18T10:00:00-03:00",
                    "acquisition_status": "acquired",
                    "local_path": "s1.txt",
                    "sha256": hashlib.sha256(source_text.encode()).hexdigest(),
                    "corpus_revision": 1,
                }
            ]
        }
        (discovery / "source-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (discovery / "discovery-summary.md").write_text(
            "# Discovery summary\n", encoding="utf-8"
        )
        return discovery

    def test_saturated_package_is_ready(self) -> None:
        result = validate(self.make_package())
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["handoff_ready"])

    def test_logged_candidate_cannot_disappear(self) -> None:
        discovery = self.make_package()
        log_path = discovery / "search-log.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8"))
        entry["new_candidate_ids"].append("C02")
        log_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        result = validate(discovery)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(
            any("C02" in error and "missing from the register" in error for error in result["errors"])
        )

    def test_recall_limited_package_is_not_ready_without_acceptance(self) -> None:
        discovery = self.make_package()
        config_path = discovery / "run-config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["saturation_reached"] = False
        config["discovery_status"] = "recall_limited"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        result = validate(discovery)
        self.assertEqual(result["status"], "passed")
        self.assertFalse(result["handoff_ready"])
        self.assertTrue(result["handoff_blockers"])

    def test_inconclusive_candidate_is_retained_without_acquired_support(self) -> None:
        discovery = self.make_package()
        candidates_path = discovery / "candidates.json"
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
        candidates["candidates"][0]["classification"] = "inconclusive"
        candidates["candidates"][0]["source_ids"] = []
        candidates_path.write_text(json.dumps(candidates), encoding="utf-8")
        coverage_path = discovery / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["candidates"][0]["capabilities"]["CAP01"] = {
            "status": "inconclusive",
            "source_ids": [],
        }
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        result = validate(discovery)
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["handoff_ready"])
        self.assertEqual(result["counts"]["retained_candidates"], 1)

    def test_recorded_budget_extension_allows_continued_search(self) -> None:
        discovery = self.make_package()
        config_path = discovery / "run-config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["budget_extensions"] = [
            {
                "new_max_queries": 2,
                "new_max_pages_opened": 2,
                "new_max_elapsed_minutes": 10,
                "reason": "Candidate expansion had not saturated",
                "extended_at": "2026-07-18T10:05:00-03:00",
                "authorized_by": "workflow:auto",
            }
        ]
        config_path.write_text(json.dumps(config), encoding="utf-8")
        second_query = {
            "query_id": "Q02",
            "iteration_id": "R01",
            "query_family": "candidate_expansion",
            "query": "another expansion query",
            "searched_at": "2026-07-18T10:06:00-03:00",
            "result_urls_considered": ["https://example.com/c2"],
            "urls_opened": ["https://example.com/c2"],
            "new_candidate_ids": [],
        }
        with (discovery / "search-log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(second_query) + "\n")
        result = validate(discovery)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["effective_budget"]["max_queries"], 2)


if __name__ == "__main__":
    unittest.main()
