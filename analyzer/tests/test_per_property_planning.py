import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analyzer"))

import generate_harness_from_paths as harness_generator  # noqa: E402
import generate_property_sequences as property_generator  # noqa: E402
import generate_repetition_aware_sequences as repetition_generator  # noqa: E402
import generate_value_guided_sequences as value_generator  # noqa: E402


CONTRACT_NAME = "TwoProperty"
PROPERTY_A = "echidna_property_a()"
PROPERTY_B = "echidna_property_b()"


def build_rw_data() -> dict:
    return {
        CONTRACT_NAME: {
            PROPERTY_A: {
                "read": ["x"],
                "write": [],
            },
            PROPERTY_B: {
                "read": ["y"],
                "write": [],
            },
            "prepareX()": {
                "read": [],
                "write": ["a"],
            },
            "stepX()": {
                "read": ["a", "x"],
                "write": ["x"],
            },
            "prepareY()": {
                "read": [],
                "write": ["b"],
            },
            "stepY()": {
                "read": ["b", "y"],
                "write": ["y"],
            },
            "noise()": {
                "read": [],
                "write": ["z"],
            },
        }
    }


class PerPropertyPlanningTests(unittest.TestCase):
    def test_property_sequences_are_isolated(self):
        legacy = property_generator.analyze(
            build_rw_data(),
            max_length=4,
            top_k=20,
        )
        a = property_generator.analyze(
            build_rw_data(),
            max_length=4,
            top_k=20,
            property_function="echidna_property_a",
        )
        b = property_generator.analyze(
            build_rw_data(),
            max_length=4,
            top_k=20,
            property_function=PROPERTY_B,
        )

        legacy_data = legacy[CONTRACT_NAME]
        a_data = a[CONTRACT_NAME]
        b_data = b[CONTRACT_NAME]

        self.assertEqual(
            set(legacy_data["property_variables"]),
            {"x", "y"},
        )
        self.assertEqual(a_data["property_function"], PROPERTY_A)
        self.assertEqual(b_data["property_function"], PROPERTY_B)
        self.assertEqual(a_data["property_variables"], ["x"])
        self.assertEqual(b_data["property_variables"], ["y"])
        self.assertNotEqual(
            a_data["property_variables"],
            b_data["property_variables"],
        )
        self.assertNotEqual(a_data["paths"], b_data["paths"])

        self.assertEqual(a_data["target_functions"], ["stepX()"])
        self.assertEqual(b_data["target_functions"], ["stepY()"])
        self.assertTrue(
            all(
                "stepX()" in path["sequence"]
                and "stepY()" not in path["sequence"]
                and path["property_function"] == PROPERTY_A
                for path in a_data["paths"]
            )
        )
        self.assertTrue(
            all(
                "stepY()" in path["sequence"]
                and "stepX()" not in path["sequence"]
                and path["property_function"] == PROPERTY_B
                for path in b_data["paths"]
            )
        )
        self.assertNotIn("property_function", legacy_data)
        self.assertTrue(
            all(
                "property_function" not in path
                for path in legacy_data["paths"]
            )
        )

    def test_repetition_is_property_specific(self):
        function_map = repetition_generator.extract_rw(
            repetition_generator.extract_function_map(
                build_rw_data()[CONTRACT_NAME]
            )
        )
        property_functions = {
            PROPERTY_A,
            PROPERTY_B,
        }

        def paths_for(property_function: str):
            variables = function_map[property_function]["reads"]
            targets = sorted(
                name
                for name, record in function_map.items()
                if name not in property_functions
                and record["writes"].intersection(variables)
            )
            predecessors = repetition_generator.build_predecessors(
                functions=function_map,
                excluded_functions=property_functions,
            )
            paths, _ = repetition_generator.generate_paths(
                predecessors=predecessors,
                target_functions=targets,
                max_path_length=2,
                max_function_visits=2,
                max_expansions=100,
            )
            return paths

        a_paths = paths_for(PROPERTY_A)
        b_paths = paths_for(PROPERTY_B)

        self.assertIn(
            ["stepX()", "stepX()"],
            [path["sequence"] for path in a_paths],
        )
        self.assertNotIn(
            "stepY()",
            {
                function
                for path in a_paths
                for function in path["sequence"]
            },
        )
        self.assertIn(
            ["stepY()", "stepY()"],
            [path["sequence"] for path in b_paths],
        )
        self.assertNotIn(
            "stepX()",
            {
                function
                for path in b_paths
                for function in path["sequence"]
            },
        )

    def test_value_guidance_preserves_property_provenance(self):
        path = {
            "sequence": ["prepareX()", "stepX()"],
            "length": 2,
            "score": 2,
            "dependency_variables": ["a"],
            "target_function": "stepX()",
            "property_function": PROPERTY_A,
        }
        constraints = {
            "prepareX()": {
                "constant_writes": {},
                "requirements": [],
            },
            "stepX()": {
                "constant_writes": {},
                "requirements": [],
            },
        }

        scored = value_generator.score_path(
            path,
            constraints,
            match_reward=4.0,
            conflict_penalty=4.0,
        )

        self.assertEqual(scored["property_function"], PROPERTY_A)
        for key in (
            "property_score",
            "value_score",
            "value_matches",
            "value_conflicts",
            "value_unknowns",
            "value_edges",
            "value_rank",
        ):
            if key == "value_rank":
                continue
            self.assertIn(key, scored)

        property_json = property_generator.analyze(
            build_rw_data(),
            max_length=4,
            top_k=20,
            property_function=PROPERTY_A,
        )
        property_json[CONTRACT_NAME]["paths"] = [scored]
        self.assertEqual(
            property_json[CONTRACT_NAME]["paths"][0]["property_function"],
            PROPERTY_A,
        )

    def test_value_guidance_rejects_mixed_property_paths(self):
        with self.assertRaisesRegex(
            ValueError,
            "different or missing",
        ):
            value_generator.validate_property_provenance(
                {"property_function": PROPERTY_A},
                [
                    {"property_function": PROPERTY_A},
                    {"property_function": PROPERTY_B},
                ],
            )

    def test_harness_exposes_only_selected_property_and_rejects_mismatch(self):
        source = """pragma solidity 0.4.25;
contract TwoProperty {
    uint public x;
    uint public y;

    function prepareX() public { x = 1; }
    function stepX() public { x = x + 1; }
    function prepareY() public { y = 1; }
    function stepY() public { y = y + 1; }

    function echidna_property_a() public view returns (bool) {
        return x >= 0;
    }

    function echidna_property_b() public view returns (bool) {
        return y >= 0;
    }
}
"""
        sequence_data = {
            CONTRACT_NAME: {
                "property_function": PROPERTY_A,
                "paths": [
                    {
                        "property_function": PROPERTY_A,
                        "sequence": ["prepareX()", "stepX()"],
                    }
                ],
            }
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "TwoProperty.sol"
            sequence_path = root / "property-a.json"
            output_path = root / "HarnessA.sol"
            source_path.write_text(source, encoding="utf-8")
            sequence_path.write_text(
                json.dumps(sequence_data),
                encoding="utf-8",
            )

            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = (
                "/home/skk/miniconda3/envs/contract-fuzz/bin:"
                + old_path
            )
            try:
                harness_generator.generate_harness(
                    source_file=source_path,
                    sequence_json=sequence_path,
                    target_contract_name=CONTRACT_NAME,
                    harness_contract_name="HarnessA",
                    output_file=output_path,
                    function_prefix="guided",
                    top_k=1,
                    property_function="echidna_property_a",
                )
            finally:
                os.environ["PATH"] = old_path

            harness = output_path.read_text(encoding="utf-8")
            self.assertIn(
                "// Target property: echidna_property_a()",
                harness,
            )
            self.assertIn(
                "function echidna_property_a()",
                harness,
            )
            self.assertNotIn(
                "function echidna_property_b()",
                harness,
            )

            with self.assertRaisesRegex(
                ValueError,
                "does not match",
            ):
                harness_generator.load_paths(
                    sequence_path,
                    CONTRACT_NAME,
                    top_k=1,
                    property_function=PROPERTY_B,
                )

            with self.assertRaisesRegex(
                ValueError,
                "was not found",
            ):
                harness_generator.resolve_property_function(
                    {},
                    PROPERTY_A,
                )


if __name__ == "__main__":
    unittest.main()
