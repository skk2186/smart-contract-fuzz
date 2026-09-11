# 附录规划

## 附录 A：实验配置

- 给出编译器、工具版本、testLimit、timeout、workers、stopOnFail、随机种子和执行模型。
- 区分 Original、Full-K1 和 Full-K5。
- 说明配置文件、manifest 和结果 summary 的对应关系。
- 不粘贴大型 raw log，只给出可复现入口和摘要字段。

## 附录 B：受控场景任务细节

- 展示六个 controlled evidence 场景的目标属性、状态变量、障碍类型和方法组件。
- 保留 formal-main 与 B-2 扩展的分组。
- 说明受控场景用于机制解释，不代表真实生态分布。

## 附录 C：真实来源 adapted candidates

- 介绍两个 Echidna-origin candidates 和两个 SmartBugs candidates 的来源、适配内容与属性接口。
- 给出 4 candidates、120 runs、80 usable/descriptive records 的分层说明。
- 只把两个 Echidna-origin candidates 的 Original/Full-K1/Full-K5 作为 comparable subset。

## 附录 D：excluded engineering rows

- 记录 SmartBugs Harness 的 40 条 compile_error。
- 说明 Solidity 0.4.25 import-path / Harness 生成限制。
- 明确这些记录不进入发现率、性能或 comparative outcomes。
- 不将 compile_error 改写为方法检测失败。

## 附录 E：参考文献与 artifact 说明

- 提供正式 BibTeX 和 cite key 对照。
- 单列 high_confidence 的定稿前复核状态和 unresolved 清单。
- 说明代码、配置、result TSV、analysis summary 和 paper-ready materials 的可用性。
- 匿名投稿版本移除用户名、私人路径和可识别仓库信息。
