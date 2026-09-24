# 附录：实现说明与复现材料

本附录集中记录正文中省略的实现入口、输出字段和参数。它们用于复现和代码审阅，不改变正文中的方法定义与实验结论。

## A.1 脚本入口

- analyzer/generate_property_sequences.py：生成属性级或联合模式的基础候选路径。
- analyzer/generate_repetition_aware_sequences.py：在属性目标函数集合上进行有界重复扩展。
- analyzer/generate_value_guided_sequences.py：对已有候选路径进行轻量值证据后处理和排序。
- analyzer/generate_harness_from_paths.py：根据选定候选生成 Solidity 测试封装合约。
- analyzer/run_per_property_isolation.py：重建受控多属性隔离实验的机器可读汇总。

## A.2 关键输入和输出字段

显式属性模式的合约数据记录以下字段：

- property_function
- property_variables
- target_functions
- paths

每条路径保留：

- sequence
- length
- score
- dependency_variables
- target_function
- property_function

值证据后处理保留或补充：

- property_score
- value_score
- value_matches
- value_conflicts
- value_unknowns
- value_edges
- value_rank

这些字段用于来源追踪和结果复核。正文采用中文概念描述，字段名称仅在实现说明中保留原样。

## A.3 实现参数

受控多属性隔离记录使用：

- max_length：6
- top_k：1000
- path_builder：build_relevant_paths

重复扩展阶段保留：

- --max-function-visits
- --max-expansions

这些参数控制路径长度、候选截断、函数访问次数和搜索展开量。它们属于实现配置，具体实验数字以冻结机器可读记录为准。

## A.4 机器可读复现材料

- contracts/benchmarks/MultiPropertyInterference.sol：受控多属性合约。
- results/per-property-isolation/summary.json：联合模式与单属性模式的候选统计、目标排序位置和前 K 命中结果。
- analyzer/run_per_property_isolation.py：受控结果的重建入口。
- analyzer/tests/test_per_property_planning.py：属性级规划回归测试。
- analyzer/generate_property_sequences.py、analyzer/generate_repetition_aware_sequences.py、analyzer/generate_value_guided_sequences.py 和 analyzer/generate_harness_from_paths.py：方法实现入口。

实验结果目录中的既有冻结文件保持原样。本附录仅记录已有实现和证据的读取位置，不生成新的实验数据。

## A.5 论文产物位置

- paper-ready/v1/c17/c17_formal_chinese_paper_draft.md：上一版中文技术稿。
- paper-ready/v1/c18/c18_academic_paper_draft.md：降技术细节后的正文稿。
- paper-ready/v1/c18/c18_reference_normalized_draft.md：编号参考文献版本。
- paper-ready/v1/c18/c18_appendix_implementation_notes.md：本附录。
- paper-ready/v1/c18/c18_academic_paper_draft.docx：Word 初稿。
