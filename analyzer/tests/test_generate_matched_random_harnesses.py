import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from generate_matched_random_harnesses import (  # noqa: E402
    parse_signature,
    render_sequence,
    selection_hash,
)


class MatchedRandomHarnessTests(unittest.TestCase):
    def test_parse_signature(self):
        self.assertEqual(
            parse_signature("execute(uint256,uint256)"),
            ("execute", ["uint256", "uint256"]),
        )
        self.assertEqual(parse_signature("prepare()"), ("prepare", []))

    def test_render_sequence_uses_unique_parameters(self):
        parameters, calls = render_sequence(
            ["run(uint256)", "run(uint256)"]
        )
        self.assertIn("arg_0_0", parameters)
        self.assertIn("arg_1_0", parameters)
        self.assertEqual(len(calls), 2)

    def test_selection_hash_is_order_sensitive(self):
        first = selection_hash([["a()", "b()"]])
        second = selection_hash([["b()", "a()"]])
        self.assertNotEqual(first, second)

    def test_invalid_signature_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid function signature"):
            parse_signature("not a signature")


if __name__ == "__main__":
    unittest.main()
