import math
import tempfile
import unittest
from pathlib import Path

from analyzer.analyze_public_c1_statistics import (
    event_from_status,
    fisher_exact_two_sided,
    holm_adjust,
    kaplan_meier,
    load_and_validate_runs,
    logrank_two_sided,
    mcnemar_exact_two_sided,
    wilson_interval,
)


class PublicC1StatisticsTests(unittest.TestCase):
    def test_wilson_extreme_intervals_are_not_degenerate(self):
        lower_all, upper_all = wilson_interval(30, 30)
        lower_none, upper_none = wilson_interval(0, 30)

        self.assertGreater(lower_all, 0.0)
        self.assertLess(lower_all, 1.0)
        self.assertAlmostEqual(upper_all, 1.0, places=15)
        self.assertAlmostEqual(lower_none, 0.0, places=15)
        self.assertGreater(upper_none, 0.0)
        self.assertLess(upper_none, 1.0)

    def test_fisher_is_invariant_to_group_order(self):
        first = fisher_exact_two_sided(29, 1, 24, 6)
        swapped = fisher_exact_two_sided(24, 6, 29, 1)

        self.assertAlmostEqual(first, swapped, places=15)

    def test_mcnemar_all_thirty_discordant_one_direction(self):
        self.assertLess(mcnemar_exact_two_sided(30, 0), 2e-9)

    def test_mcnemar_no_discordance_is_one(self):
        self.assertEqual(mcnemar_exact_two_sided(0, 0), 1.0)

    def test_holm_is_bounded_and_monotone_in_sorted_order(self):
        raw = [0.04, 0.001, 0.02, 0.8]
        adjusted = holm_adjust(raw)

        self.assertTrue(all(0.0 <= value <= 1.0 for value in adjusted))
        ordered_adjusted = [
            adjusted[index]
            for index, _ in sorted(
                enumerate(raw),
                key=lambda item: item[1],
            )
        ]
        self.assertEqual(ordered_adjusted, sorted(ordered_adjusted))

    def test_kaplan_meier_handles_events_and_censoring(self):
        points = kaplan_meier([(1.0, 1), (2.0, 0), (3.0, 1)])

        self.assertEqual(points[0].at_risk, 3)
        self.assertEqual(points[1].events, 1)
        self.assertAlmostEqual(points[1].survival_probability, 2 / 3)
        self.assertEqual(points[2].censored, 1)
        self.assertAlmostEqual(points[2].survival_probability, 2 / 3)
        self.assertEqual(points[3].survival_probability, 0.0)

    def test_logrank_identical_samples_are_not_significant(self):
        sample = [(1.0, 1), (2.0, 0), (3.0, 1)]
        statistic, p_value = logrank_two_sided(sample, sample)

        self.assertAlmostEqual(statistic, 0.0)
        self.assertAlmostEqual(p_value, 1.0)

    def test_empty_survival_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            kaplan_meier([])

    def test_empty_parsed_input_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "five C-1"):
                load_and_validate_runs(Path(directory))

    def test_missing_duration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            kaplan_meier([(None, 1)])

    def test_illegal_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid"):
            event_from_status("incomplete")

    def test_nonfinite_holm_value_is_rejected(self):
        with self.assertRaises(ValueError):
            holm_adjust([math.nan])


if __name__ == "__main__":
    unittest.main()
