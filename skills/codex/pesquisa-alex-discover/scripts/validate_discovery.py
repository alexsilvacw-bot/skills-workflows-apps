#!/usr/bin/env python3
"""Validate a Pesquisa Alex discovery package.

This checks reproducibility and internal consistency. It does not judge relevance,
semantic support, publisher authority, or truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


CLASSIFICATIONS = {"direct", "adjacent", "inconclusive", "excluded"}
RETAINED_CLASSIFICATIONS = {"direct", "adjacent", "inconclusive"}
COVERAGE_STATES = {"supported", "not_found", "not_searched", "inconclusive"}
SOURCE_TYPES = {"official", "independent", "regulatory", "other"}
ACQUIRED_STATES = {"acquired", "partial"}
FAILED_STATES = {"blocked", "failed", "inaccessible", "snippet_only"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_corpus_path(corpus: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = (corpus / value).resolve()
    try:
        candidate.relative_to(corpus.resolve())
    except ValueError:
        return None
    return candidate


def effective_budget(config: dict[str, Any], errors: list[str]) -> dict[str, int]:
    """Return the latest explicitly recorded navigation limits."""
    budget = config.get("budget", {})
    keys = ("max_queries", "max_pages_opened", "max_elapsed_minutes")
    current: dict[str, int] = {}
    for key in keys:
        value = budget.get(key) if isinstance(budget, dict) else None
        if not isinstance(value, int) or value < 1:
            errors.append(f"run-config.json: budget.{key} must be a positive integer")
        else:
            current[key] = value

    extensions = config.get("budget_extensions", [])
    if not isinstance(extensions, list):
        errors.append("run-config.json: budget_extensions must be an array")
        return current
    for index, extension in enumerate(extensions, 1):
        prefix = f"run-config.json: budget extension #{index}"
        if not isinstance(extension, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("reason", "extended_at", "authorized_by"):
            if not nonempty(extension.get(field)):
                errors.append(f"{prefix}: missing {field}")
        for key in keys:
            extension_key = f"new_{key}"
            value = extension.get(extension_key)
            if not isinstance(value, int) or value < current.get(key, 1):
                errors.append(f"{prefix}: {extension_key} must be an integer no smaller than the previous limit")
            else:
                current[key] = value
    return current


def validate(discovery: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = {
        "run-config.json",
        "search-log.jsonl",
        "candidates.json",
        "coverage.json",
        "source-manifest.json",
        "discovery-summary.md",
    }
    for name in sorted(required):
        if not (discovery / name).is_file():
            errors.append(f"missing {name}")
    corpus = discovery / "corpus"
    if not corpus.is_dir():
        errors.append("missing corpus directory")

    if errors:
        return {"status": "failed", "errors": errors, "warnings": warnings}

    config = load_json(discovery / "run-config.json")
    if not isinstance(config, dict):
        errors.append("run-config.json must contain an object")
        config = {}
    for key in ("topic", "geography", "current_date", "eligibility", "required_capabilities", "budget"):
        if not nonempty(config.get(key)):
            errors.append(f"run-config.json: missing {key}")
    budget_mode = config.get("budget_mode")
    if budget_mode not in {"adaptive", "hard"}:
        errors.append("run-config.json: budget_mode must be adaptive or hard")
    corpus_revision = config.get("corpus_revision")
    if not isinstance(corpus_revision, int) or corpus_revision < 1:
        errors.append("run-config.json: corpus_revision must be a positive integer")
    budget = effective_budget(config, errors)
    minimum_retained = config.get("minimum_retained_candidates", 0)
    if not isinstance(minimum_retained, int) or minimum_retained < 0:
        errors.append("run-config.json: minimum_retained_candidates must be a non-negative integer")
        minimum_retained = 0

    query_ids: set[str] = set()
    logged_candidate_ids: set[str] = set()
    query_count = 0
    opened_urls: set[str] = set()
    with (discovery / "search-log.jsonl").open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            query_count += 1
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"search-log.jsonl:{line_number}: invalid JSON: {exc.msg}")
                continue
            query_id = entry.get("query_id")
            if not nonempty(query_id):
                errors.append(f"search-log.jsonl:{line_number}: missing query_id")
            elif query_id in query_ids:
                errors.append(f"search-log.jsonl:{line_number}: duplicate query_id {query_id}")
            else:
                query_ids.add(query_id)
            for key in ("iteration_id", "query", "searched_at", "result_urls_considered", "urls_opened"):
                if key not in entry:
                    errors.append(f"search-log.jsonl:{line_number}: missing {key}")
            new_candidate_ids = entry.get("new_candidate_ids", [])
            if not isinstance(new_candidate_ids, list) or any(not nonempty(value) for value in new_candidate_ids):
                errors.append(f"search-log.jsonl:{line_number}: new_candidate_ids must be an array of IDs")
            else:
                logged_candidate_ids.update(new_candidate_ids)
            for url in entry.get("result_urls_considered", []) + entry.get("urls_opened", []):
                if not valid_url(url):
                    errors.append(f"search-log.jsonl:{line_number}: invalid URL {url!r}")
            opened_urls.update(entry.get("urls_opened", []))
    if query_count == 0:
        errors.append("search-log.jsonl: no queries")
    if query_count > budget.get("max_queries", query_count):
        errors.append("search log exceeds max_queries")
    if len(opened_urls) > budget.get("max_pages_opened", len(opened_urls)):
        errors.append("search log exceeds max_pages_opened")

    candidates_data = load_json(discovery / "candidates.json")
    candidates = candidates_data.get("candidates", []) if isinstance(candidates_data, dict) else []
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidates.json: candidates must be a non-empty array")
        candidates = []
    candidate_ids: set[str] = set()
    for index, candidate in enumerate(candidates, 1):
        prefix = f"candidates.json: candidate #{index}"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix} must be an object")
            continue
        candidate_id = candidate.get("candidate_id")
        if not nonempty(candidate_id):
            errors.append(f"{prefix}: missing candidate_id")
        elif candidate_id in candidate_ids:
            errors.append(f"{prefix}: duplicate candidate_id {candidate_id}")
        else:
            candidate_ids.add(candidate_id)
        for key in ("name", "normalized_name", "classification", "rationale"):
            if not nonempty(candidate.get(key)):
                errors.append(f"{prefix}: missing {key}")
        if candidate.get("classification") not in CLASSIFICATIONS:
            errors.append(f"{prefix}: invalid classification")
        source_ids_value = candidate.get("source_ids")
        if not isinstance(source_ids_value, list):
            errors.append(f"{prefix}: source_ids must be an array")
        elif candidate.get("classification") in {"direct", "adjacent"} and not source_ids_value:
            errors.append(f"{prefix}: retained confirmed candidate requires at least one source_id")

    missing_logged_candidates = logged_candidate_ids - candidate_ids
    if missing_logged_candidates:
        errors.append(
            "candidates.json: logged candidate IDs are missing from the register "
            f"{sorted(missing_logged_candidates)}"
        )

    manifest_data = load_json(discovery / "source-manifest.json")
    sources = manifest_data.get("sources", []) if isinstance(manifest_data, dict) else []
    if not isinstance(sources, list) or not sources:
        errors.append("source-manifest.json: sources must be a non-empty array")
        sources = []
    source_ids: set[str] = set()
    acquired_count = 0
    for index, source in enumerate(sources, 1):
        prefix = f"source-manifest.json: source #{index}"
        if not isinstance(source, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source_id = source.get("source_id")
        if not nonempty(source_id):
            errors.append(f"{prefix}: missing source_id")
        elif source_id in source_ids:
            errors.append(f"{prefix}: duplicate source_id {source_id}")
        else:
            source_ids.add(source_id)
        for key in ("title", "publisher", "url", "source_type", "candidate_ids", "coverage", "accessed_at", "acquisition_status", "corpus_revision"):
            if not nonempty(source.get(key)):
                errors.append(f"{prefix}: missing {key}")
        if not valid_url(source.get("url")):
            errors.append(f"{prefix}: invalid url")
        if source.get("final_url") and not valid_url(source.get("final_url")):
            errors.append(f"{prefix}: invalid final_url")
        if source.get("source_type") not in SOURCE_TYPES:
            errors.append(f"{prefix}: invalid source_type")
        unknown_candidates = set(source.get("candidate_ids", [])) - candidate_ids
        if unknown_candidates:
            errors.append(f"{prefix}: unknown candidate IDs {sorted(unknown_candidates)}")
        status = source.get("acquisition_status")
        local_path = safe_corpus_path(corpus, source.get("local_path"))
        if status in ACQUIRED_STATES:
            acquired_count += 1
            if local_path is None or not local_path.is_file():
                errors.append(f"{prefix}: acquired source lacks a valid corpus file")
            elif source.get("sha256") != sha256(local_path):
                errors.append(f"{prefix}: SHA-256 mismatch")
            if (source.get("final_url") or source.get("url")) not in opened_urls:
                warnings.append(f"{prefix}: acquired URL is not present in urls_opened")
        elif status in FAILED_STATES:
            if source.get("local_path") or source.get("sha256"):
                errors.append(f"{prefix}: failed source must not claim a snapshot or hash")
            if not nonempty(source.get("limitations")):
                errors.append(f"{prefix}: failed source lacks limitations")
        else:
            errors.append(f"{prefix}: invalid acquisition_status {status!r}")

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_source_ids = candidate.get("source_ids", [])
        if not isinstance(candidate_source_ids, list):
            candidate_source_ids = []
        unknown_sources = set(candidate_source_ids) - source_ids
        if unknown_sources:
            errors.append(f"candidate {candidate.get('candidate_id')}: unknown source IDs {sorted(unknown_sources)}")

    coverage_data = load_json(discovery / "coverage.json")
    rows = coverage_data.get("candidates", []) if isinstance(coverage_data, dict) else []
    if not isinstance(rows, list):
        errors.append("coverage.json: candidates must be an array")
        rows = []
    covered_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("coverage.json: candidate row must be an object")
            continue
        candidate_id = row.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"coverage.json: unknown candidate_id {candidate_id}")
        covered_ids.add(candidate_id)
        capabilities = row.get("capabilities")
        if not isinstance(capabilities, dict):
            errors.append(f"coverage.json: {candidate_id} capabilities must be an object")
            continue
        for capability in config.get("required_capabilities", []):
            cell = capabilities.get(capability)
            if not isinstance(cell, dict) or cell.get("status") not in COVERAGE_STATES:
                errors.append(f"coverage.json: {candidate_id}.{capability} has invalid or missing status")
            elif set(cell.get("source_ids", [])) - source_ids:
                errors.append(f"coverage.json: {candidate_id}.{capability} references unknown sources")
    missing_rows = candidate_ids - covered_ids
    if missing_rows:
        errors.append(f"coverage.json: missing candidates {sorted(missing_rows)}")

    retained_count = sum(
        1
        for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("classification") in RETAINED_CLASSIFICATIONS
    )
    saturation_reached = config.get("saturation_reached") is True
    recall_acceptance = config.get("recall_limit_acceptance")
    recall_accepted = False
    if isinstance(recall_acceptance, dict):
        required_acceptance = ("accepted_by", "accepted_at", "reason")
        recall_accepted = all(nonempty(recall_acceptance.get(key)) for key in required_acceptance)
        if not recall_accepted:
            errors.append("run-config.json: recall_limit_acceptance is incomplete")

    handoff_blockers: list[str] = []
    if not saturation_reached and not recall_accepted:
        handoff_blockers.append("discovery is not saturated and recall limitation was not explicitly accepted")
    if retained_count < minimum_retained:
        handoff_blockers.append(
            f"retained candidates {retained_count} are below the predeclared minimum {minimum_retained}"
        )

    status = "passed" if not errors else "failed"
    handoff_ready = status == "passed" and not handoff_blockers
    return {
        "status": status,
        "validator_scope": "structural references, paths, hashes, URLs, candidate retention, budget revisions, and handoff gates only",
        "truth_or_relevance_verified": False,
        "budget_mode": budget_mode,
        "effective_budget": budget,
        "handoff_ready": handoff_ready,
        "handoff_blockers": handoff_blockers,
        "counts": {
            "queries": query_count,
            "unique_pages_opened": len(opened_urls),
            "candidates": len(candidate_ids),
            "logged_candidate_ids": len(logged_candidate_ids),
            "retained_candidates": retained_count,
            "sources": len(source_ids),
            "acquired_sources": acquired_count,
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    discovery = args.discovery.resolve()
    summary = validate(discovery)
    if args.write:
        output = discovery / "validation-summary.json"
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
