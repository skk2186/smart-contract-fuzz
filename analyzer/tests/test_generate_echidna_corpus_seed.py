import json
import tempfile
import unittest
from pathlib import Path

from analyzer.generate_echidna_corpus_seed import (
    SeedSpecError,
    build_call,
    write_seed,
)


class GenerateEchidnaCorpusSeedTests(unittest.TestCase):
    def test_builds_zero_argument_call_with_echidna_metadata(self):
        call = build_call("Owner()", [])
        self.assertEqual(call["call"], {"contents": ["Owner", []], "tag": "SolCall"})
        self.assertEqual(call["gas"], 12_500_000)
        self.assertEqual(call["delay"], ["0x" + "0" * 64] * 2)

    def test_writes_ordered_multi_transaction_seed_and_uint_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_seed(
                Path(tmp),
                ["prepareGood()", "unlock()", "activate()", "trigger(uint256)"],
                [101],
            )
            payload = json.loads(path.read_text())
        self.assertEqual([item["call"]["contents"][0] for item in payload], [
            "prepareGood", "unlock", "activate", "trigger"
        ])
        self.assertEqual(payload[-1]["call"]["contents"][1][0]["contents"], [256, "101"])

    def test_rejects_wrong_value_count_and_unsupported_types(self):
        with self.assertRaises(SeedSpecError):
            write_seed(Path(tempfile.mkdtemp()), ["f(uint256)"], [])
        with self.assertRaises(SeedSpecError):
            build_call("f(address)", [1])

    def test_encodes_signed_integer_argument(self):
        call = build_call("set(int256)", [-10])
        self.assertEqual(
            call["call"]["contents"][1][0],
            {"contents": [256, "-10"], "tag": "AbiInt"},
        )


if __name__ == "__main__":
    unittest.main()
