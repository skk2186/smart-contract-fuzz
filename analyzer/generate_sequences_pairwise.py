import json
import sys
from pathlib import Path


def is_echidna_property(function_name: str) -> bool:
    return function_name.startswith("echidna_")


def build_sequences(rw_data: dict, top_k: int = 10) -> dict:
    result = {}

    for contract_name, functions in rw_data.items():
        candidates = []

        # 过滤掉 echidna_ 属性函数，因为它们不是交易步骤
        normal_functions = {
            fname: info
            for fname, info in functions.items()
            if not is_echidna_property(fname)
        }

        function_items = list(normal_functions.items())

        for f1_name, f1_info in function_items:
            for f2_name, f2_info in function_items:
                if f1_name == f2_name:
                    continue

                f1_reads = set(f1_info.get("read", []))
                f1_writes = set(f1_info.get("write", []))
                f2_reads = set(f2_info.get("read", []))
                f2_writes = set(f2_info.get("write", []))

                write_read = f1_writes & f2_reads
                write_write = f1_writes & f2_writes

                # 核心规则：
                # 如果 f1 写的变量被 f2 读取，则认为 f1 -> f2 有状态依赖
                score = 2 * len(write_read) + 1 * len(write_write)

                if score > 0:
                    candidates.append({
                        "sequence": [f1_name, f2_name],
                        "score": score,
                        "write_read_variables": sorted(write_read),
                        "write_write_variables": sorted(write_write),
                    })

        candidates.sort(
            key=lambda x: (
                x["score"],
                len(x["write_read_variables"]),
                len(x["write_write_variables"]),
            ),
            reverse=True,
        )

        result[contract_name] = {
            "sequences": candidates[:top_k]
        }

    return result


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python analyzer/generate_sequences.py <rw.json> [top_k]",
            file=sys.stderr,
        )
        raise SystemExit(1)

    rw_path = Path(sys.argv[1])

    if not rw_path.is_file():
        print(f"File not found: {rw_path}", file=sys.stderr)
        raise SystemExit(1)

    top_k = 10
    if len(sys.argv) >= 3:
        top_k = int(sys.argv[2])

    with rw_path.open("r", encoding="utf-8") as f:
        rw_data = json.load(f)

    sequences = build_sequences(rw_data, top_k=top_k)
    print(json.dumps(sequences, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
