import unittest

from analyzer.parse_experiment_logs import parse_status


class ParseStatusTests(unittest.TestCase):
    def test_falsified_takes_priority_over_budget_exhausted(self):
        text = """
        Test echidna_property falsified!
        Test limit reached. Stopping.
        echidna_property: failed!
        """

        self.assertEqual(parse_status(text), "falsified")

    def test_passing_with_test_limit_is_budget_exhausted(self):
        text = """
        Test limit reached. Stopping.
        echidna_property: passing
        PUBLIC_C1_RUN_COMPLETED=1
        """

        self.assertEqual(parse_status(text), "budget_exhausted")

    def test_passing_without_test_limit_is_passed(self):
        self.assertEqual(
            parse_status("echidna_property: passing"),
            "passed",
        )

    def test_startup_error_takes_highest_priority(self):
        text = """
        ParserError: invalid source
        Test echidna_property falsified!
        """

        self.assertEqual(parse_status(text), "startup_error")

    def test_unclassified_log_is_incomplete(self):
        self.assertEqual(parse_status("partial log"), "incomplete")

    def test_completion_marker_alone_is_incomplete(self):
        self.assertEqual(
            parse_status("PUBLIC_C1_RUN_COMPLETED=1"),
            "incomplete",
        )


if __name__ == "__main__":
    unittest.main()
