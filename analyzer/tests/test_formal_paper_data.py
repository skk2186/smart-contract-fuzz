import csv
import re
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from analyzer.experiment_validation import validate_manifest_runs


ROOT = Path(__file__).resolve().parents[2]


def read_rows(relative: str) -> list[dict]:
    with (ROOT / relative).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


class FormalDerivedDataTests(unittest.TestCase):
    def test_formal_has_expected_groups_rows_and_status_counts(self):
        summary = read_rows("results/formal/formal-group-summary.csv")
        self.assertEqual(len(summary), 15)
        self.assertTrue(all(int(row["total_logs"]) == 30 for row in summary))
        self.assertEqual(sum(int(row["total_logs"]) for row in summary), 450)
        self.assertEqual(sum(int(row["falsified_runs"]) for row in summary), 381)
        self.assertEqual(
            sum(int(row["budget_exhausted_runs"]) for row in summary), 69
        )
        for field in (
            "total_logs",
            "valid_runs",
            "falsified_runs",
            "budget_exhausted_runs",
            "passed_runs",
            "startup_error_runs",
            "incomplete_runs",
            "success_rate",
        ):
            self.assertIn(field, summary[0])
        self.assertEqual(sum(int(row["passed_runs"]) for row in summary), 0)
        self.assertEqual(
            sum(int(row["startup_error_runs"]) for row in summary), 0
        )
        self.assertEqual(sum(int(row["incomplete_runs"]) for row in summary), 0)

        parsed = []
        for path in sorted((ROOT / "results/formal/parsed").glob("*.csv")):
            with path.open(encoding="utf-8", newline="") as file:
                parsed.extend(csv.DictReader(file))
        self.assertEqual(len(parsed), 450)
        statuses = Counter(row["status"] for row in parsed)
        self.assertEqual(statuses, Counter(falsified=381, budget_exhausted=69))
        self.assertNotIn("not_falsified", statuses)

    def test_formal_group_counts_match_audited_values(self):
        expected = {
            ("branch-value", "original"): (28, 2),
            ("branch-value", "property-k1"): (0, 30),
            ("branch-value", "value-k1"): (30, 0),
            ("branch-value", "full-k1"): (30, 0),
            ("noisy-four-step", "original"): (26, 4),
            ("noisy-four-step", "dependency-k10"): (30, 0),
            ("noisy-four-step", "property-k1"): (30, 0),
            ("noisy-four-step", "full-k1"): (30, 0),
            ("reset-example", "original"): (27, 3),
            ("reset-example", "dependency-k10"): (30, 0),
            ("reset-example", "property-k1"): (30, 0),
            ("reset-example", "full-k1"): (30, 0),
            ("repeated-call", "original"): (30, 0),
            ("repeated-call", "value-no-repeat-k1"): (0, 30),
            ("repeated-call", "full-k1"): (30, 0),
        }
        rows = read_rows("results/formal/formal-group-summary.csv")
        observed = {
            (row["benchmark"], row["method"]): (
                int(row["falsified_runs"]),
                int(row["budget_exhausted_runs"]),
            )
            for row in rows
        }
        self.assertEqual(observed, expected)


class FormalB2Tests(unittest.TestCase):
    def test_b2_run_summary_has_five_groups_and_150_successes(self):
        rows = read_rows("results/formal-b2/formal-b2-run-summary.csv")
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(int(row["runs"]) == 30 for row in rows))
        self.assertEqual(sum(int(row["runs"]) for row in rows), 150)
        self.assertEqual(sum(int(row["successful_runs"]) for row in rows), 150)
        self.assertTrue(all(row["denominator_unit"] == "runs" for row in rows))
        self.assertTrue(
            all(
                row["environment_snapshot_status"]
                == "missing_independent_snapshot"
                for row in rows
            )
        )

    def test_multi_property_distinguishes_runs_and_property_outcomes(self):
        rows = read_rows(
            "results/formal-b2/parsed/multi-property-detailed.csv"
        )
        self.assertEqual(len(rows), 60)
        for method in ("original", "full-k1"):
            selected = [row for row in rows if row["method"] == method]
            self.assertEqual(len(selected), 30)
            self.assertEqual(sum(int(row["property_outcomes"]) for row in selected), 60)
            self.assertEqual(
                sum(int(row["echidna_value_a_safe"]) for row in selected), 30
            )
            self.assertEqual(
                sum(int(row["echidna_value_b_safe"]) for row in selected), 30
            )
            self.assertEqual(
                sum(int(row["both_properties_failed"]) for row in selected), 30
            )

        grouped = read_rows(
            "results/formal-b2/grouped/multi-property-properties.csv"
        )
        composites = [
            row for row in grouped if row["metric"] == "both_properties_failed"
        ]
        self.assertEqual(len(composites), 2)
        self.assertTrue(
            all(row["metric_type"] == "run_level_composite" for row in composites)
        )


