import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from build_matched_random_schedule import (  # noqa: E402
    balanced_schedule,
    stable_permutation,
)


class MatchedRandomScheduleTests(unittest.TestCase):
    def test_schedule_is_deterministic(self):
        first = balanced_schedule(7, 30, 1, 20260805, "case")
        second = balanced_schedule(7, 30, 1, 20260805, "case")
        self.assertEqual(first, second)

    def test_different_benchmarks_get_different_permutations(self):
        first = stable_permutation(20, 1, "case-a", 0, "candidates")
        second = stable_permutation(20, 1, "case-b", 0, "candidates")
        self.assertNotEqual(first, second)

    def test_top1_inclusion_is_balanced(self):
        schedule = balanced_schedule(7, 30, 1, 20260805, "case")
        counts = Counter(selected[0] for _, _, selected in schedule)
        values = [counts[index] for index in range(7)]
        self.assertLessEqual(max(values) - min(values), 1)

    def test_topk_full_block_is_balanced(self):
        schedule = balanced_schedule(7, 7, 3, 20260805, "case")
        counts = Counter(index for _, _, selected in schedule for index in selected)
        self.assertEqual(set(counts.values()), {3})

    def test_selection_contains_unique_candidates(self):
        schedule = balanced_schedule(5, 30, 3, 20260805, "case")
        self.assertTrue(
            all(len(selected) == len(set(selected)) for _, _, selected in schedule)
        )

    def test_invalid_topk_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "top_k"):
            balanced_schedule(2, 30, 3, 20260805, "case")


if __name__ == "__main__":
    unittest.main()
