import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from validate_semantic_differential import validate_log  # noqa: E402


class SemanticDifferentialValidationTests(unittest.TestCase):
    def test_all_expected_passing_properties_are_accepted(self):
        text = "\n".join(
            [
                "echidna_same_caller_trace_is_equivalent: passing",
                "echidna_caller_alternation_changes_behavior: passing",
                "echidna_rollback_boundary_changes_behavior: passing",
            ]
        )
        result = validate_log(text)
        self.assertTrue(result["all_passed"])
        self.assertEqual(len(result["passed_properties"]), 3)

    def test_missing_property_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing expected"):
            validate_log(
                "echidna_same_caller_trace_is_equivalent: passing\n"
            )

    def test_failed_property_is_rejected(self):
        text = "\n".join(
            [
                "echidna_same_caller_trace_is_equivalent: passing",
                "echidna_caller_alternation_changes_behavior: failed",
                "echidna_rollback_boundary_changes_behavior: passing",
            ]
        )
        with self.assertRaisesRegex(ValueError, "failed"):
            validate_log(text)


if __name__ == "__main__":
    unittest.main()
