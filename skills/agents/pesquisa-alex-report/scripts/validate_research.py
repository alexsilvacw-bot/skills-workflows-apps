#!/usr/bin/env python3
"""Validate Pesquisa Alex artifacts without making truth claims."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

ABSENCE_STATES = {"not_found", "not_searched", "not_applicable", "inconclusive"}
CLAIM_ROLES = {"answer", "premise", "counterevidence", "context"}
SEMANTIC_STATES = {
    "full",
    "partial",
    "irrelevant",
    "contradicted",
    "inconclusive",
    "unreviewed",
}
REPORT_MODES = {
    "auto",
    "choice",
    "landscape",
    "diagnostic",
    "evidence_synthesis",
    "assessment",
    "descriptive",
    "custom",
}
REPORT_DETAIL_LEVELS = {"executive", "standard", "detailed"}
INTENT_POINTS = {"objective", "audience", "expected_outcome", "time_horizon"}
EXECUTION_MODES = {"current_environment", "external_executor"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip() != "[uncertain]"
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def normalize_quote(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def validate_reporting_config(reporting: Any) -> list[str]:
    if reporting is None:
        return []
    if not isinstance(reporting, dict):
        return ["outline.reporting must be an object"]
    config_errors: list[str] = []
    for key in ("audience", "primary_use"):
        if not nonempty(reporting.get(key)):
            config_errors.append(f"outline.reporting.{key} is required")
    modes = reporting.get("report_mode", "auto")
    if isinstance(modes, str):
        modes = [modes]
    if (
        not isinstance(modes, list)
        or not modes
        or any(not isinstance(mode, str) or mode not in REPORT_MODES for mode in modes)
    ):
        config_errors.append(
            "outline.reporting.report_mode must be a supported mode or non-empty list of modes"
        )
    detail_level = reporting.get("detail_level", "standard")
    if not isinstance(detail_level, str) or detail_level not in REPORT_DETAIL_LEVELS:
        config_errors.append(
            "outline.reporting.detail_level must be executive, standard, or detailed"
        )
    item_dossier = reporting.get("item_dossier", "auto")
    if item_dossier != "auto" and not isinstance(item_dossier, bool):
        config_errors.append(
            "outline.reporting.item_dossier must be auto, true, or false"
        )
    return config_errors


def validate_intent_audit(outline: dict[str, Any]) -> list[str]:
    """Require the confirmation gate for artifacts created by Pesquisa Alex."""
    if outline.get("workflow") != "pesquisa-alex":
        return []
    audit = outline.get("intent_audit")
    if not isinstance(audit, dict):
        return ["outline.intent_audit is required for workflow pesquisa-alex"]
    audit_errors: list[str] = []
    if audit.get("status") != "confirmed":
        audit_errors.append("outline.intent_audit.status must be confirmed")
    for section in ("initial_interpretation", "confirmed_interpretation"):
        values = audit.get(section)
        if not isinstance(values, dict):
            audit_errors.append(f"outline.intent_audit.{section} must be an object")
            continue
        for point in sorted(INTENT_POINTS):
            if not nonempty(values.get(point)):
                audit_errors.append(
                    f"outline.intent_audit.{section}.{point} is required"
                )
    misalignments = audit.get("misalignments", [])
    if not isinstance(misalignments, list):
        audit_errors.append("outline.intent_audit.misalignments must be an array")
    else:
        for index, entry in enumerate(misalignments):
            prefix = f"outline.intent_audit.misalignments[{index}]"
            if not isinstance(entry, dict):
                audit_errors.append(f"{prefix} must be an object")
                continue
            if entry.get("point") not in INTENT_POINTS:
                audit_errors.append(f"{prefix}.point is invalid")
            for key in ("initial_reading", "correction", "cause", "counterfactual"):
                if not nonempty(entry.get(key)):
                    audit_errors.append(f"{prefix}.{key} is required")
    return audit_errors


def uses_claude_cli(handoff: dict[str, Any]) -> bool:
    """Detect the Claude CLI surface without hard-coding it as the only executor."""
    destination = " ".join(
        str(handoff.get(key, "")) for key in ("executor", "surface")
    ).casefold()
    return "claude" in destination and ("cli" in destination or "command line" in destination)


def validate_execution_handoff(outline: dict[str, Any]) -> list[str]:
    """Require an explicit execution destination for Pesquisa Alex artifacts."""
    if outline.get("workflow") != "pesquisa-alex":
        return []
    handoff = outline.get("execution_handoff")
    if not isinstance(handoff, dict):
        return ["outline.execution_handoff is required for workflow pesquisa-alex"]
    handoff_errors: list[str] = []
    mode = handoff.get("mode")
    if mode not in EXECUTION_MODES:
        handoff_errors.append("outline.execution_handoff.mode is invalid")
    if handoff.get("status") not in {"confirmed", "ready"}:
        handoff_errors.append(
            "outline.execution_handoff.status must be confirmed or ready"
        )
    for key in ("executor", "surface"):
        if not nonempty(handoff.get(key)):
            handoff_errors.append(f"outline.execution_handoff.{key} is required")
    if uses_claude_cli(handoff) and not nonempty(handoff.get("model")):
        handoff_errors.append(
            "outline.execution_handoff.model is required for Claude CLI"
        )
    if mode == "external_executor":
        if handoff.get("status") != "ready":
            handoff_errors.append(
                "external execution requires outline.execution_handoff.status ready"
            )
        for key in ("package_path", "manifest_path", "first_pending_phase"):
            if not nonempty(handoff.get(key)):
                handoff_errors.append(f"outline.execution_handoff.{key} is required")
        if handoff.get("first_pending_phase") not in {None, "deep"}:
            handoff_errors.append(
                "outline.execution_handoff.first_pending_phase must be deep"
            )
    return handoff_errors


def field_specs(fields: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    categories = fields.get("field_categories", [])
    if isinstance(categories, dict):
        categories = [
            {"category": name, **(body if isinstance(body, dict) else {})}
            for name, body in categories.items()
        ]
    for category in categories if isinstance(categories, list) else []:
        if not isinstance(category, dict):
            continue
        for spec in category.get("fields", []) or []:
            if isinstance(spec, dict) and nonempty(spec.get("name")):
                specs.append(spec)
    return specs


def corpus_file(corpus: Path, source_path: Any) -> Path | None:
    if not isinstance(source_path, str) or not source_path.strip():
        return None
    candidate = (corpus / source_path).resolve()
    try:
        candidate.relative_to(corpus.resolve())
    except ValueError:
        return None
    return candidate


def validate(
    outline: dict[str, Any],
    fields: dict[str, Any],
    result_paths: list[Path],
    corpus: Path,
    write: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(validate_intent_audit(outline))
    errors.extend(validate_execution_handoff(outline))
    errors.extend(validate_reporting_config(outline.get("reporting")))
    question_ids = {
        q.get("question_id")
        for q in outline.get("decision_questions", [])
        if isinstance(q, dict) and nonempty(q.get("question_id"))
    }
    if not question_ids:
        errors.append("outline: no decisive questions")

    required_fields = {
        spec["name"] for spec in field_specs(fields) if spec.get("required") is True
    }
    outline_item_ids = {
        item.get("item_id")
        for item in outline.get("items", [])
        if isinstance(item, dict) and nonempty(item.get("item_id"))
    }
    seen_items: set[str] = set()
    seen_claims: set[str] = set()
    answered_questions: set[str] = set()
    closed_questions: set[str] = set()
    claim_count = 0
    human_reviewed_count = 0
    passed_quote_count = 0
    file_summaries: list[dict[str, Any]] = []

    for result_path in result_paths:
        data = load_json(result_path)
        file_errors: list[str] = []
        item_id = data.get("item_id")
        if not nonempty(item_id):
            file_errors.append("missing item_id")
        elif item_id in seen_items:
            file_errors.append(f"duplicate item_id {item_id}")
        elif outline_item_ids and item_id not in outline_item_ids:
            file_errors.append(f"item_id {item_id} is not present in outline")
        else:
            seen_items.add(item_id)
        if not nonempty(data.get("item_name")):
            file_errors.append("missing item_name")

        values = data.get("fields", {})
        if not isinstance(values, dict):
            file_errors.append("fields must be an object")
            values = {}
        for name in required_fields:
            value = values.get(name)
            explicit_absence = (
                isinstance(value, dict) and value.get("status") in ABSENCE_STATES
            )
            if not nonempty(value) or (isinstance(value, dict) and not explicit_absence):
                file_errors.append(f"required field {name!r} is empty or malformed")

        sources = data.get("sources", [])
        if not isinstance(sources, list):
            file_errors.append("sources must be an array")
            sources = []
        source_map: dict[str, Path] = {}
        for source in sources:
            if not isinstance(source, dict):
                file_errors.append("source entry must be an object")
                continue
            source_id = source.get("source_id")
            path = corpus_file(corpus, source.get("path"))
            if not nonempty(source_id):
                file_errors.append("source missing source_id")
            elif source_id in source_map:
                file_errors.append(f"duplicate source_id {source_id}")
            elif path is None:
                file_errors.append(f"source {source_id}: invalid corpus path")
            elif not path.is_file():
                file_errors.append(f"source {source_id}: file not found in corpus")
            else:
                source_map[source_id] = path

        dispositions = data.get("question_dispositions", [])
        if not isinstance(dispositions, list):
            file_errors.append("question_dispositions must be an array")
            dispositions = []
        for disposition in dispositions:
            if not isinstance(disposition, dict):
                file_errors.append("question disposition must be an object")
                continue
            qid = disposition.get("question_id")
            status = disposition.get("status")
            if qid not in question_ids:
                file_errors.append(f"disposition references unknown question {qid}")
            if status not in ABSENCE_STATES:
                file_errors.append(f"question {qid}: invalid absence status {status}")
            if qid in question_ids and status in ABSENCE_STATES:
                closed_questions.add(qid)

        claims = data.get("critical_claims", [])
        if not isinstance(claims, list):
            file_errors.append("critical_claims must be an array")
            claims = []
        changed = False
        for claim in claims:
            claim_count += 1
            prefix = f"claim #{claim_count}"
            if not isinstance(claim, dict):
                file_errors.append(f"{prefix}: must be an object")
                continue
            claim_id = claim.get("claim_id")
            prefix = f"claim {claim_id or '#'+str(claim_count)}"
            if not nonempty(claim_id):
                file_errors.append(f"{prefix}: missing claim_id")
            elif claim_id in seen_claims:
                file_errors.append(f"{prefix}: duplicate claim_id")
            else:
                seen_claims.add(claim_id)
            if not nonempty(claim.get("claim_text")):
                file_errors.append(f"{prefix}: missing claim_text")
            if claim.get("critical") is not True:
                file_errors.append(f"{prefix}: critical must be true")
            if claim.get("claim_role") not in CLAIM_ROLES:
                file_errors.append(f"{prefix}: invalid claim_role")
            linked_questions = claim.get("decision_question_ids", [])
            if (
                not isinstance(linked_questions, list)
                or not linked_questions
                or any(qid not in question_ids for qid in linked_questions)
            ):
                file_errors.append(f"{prefix}: invalid decisive-question references")
            if claim.get("criticality_source") not in {"brief", "emerging"}:
                file_errors.append(f"{prefix}: invalid criticality_source")
            if (
                claim.get("criticality_source") == "emerging"
                and not nonempty(claim.get("criticality_reason"))
            ):
                file_errors.append(f"{prefix}: emerging claim lacks criticality_reason")
            source_id = claim.get("source_id")
            quote = claim.get("evidence_quote")
            location = claim.get("evidence_location")
            if source_id not in source_map:
                file_errors.append(f"{prefix}: unknown source_id {source_id}")
                quote_passed = False
            elif not isinstance(quote, str) or not normalize_quote(quote):
                file_errors.append(f"{prefix}: missing evidence_quote")
                quote_passed = False
            else:
                source_text = source_map[source_id].read_text(
                    encoding="utf-8", errors="replace"
                )
                quote_passed = normalize_quote(quote) in normalize_quote(source_text)
                if not quote_passed:
                    file_errors.append(f"{prefix}: literal normalized quote not found")
            new_match = "passed" if quote_passed else "failed"
            if claim.get("quote_match") != new_match:
                claim["quote_match"] = new_match
                changed = True
            if quote_passed:
                passed_quote_count += 1
            if not isinstance(location, dict) or not any(
                nonempty(value) for value in location.values()
            ):
                file_errors.append(f"{prefix}: missing recoverable evidence_location")

            semantic = claim.get("semantic_support")
            reviewer = claim.get("reviewed_by")
            if semantic not in SEMANTIC_STATES:
                file_errors.append(f"{prefix}: invalid semantic_support")
            if semantic == "unreviewed":
                if reviewer is not None:
                    file_errors.append(f"{prefix}: unreviewed claim has reviewed_by")
            else:
                if not isinstance(reviewer, dict):
                    file_errors.append(f"{prefix}: reviewed claim lacks reviewed_by")
                else:
                    missing_review = [
                        key
                        for key in ("type", "id", "protocol", "reviewed_at")
                        if not nonempty(reviewer.get(key))
                    ]
                    if reviewer.get("type") not in {"human", "model"}:
                        missing_review.append("valid type")
                    if missing_review:
                        file_errors.append(
                            f"{prefix}: incomplete review ({', '.join(missing_review)})"
                        )
                    elif reviewer.get("type") == "human":
                        human_reviewed_count += 1
            if semantic in {"partial", "inconclusive", "contradicted", "irrelevant"}:
                if not nonempty(claim.get("limitations")):
                    file_errors.append(f"{prefix}: qualified support lacks limitations")
            if semantic in {"contradicted", "irrelevant"} and claim.get(
                "presented_as_established", False
            ):
                file_errors.append(f"{prefix}: invalidly presented as established")
            if (
                claim.get("claim_role") == "answer"
                and semantic in {"full", "partial"}
                and isinstance(linked_questions, list)
            ):
                answered_questions.update(linked_questions)

        if write and changed:
            result_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        errors.extend(f"{result_path.name}: {message}" for message in file_errors)
        file_summaries.append(
            {
                "file": result_path.name,
                "critical_claims": len(claims),
                "valid": not file_errors,
                "errors": file_errors,
            }
        )

    unresolved_questions = sorted(
        question_ids - answered_questions - closed_questions
    )
    missing_result_items = sorted(outline_item_ids - seen_items)
    if missing_result_items:
        errors.append(
            "outline items without result JSON: " + ", ".join(missing_result_items)
        )
    if unresolved_questions:
        errors.append(
            "decisive questions without supported answer or explicit absence: "
            + ", ".join(unresolved_questions)
        )
    if not result_paths:
        errors.append("no result JSON files found")

    # Vacuous success is intentional: a corpus may support no critical claims.
    # Explicitly closed decisive questions can still be decision-ready.
    all_quotes_passed = passed_quote_count == claim_count
    all_human_reviewed = human_reviewed_count == claim_count
    structural_valid = not errors
    decision_ready = (
        structural_valid
        and all_quotes_passed
        and all_human_reviewed
        and not unresolved_questions
    )
    if claim_count == 0:
        warnings.append("no critical claims recorded; decisive questions must use explicit absence")
    return {
        "validator_claim": "structural_validation_and_quote_match_only",
        "truth_verified": False,
        "delivery_status": "decision_ready" if decision_ready else "draft",
        "gates": {
            "structural_valid": structural_valid,
            "all_outline_items_have_results": not missing_result_items,
            "all_critical_quotes_passed": all_quotes_passed,
            "all_critical_claims_human_reviewed": all_human_reviewed,
            "all_decisive_questions_closed": not unresolved_questions,
        },
        "counts": {
            "result_files": len(result_paths),
            "critical_claims": claim_count,
            "quote_match_passed": passed_quote_count,
            "human_reviewed": human_reviewed_count,
        },
        "unresolved_question_ids": unresolved_questions,
        "errors": errors,
        "warnings": warnings,
        "files": file_summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Pesquisa Alex structure and literal quotes"
    )
    parser.add_argument("--outline", type=Path, required=True)
    parser.add_argument("--fields", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write computed quote_match values and validation-summary.json",
    )
    args = parser.parse_args()

    outline = load_yaml(args.outline)
    fields = load_yaml(args.fields)
    corpus_value = args.corpus or Path(outline.get("authorized_corpus", "./corpus"))
    corpus = (
        corpus_value
        if corpus_value.is_absolute()
        else (args.outline.parent / corpus_value)
    ).resolve()
    result_paths = sorted(
        path
        for path in args.results.glob("*.json")
        if path.name != "validation-summary.json"
    )
    summary = validate(outline, fields, result_paths, corpus, args.write)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        args.results.mkdir(parents=True, exist_ok=True)
        (args.results / "validation-summary.json").write_text(
            rendered, encoding="utf-8"
        )
    print(rendered, end="")
    return 0 if summary["gates"]["structural_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
