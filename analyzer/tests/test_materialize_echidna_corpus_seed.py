import unittest
from types import SimpleNamespace

from analyzer.materialize_echidna_corpus_seed import (
    boundary_value,
    parameter_equalities,
    parameter_uses,
    parse_literal,
)


class MaterializeEchidnaCorpusSeedTests(unittest.TestCase):
    def test_parses_integer_literals_and_violation_boundary(self):
        self.assertEqual(parse_literal("0x0c"), 12)
        self.assertEqual(parse_literal("-10"), -10)
        self.assertEqual(boundary_value({"op": "gt", "left": {"kind": "state_variable"}, "right": {"kind": "constant", "value": 100}}), 101)

    def test_extracts_exact_parameter_requirements(self):
        function = SimpleNamespace(
            full_name="f(uint256)",
            parameters=[SimpleNamespace(name="x")],
            nodes=[SimpleNamespace(expression="require(bool)(x == 12)")],
        )
        self.assertEqual(parameter_equalities(function), {"x": 12})
        self.assertEqual(parameter_uses(function), {"x"})

    def test_ignores_non_exact_requirements(self):
        function = SimpleNamespace(
            full_name="f(uint256)",
            parameters=[SimpleNamespace(name="x")],
            nodes=[SimpleNamespace(expression="require(bool)(x > 12)")],
        )
        self.assertEqual(parameter_equalities(function), {})


if __name__ == "__main__":
    unittest.main()
