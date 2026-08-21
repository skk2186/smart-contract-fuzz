import unittest

from analyzer.run_native_corpus_seed import classify_output


class RunNativeCorpusSeedTests(unittest.TestCase):
    def test_falsified_property_with_nonzero_exit_is_valid_result(self):
        self.assertEqual(
            classify_output("Test echidna_value_safe falsified!", 1),
            "falsified",
        )

    def test_clean_passing_and_startup_error_are_distinguished(self):
        self.assertEqual(classify_output("echidna_value_safe: passing", 0), "passed")
        self.assertEqual(classify_output("compilation failed", 1), "startup_error")


if __name__ == "__main__":
    unittest.main()