class PaperDataTests(unittest.TestCase):
    def test_synthetic_six_totals(self):
        detailed = read_rows(
            "results/paper-data/synthetic-six-benchmark-summary.csv"
        )
        self.assertEqual(len(detailed), 12)
        overall = read_rows(
            "results/paper-data/synthetic-six-overall-descriptive.csv"
        )
        observed = {
            row["method"]: (int(row["runs"]), int(row["falsified_runs"]))
            for row in overall
        }
        self.assertEqual(observed, {"Original": (180, 171), "Full-K1": (180, 180)})
        self.assertTrue(
            all(row["pooled_significance_test"] == "not_performed" for row in overall)
        )
        multi = [row for row in detailed if row["benchmark"] == "multi-property"]
        self.assertTrue(all(row["stop_on_fail"] == "false" for row in multi))
        self.assertTrue(
            all(
                row["success_definition"]
                == "both_specified_properties_falsified_in_same_run"
                for row in multi
            )
        )

    def test_dataset_roles_exclude_development_and_mixed_inputs(self):
        rows = read_rows("results/paper-data/dataset-whitelist.csv")
        roles = {row["role"] for row in rows}
        self.assertEqual(
            roles, {"main", "ablation_or_appendix", "exclude_from_main"}
        )
        prohibited_markers = ("results/v2/", "c0", "smoke", "random/")
        for row in rows:
            if any(marker in row["path"] for marker in prohibited_markers):
                self.assertEqual(row["role"], "exclude_from_main")
                self.assertEqual(row["inclusion_status"], "excluded")

    def test_ranking_interpretation_matches_tie_aware_csv(self):
        rows = read_rows("results/formal/formal-tie-aware-ranking.csv")
        reset = {
            row["method"]: row
            for row in rows
            if row["benchmark"] == "reset-example"
        }
        self.assertEqual(
            (reset["property"]["best_tied_rank"], reset["property"]["worst_tied_rank"]),
            ("1", "6"),
        )
        self.assertEqual(reset["repeat"]["display_rank"], "5")
        self.assertEqual(
            (reset["repeat"]["best_tied_rank"], reset["repeat"]["worst_tied_rank"]),
            ("1", "18"),
        )
        document = (
            ROOT / "results/paper-data/ranking-interpretation.md"
        ).read_text(encoding="utf-8")
        for statement in ("66.3043478%", "tie-aware rank 为1–6", "tie-aware rank 为1–18"):
            self.assertIn(statement, document)
        self.assertIn("不得把 Reset 描述成严格分数意义", document)

    def test_rebuild_scripts_are_pure_derived_entrypoints(self):
        forbidden = re.compile(r"\b(?:echidna|solc|solc-select)\b", re.I)
        for relative in (
            "scripts/rebuild_formal_derived_results.sh",
            "scripts/rebuild_formal_b2_derived_results.sh",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("set -euo pipefail", text)
            self.assertIsNone(forbidden.search(text))
            self.assertNotIn("$HOME", text)

    def test_invalid_manifest_inputs_fail_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "manifest.tsv"
            manifest.write_text(
                "benchmark\tmethod\tcontract_file\tcontract_name\tconfig_file\n"
                "case\tmethod\tcontract.sol\tContract\tconfig.yaml\n",
                encoding="utf-8",
            )
            group = root / "runs/case/method"
            group.mkdir(parents=True)
            (group / "seed-1.log").write_text(
                "SEED=1\nDONE=1\n", encoding="utf-8"
            )
            output = root / "derived.csv"
            with self.assertRaises(ValueError):
                validate_manifest_runs(
                    manifest,
                    root / "runs",
                    expected_groups=1,
                    expected_seeds=2,
                    completion_marker="DONE=1",
                )
            self.assertFalse(output.exists())

    def test_checksum_manifest_has_sorted_valid_entries(self):
        path = ROOT / "results/paper-data/input-checksums.sha256"
        lines = path.read_text(encoding="utf-8").splitlines()
        paths = [line.split("  ", 1)[1] for line in lines]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all((ROOT / item).is_file() for item in paths))
        self.assertTrue(any(item.startswith("results/formal/runs/") for item in paths))
        self.assertTrue(
            any(item.startswith("results/formal-b2/runs/") for item in paths)
        )
        self.assertTrue(
            any(item.startswith("results/public-benchmarks/c1/runs/") for item in paths)
        )
        self.assertTrue(
            any(item.startswith("results/matched-random-v1/runs/") for item in paths)
        )
        self.assertTrue(
            any(
                item.startswith(
                    "results/public-benchmarks/c2-screening/"
                    "smartian-formal-20260806/runs/"
                )
                for item in paths
            )
        )


if __name__ == "__main__":
    unittest.main()
