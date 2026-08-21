import sys
from pathlib import Path

from slither.slither import Slither


INTERESTING_ATTRIBUTES = (
    "lvalue",
    "rvalue",
    "variable_left",
    "variable_right",
    "type",
    "function",
    "arguments",
    "read",
)


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python analyzer/inspect_slithir.py <contract.sol>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    source = Path(sys.argv[1])

    if not source.is_file():
        print(f"Source not found: {source}", file=sys.stderr)
        raise SystemExit(1)

    slither = Slither(str(source))

    for contract in slither.contracts:
        print(f"\n===== CONTRACT {contract.name} =====")

        for function in contract.functions_declared:
            if function.is_constructor:
                continue

            print(f"\n--- FUNCTION {function.full_name} ---")

            for node in function.nodes:
                print(
                    f"\nNODE id={node.node_id} "
                    f"type={node.type}"
                )
                print(f"EXPRESSION: {node.expression}")

                for ir in node.irs:
                    print(
                        f"  IR_CLASS: {ir.__class__.__name__}"
                    )
                    print(f"  IR_TEXT : {ir}")

                    for attribute in INTERESTING_ATTRIBUTES:
                        if not hasattr(ir, attribute):
                            continue

                        try:
                            value = getattr(ir, attribute)
                        except Exception as error:
                            value = f"<error: {error}>"

                        print(
                            f"  {attribute.upper()}: {value}"
                        )


if __name__ == "__main__":
    main()
