# SMARTIAN 校准阶段记录

日期：2026-08-06  
状态：完成短时运行校准；尚未纳入正式 C2 分母。

## 固定运行条件

- SMARTIAN commit：`eca1ed1d60c88ec5402055a05b59174b7288264c`
- .NET SDK：8.0.423；目标框架：`net8.0`
- 程序：`baselines/smartian/src/bin/Release/net8.0/Smartian.dll`
- 每个样例：5 秒，`-v 0`，默认 SDFA/DDFA，未启用 `--useothersoracle`
- 输出根目录：`/tmp/smartian-calibration-20260806`
- SMARTIAN CLI 没有公开 seed 参数，因此本阶段不宣称 seed 级确定性；正式实验必须保存每次运行的完整命令、环境和输出。

复现命令模板（在仓库根目录执行）：

```bash
export DOTNET_ROOT="$PWD/.tools/dotnet"
export PATH="$DOTNET_ROOT:$PATH"
export DOTNET_CLI_HOME=/tmp/smartian-dotnet-home
export NUGET_PACKAGES=/tmp/smartian-nuget
dotnet baselines/smartian/src/bin/Release/net8.0/Smartian.dll fuzz \
  -p baselines/smartian/examples/bc/IB.bin \
  -a baselines/smartian/examples/abi/IB.abi \
  -t 5 -o /tmp/smartian-calibration-replay-IB -v 0
```

## 结果

逐行结果见 [`smartian-calibration.tsv`](smartian-calibration.tsv)，机器可读摘要见 [`smartian-calibration-summary.json`](smartian-calibration-summary.json)。三个样例均退出码为 0；`MS_true` 产生 1 个 `MultipleSend` bug 文件，`IB` 和 `BD_false` 在该次 5 秒运行内未产生 bug 文件。

随后完成了每个样例 3 次的重复性检查，明细见 [`smartian-calibration-repeatability.tsv`](smartian-calibration-repeatability.tsv)：9/9 日志有完整结束标记，退出码通过直接捕获或同参数补捕均为 0；`IB` 的告警为 1/3，`BD_false` 为 0/3，`MS_true` 为 3/3。这说明运行链路和解析稳定，但发现结果具有随机性，不能用这组短跑估计检测率。

这里的“未产生”不等于“性质为真”，尤其不能把 `IntegerBug`/`MultipleSend` 等 SMARTIAN 内部告警直接计为 Echidna 的 Boolean property violation。`BD_false` 是负控制样例，用来检查误报边界。

## 进入正式实验前的门槛

1. 为每个候选建立独立、可重放的 Boolean property 或等价判定器，并记录它与 SMARTIAN bug oracle 的映射。
2. 冻结目标字节码、ABI、编译器、预算、重复次数和输出目录命名规则；没有 seed CLI 时以运行编号和完整环境快照代替 seed。
3. 先做一次小规模重复性检查（建议每个目标 3 次），确认退出码、静态分析完成和输出解析稳定。
4. 只有通过上述门槛的候选，才可把 `fuzzing_status` 从 `not_started` 改为正式运行状态；本校准不改变候选注册表。

当前结论：SMARTIAN 已达到“可运行基线”状态，但尚未达到“与 C2 属性公平可比”状态。下一步应做 oracle/property 对齐，而不是直接扩大全量 fuzzing。
