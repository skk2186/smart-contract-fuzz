import csv
import sys
import tempfile
import unittest
from pathlib import Path


ANALYZER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYZER_DIR))

from run_matched_random_v1 import (  # noqa: E402
    classify_output,
    expected_properties,
    load_manifest,
)


class RunMatchedRandomV1Tests(unittest.TestCase):
    def test_status_priority_and_budget_semantics(self):
        expected = {"echidna_ok"}
        self.assertEqual(
            classify_output("echidna_ok: failed!", 0, expected), "falsified"
        )
        self.assertEqual(
            classify_output("echidna_ok: failed!", 1, expected), "falsified"
        )
        self.assertEqual(
            classify_output(
                "echidna_ok: passing\nTest limit reached. Stopping.", 0, expected
            ),
            "budget_exhausted",
        )
        self.assertEqual(classify_output("echidna_ok: passing", 0, expected), "passed")
        self.assertEqual(classify_output("partial", 0, expected), "incomplete")
        self.assertEqual(
            classify_output("echidna_ok: passing", 1, expected), "startup_error"
        )

    def test_requires_all_declared_properties(self):
        expected = {"echidna_a", "echidna_b"}
        self.assertEqual(
            classify_output("echidna_a: failed!", 0, expected), "incomplete"
        )

    def test_reads_declared_properties(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Harness.sol"
            path.write_text(
                "contract H { function echidna_a() public returns (bool) { "
                "return true; } function helper() public {} }",
                encoding="utf-8",
            )
            self.assertEqual(expected_properties(path), {"echidna_a"})

    def test_manifest_rejects_duplicate_benchmark_seed(self):
        fields = [
            "cohort",
            "benchmark",
            "method",
            "fuzz_seed",
            "schedule_seed",
            "selection_id",
            "selected_candidate_indices",
            "selection_sha256",
            "harness_file",
            "harness_contract",
            "compiler",
            "config_file",
            "semantic_classification",
        ]
        row = {
            "cohort": "formal",
            "benchmark": "example",
            "method": "matched-random-k1",
            "fuzz_seed": "1",
            "schedule_seed": "7",
            "selection_id": "x",
            "selected_candidate_indices": "1",
            "selection_sha256": "abc",
            "harness_file": "h.sol",
            "harness_contract": "H",
            "compiler": "0.8.20",
            "config_file": "c.yaml",
            "semantic_classification": "supported",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.tsv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerow(row)
                writer.writerow(row)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_manifest(path, Path(directory))


if __name__ == "__main__":
    unittest.main()
