import csv
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from audit_baseline_feasibility import audit_baselines  # noqa: E402
from validate_c2_candidate_registry import (  # noqa: E402
    REQUIRED_FIELDS,
    validate_registry,
)


class C2ReadinessTests(unittest.TestCase):
    def test_baseline_audit_contains_external_and_internal_entries(self):
        rows = audit_baselines(ROOT)
        names = {row["baseline"] for row in rows}
        self.assertIn("original-echidna", names)
        self.assertIn("smartian", names)
        self.assertIn("random-matched-top-k", names)

    def write_registry(self, path: Path, row: dict[str, str]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=sorted(REQUIRED_FIELDS),
                delimiter="\t",
            )
            writer.writeheader()
            writer.writerow(row)

    def base_row(self) -> dict[str, str]:
        return {
            "candidate_id": "candidate-a",
            "role": "c2_candidate",
            "source_pool": "test",
            "repository": "example/repo",
            "commit": "abc",
            "source_path": "A.sol",
            "local_source": "A.sol",
            "compiler": "0.8.20",
            "target_contract": "A",
            "property_origin": "upstream",
            "min_sequence_length": "2",
            "semantic_classification": "supported",
            "screening_status": "identified",
            "fuzzing_status": "not_started",
            "exclusion_reason": "",
        }

    def test_valid_preregistered_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "A.sol").write_text("contract A {}", encoding="utf-8")
            registry = root / "registry.tsv"
            self.write_registry(registry, self.base_row())
            self.assertEqual(len(validate_registry(registry, root)), 1)

    def test_rejects_fuzzing_before_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "A.sol").write_text("contract A {}", encoding="utf-8")
            row = self.base_row()
            row["fuzzing_status"] = "started"
            registry = root / "registry.tsv"
            self.write_registry(registry, row)
            with self.assertRaisesRegex(ValueError, "before registry freeze"):
                validate_registry(registry, root)

    def test_rejects_single_step_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "A.sol").write_text("contract A {}", encoding="utf-8")
            row = self.base_row()
            row["min_sequence_length"] = "1"
            registry = root / "registry.tsv"
            self.write_registry(registry, row)
            with self.assertRaisesRegex(ValueError, "not a multi-step"):
                validate_registry(registry, root)


if __name__ == "__main__":
    unittest.main()
