import json
import sys
from pathlib import Path

from slither.slither import Slither


def state_variable_key(variable) -> str:
    """
    生成状态变量的唯一标识键，优先使用 canonical_name
    避免继承层级中同名变量发生混淆
    """
    canonical_name = getattr(
        variable,
        "canonical_name",
        None,
    )

    if canonical_name:
        return str(canonical_name)

    return str(variable.name)


def collect_callable_functions(contract):
    """
    收集目标合约所有可外部调用的函数，包含继承而来的函数
    过滤构造函数、fallback、receive，仅保留 public/external 可见性
    """
    functions = {}

    for function in contract.functions:
        if getattr(function, "is_constructor", False):
            continue

        if getattr(function, "is_fallback", False):
            continue

        if getattr(function, "is_receive", False):
            continue

        if function.visibility not in {
            "public",
            "external",
        }:
            continue

        functions[function.full_name] = function

    return list(functions.values())


def collect_state_reads(function) -> set:
    """
    递归收集函数读取的所有状态变量，包含内部调用和修饰器中的读取
    优先使用 all_state_variables_read()，异常时回退到基础属性
    """
    variables = set()

    try:
        variables.update(
            function.all_state_variables_read()
        )
    except Exception:
        variables.update(
            function.state_variables_read
        )

    for modifier in getattr(
        function,
        "modifiers",
        [],
    ):
        try:
            variables.update(
                modifier.all_state_variables_read()
            )
        except Exception:
            variables.update(
                modifier.state_variables_read
            )

    return {
        state_variable_key(variable)
        for variable in variables
    }


def collect_state_writes(function) -> set:
    """
    递归收集函数写入的所有状态变量，包含内部调用和修饰器中的写入
    优先使用 all_state_variables_written()，异常时回退到基础属性
    """
    variables = set()

    try:
        variables.update(
            function.all_state_variables_written()
        )
    except Exception:
        variables.update(
            function.state_variables_written
        )

    for modifier in getattr(
        function,
        "modifiers",
        [],
    ):
        try:
            variables.update(
                modifier.all_state_variables_written()
            )
        except Exception:
            variables.update(
                modifier.state_variables_written
            )

    return {
        state_variable_key(variable)
        for variable in variables
    }


def extract_rw(contract_file: str) -> dict:
    slither = Slither(contract_file)
    result = {}

    for contract in slither.contracts:
        functions = {}

        # 替换为全量可调用函数收集（含继承）
        for function in collect_callable_functions(contract):
            reads = sorted(collect_state_reads(function))
            writes = sorted(collect_state_writes(function))

            functions[function.full_name] = {
                "visibility": function.visibility,
                "read": reads,
                "write": writes,
            }

        result[contract.name] = functions

    return result


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python analyzer/extract_rw.py <contract.sol>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    contract_path = Path(sys.argv[1])

    if not contract_path.is_file():
        print(f"Contract not found: {contract_path}", file=sys.stderr)
        raise SystemExit(1)

    result = extract_rw(str(contract_path))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()