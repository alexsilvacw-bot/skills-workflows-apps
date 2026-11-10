#!/usr/bin/env python3

from __future__ import annotations

import unittest

from validate_research import validate_execution_handoff, validate_intent_audit


def valid_audit() -> dict:
    interpretation = {
        "objective": "Understand the issue",
        "audience": "Decision group",
        "expected_outcome": "Support a decision",
        "time_horizon": "This quarter",
    }
    return {
        "workflow": "pesquisa-alex",
        "intent_audit": {
            "status": "confirmed",
            "initial_interpretation": dict(interpretation),
            "confirmed_interpretation": dict(interpretation),
            "misalignments": [],
        },
    }


class IntentAuditTests(unittest.TestCase):
    def test_confirmed_four_point_audit_is_valid(self) -> None:
        self.assertEqual(validate_intent_audit(valid_audit()), [])

    def test_new_workflow_cannot_skip_confirmation(self) -> None:
        outline = valid_audit()
        outline["intent_audit"]["status"] = "pending"
        self.assertTrue(validate_intent_audit(outline))

    def test_misalignment_requires_cause_and_counterfactual(self) -> None:
        outline = valid_audit()
        outline["intent_audit"]["misalignments"] = [
            {
                "point": "audience",
                "initial_reading": "General public",
                "correction": "Technical reviewers",
            }
        ]
        errors = validate_intent_audit(outline)
        self.assertTrue(any("cause" in error for error in errors))
        self.assertTrue(any("counterfactual" in error for error in errors))

    def test_legacy_artifacts_remain_compatible(self) -> None:
        self.assertEqual(validate_intent_audit({"topic": "Legacy research"}), [])


class ExecutionHandoffTests(unittest.TestCase):
    def test_current_environment_must_be_explicit(self) -> None:
        outline = {
            "workflow": "pesquisa-alex",
            "execution_handoff": {
                "status": "confirmed",
                "mode": "current_environment",
                "executor": "Current environment",
                "surface": "Application",
                "package_path": None,
            },
        }
        self.assertEqual(validate_execution_handoff(outline), [])

    def test_external_executor_requires_ready_package(self) -> None:
        outline = {
            "workflow": "pesquisa-alex",
            "execution_handoff": {
                "status": "confirmed",
                "mode": "external_executor",
                "executor": "External environment",
                "surface": "Application",
            },
        }
        errors = validate_execution_handoff(outline)
        self.assertTrue(any("status ready" in error for error in errors))
        self.assertTrue(any("package_path" in error for error in errors))

    def test_external_ready_package_is_valid(self) -> None:
        outline = {
            "workflow": "pesquisa-alex",
            "execution_handoff": {
                "status": "ready",
                "mode": "external_executor",
                "executor": "External environment",
                "surface": "CLI",
                "package_path": "./handoff",
                "manifest_path": "./handoff/handoff-manifest.json",
                "first_pending_phase": "deep",
            },
        }
        self.assertEqual(validate_execution_handoff(outline), [])

    def test_claude_cli_requires_user_confirmed_model(self) -> None:
        outline = {
            "workflow": "pesquisa-alex",
            "execution_handoff": {
                "status": "ready",
                "mode": "external_executor",
                "executor": "Claude",
                "surface": "Claude CLI",
                "package_path": "./handoff",
                "manifest_path": "./handoff/handoff-manifest.json",
                "first_pending_phase": "deep",
            },
        }
        errors = validate_execution_handoff(outline)
        self.assertTrue(any("model is required for Claude CLI" in error for error in errors))

    def test_claude_cli_with_confirmed_model_is_valid(self) -> None:
        outline = {
            "workflow": "pesquisa-alex",
            "execution_handoff": {
                "status": "ready",
                "mode": "external_executor",
                "executor": "Claude",
                "surface": "Claude CLI",
                "model": "User-confirmed Claude model",
                "package_path": "./handoff",
                "manifest_path": "./handoff/handoff-manifest.json",
                "first_pending_phase": "deep",
            },
        }
        self.assertEqual(validate_execution_handoff(outline), [])


if __name__ == "__main__":
    unittest.main()
