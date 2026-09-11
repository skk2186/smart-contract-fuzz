# Ethics and Limitations Note

本研究面向公开来源或经过研究适配的智能合约测试任务，目标是评估多交易序列生成方法的适用性和证据边界。实验不包含真实攻击部署、资产转移或针对运行中系统的入侵行为，也不声称发现了现实世界中尚未披露的漏洞。

真实来源适配仅用于研究评估，适配后的源代码、属性接口、编译器和 Harness 执行条件可能与原始部署环境不同。工具输出由研究者进行复核，并将 SmartBugs Harness 的 compile_error、budget_exhausted 的 right-censoring 和 Original/Harness execution-model difference 分别报告。因而，结果不应被解释为真实系统安全保证，也不应被解释为 Original 与 Harness 语义等价。
