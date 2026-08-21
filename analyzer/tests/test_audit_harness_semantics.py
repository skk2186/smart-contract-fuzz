import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT / "analyzer"))

from audit_harness_semantics import (  # noqa: E402
    audit_target,
    collect_source_closure,
    strip_comments_and_strings,
)


class HarnessSemanticsAuditTests(unittest.TestCase):
    def write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def audit(self, root: Path, source: str, contract: str):
        return audit_target(
            project_root=root,
            cohort="test",
            benchmark="case",
            source_file=source,
            target_contract=contract,
        )

    def test_comments_and_strings_do_not_trigger_features(self):
        clean = strip_comments_and_strings(
            '// msg.sender\nstring x = "msg.value"; /* tx.origin */\nuint x;'
        )
        self.assertNotIn("msg.sender", clean)
        self.assertNotIn("msg.value", clean)
        self.assertNotIn("tx.origin", clean)
        self.assertEqual(clean.count("\n"), 2)

    def test_plain_contract_is_supported_with_atomicity_caveat(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "Plain.sol",
                "pragma solidity 0.8.20; contract Plain { "
                "uint x; function set(uint v) public { x = v; } }",
            )
            row = self.audit(root, "Plain.sol", "Plain")
            self.assertEqual(row["classification"], "supported")
            self.assertEqual(row["atomicity_caveat"], 1)
            self.assertEqual(row["reasons"], "atomicity_caveat")

    def test_msg_sender_is_conditional(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "Sender.sol",
                "contract Sender { address owner; function take() public { "
                "owner = msg.sender; } }",
            )
            row = self.audit(root, "Sender.sol", "Sender")
            self.assertEqual(row["classification"], "conditional")
            self.assertEqual(row["msg_sender"], 1)

    def test_payable_and_msg_value_are_unsupported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "Value.sol",
                "contract Value { function put() public payable { "
                "require(msg.value > 0); } }",
            )
            row = self.audit(root, "Value.sol", "Value")
            self.assertEqual(row["classification"], "unsupported")
            self.assertEqual(row["payable"], 1)
            self.assertEqual(row["msg_value"], 1)

    def test_constructor_parameters_are_unsupported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "Ctor.sol",
                "contract Ctor { constructor(uint x, address y) {} }",
            )
            row = self.audit(root, "Ctor.sol", "Ctor")
            self.assertEqual(row["constructor_parameters"], 2)
            self.assertEqual(row["classification"], "unsupported")

    def test_local_imports_are_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "Base.sol",
                "contract Base { address owner = msg.sender; }",
            )
            self.write(
                root,
                "Target.sol",
                'import "./Base.sol"; contract Target is Base {}',
            )
            closure = collect_source_closure(root / "Target.sol")
            self.assertEqual(len(closure), 2)
            row = self.audit(root, "Target.sol", "Target")
            self.assertEqual(row["msg_sender"], 1)
            self.assertEqual(row["classification"], "conditional")

    def test_missing_target_contract_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "Only.sol", "contract Only {}")
            with self.assertRaisesRegex(ValueError, "Target contract"):
                self.audit(root, "Only.sol", "Missing")


if __name__ == "__main__":
    unittest.main()
