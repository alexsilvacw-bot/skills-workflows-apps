#!/usr/bin/env python3

from __future__ import annotations

import unittest

from validate_research import validate_reporting_config


class ReportingConfigTests(unittest.TestCase):
    def test_all_domain_neutral_modes_are_valid(self) -> None:
        for mode in (
            "auto",
            "choice",
            "landscape",
            "diagnostic",
            "evidence_synthesis",
            "assessment",
            "descriptive",
            "custom",
        ):
            config = {
                "audience": "Intended reader",
                "primary_use": "Understand the research answer",
                "report_mode": mode,
                "detail_level": "standard",
                "item_dossier": "auto",
            }
            self.assertEqual(validate_reporting_config(config), [])

    def test_mixed_modes_are_valid(self) -> None:
        config = {
            "audience": "Technical review group",
            "primary_use": "Explain evidence and assess alternatives",
            "report_mode": ["diagnostic", "assessment"],
            "detail_level": "detailed",
            "item_dossier": True,
        }
        self.assertEqual(validate_reporting_config(config), [])

    def test_domain_specific_unknown_mode_is_rejected(self) -> None:
        config = {
            "audience": "Reader",
            "primary_use": "Use the report",
            "report_mode": "domain_specific_template",
            "detail_level": "standard",
            "item_dossier": "auto",
        }
        self.assertTrue(validate_reporting_config(config))

    def test_missing_reader_context_is_rejected(self) -> None:
        config = {
            "report_mode": "descriptive",
            "detail_level": "standard",
            "item_dossier": False,
        }
        errors = validate_reporting_config(config)
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
