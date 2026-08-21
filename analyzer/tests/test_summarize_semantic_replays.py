import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from summarize_semantic_replays import TRACE_CASES, build_rows  # noqa: E402


class SemanticReplaySummaryTests(unittest.TestCase):
    def write_profiles(self, root: Path, all_passed: bool = True) -> None:
        profiles = sorted({case[2] for case in TRACE_CASES})
        for profile in profiles:
            properties = [case[3] for case in TRACE_CASES if case[2] == profile]
            data = {
                "profile": profile,
                "all_passed": all_passed,
                "passed_properties": properties,
            }
            (root / f"{profile}-validation.json").write_text(
                json.dumps(data), encoding="utf-8"
            )

    def test_builds_all_eleven_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_profiles(root)
            rows = build_rows(root)
            self.assertEqual(len(rows), 11)
            self.assertEqual(
                sum(row["static_classification"] == "conditional" for row in rows),
                1,
            )

    def test_rejects_nonpassing_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_profiles(root, all_passed=False)
            with self.assertRaisesRegex(ValueError, "did not pass"):
                build_rows(root)


if __name__ == "__main__":
    unittest.main()
