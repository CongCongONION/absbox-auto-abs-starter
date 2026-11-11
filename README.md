# Auto ABS Starter — 用 AbsBox 搭的汽车贷款证券化现金流模型

一个**已经实际跑通**的 starter 项目：用开源库 [AbsBox](https://github.com/yellowbean/AbsBox)
（后端引擎 Hastructure）建模一笔简化的 Auto ABS，做情景分析和 CDR×CPR 敏感性分析。

> 数据全部为合成的代表性资产池（rep lines），不是真实交易。
> 真实交易参考：AbsBox 文档里的 BMW Auto Deal 2023-01（revolving 结构，复杂度高得多），
> 本项目是它的简化学习版：静态池 + 顺序支付（sequential pay）。

## 交易结构

| 部分 | 设定 |
|---|---|
| 资产池 | $100mm 汽车贷款，用 3 条 `Installment` 代表线：prime $50mm / near-prime $30mm / subprime $20mm |
| Class A（senior） | $85mm，固定 5.00%，sequential |
| Class B（mezz） | $10mm，固定 7.50%，sequential |
| Class E（equity） | $5mm，无票息，拿剩余现金流 → A 的次级保护 = 15% |
| 费用 | servicer fee 1.00%/年（按池余额），trustee 固定费 $25,000 |
| Waterfall | 费用 → A 利息 → B 利息 → A 本金 → B 本金 → E 本金 → 剩余给 E |

**关键口径（踩过的坑）**：`Installment` 资产的 `feeRate` 是**按月、按原始余额的固定费率**
（fee/月 = originBalance × feeRate，引擎实测验证），不是 APR。
本项目 prime 0.30%/月 ⇒ 全期总财务费用 = 0.30% × 60 期 = 原始余额的 18%。

## 实测结果（2026-11-10 本地引擎真实运行，见 `outputs/`）

| 情景 | 假设 (CDR/CPR/回收率/滞后) | 结果 |
|---|---|---|
| Base | 1.5% / 8% / 35% / 4月 | 三档全额偿还；A WAL 1.66y，B 3.77y，E 拿回 $5mm + 剩余 $2.16mm |
| Optimistic | 0.8% / 12% / 45% / 3月 | 三档全额偿还；A WAL 缩短到 1.56y |
| Stress | 4.0% / 5% / 25% / 6月 | 池累计损失 $6.19mm；**E 本金损失 $2.03mm（40.6%）、剩余为 0；A、B 仍全额偿还** — 次级保护按设计生效 |

敏感性网格（`outputs/sensitivity_grid.csv`，CDR 0.5%–5% × CPR 3%–15%）：
- A 在所有格子里零损失；B 只在极端角（CDR 5% + CPR 15%）出现 $1.54mm 损失；
- 一个值得讲的现象：**CPR 越高，E 损失反而越大** — 提前还款抽走的是还在付费的优质贷款，
  excess spread 变薄，吸收损失的垫子就变薄。这是面试里能展开讲的点。

## 怎么跑

版本必须对齐（AbsBox 官方规则：absbox 与引擎的 minor 版本要一致）：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # absbox==0.50.3

# 终端 1：启动本地引擎（首次会自动下载 Hastructure 0.50.2 二进制 + config.yml）
bash engine/start_engine.sh            # http://localhost:8081

# 终端 2：
python src/run_scenarios.py            # 三情景 -> outputs/scenario_summary.csv, summary.md
python src/sensitivity.py              # CDR x CPR 网格 -> outputs/sensitivity_grid.csv
```

为什么用本地引擎：2026-11-10 实测公共引擎 `https://absbox.org/api/latest` 返回 **502 Bad Gateway**；
本地二进制（absbox 0.50.3 + Hastructure 0.50.2）连接和运行都已验证通过。

## 文件结构

```
src/auto_abs_deal.py   # 交易定义（池/债券/费用/waterfall/情景假设）
src/run_scenarios.py   # 三情景运行 + WAL/损失汇总
src/sensitivity.py     # CDR x CPR 敏感性网格
engine/start_engine.sh # 本地引擎一键启动
outputs/               # 引擎实际输出的现金流 CSV + 汇总
```

## 下一步可以加什么（按价值排序）

1. **分段假设**：现在三条代表线共用一组 CDR/CPR；改成按 segment 分别设假设
   （subprime CDR 更高），用 AbsBox 的 by-index / by-tag 假设功能。
2. **Trigger**：加累计损失 trigger，触发后 turbos（全部本金先还 A），对比有无 trigger 时 B 的损失。
3. **Reserve account**：加固定目标 $1mm 储备账户，看 stress 下 B 是否还能全额偿还。
4. **定价**：给每档加 pricing 假设出 IRR/PV，和 WAL 一起做成完整的 tranche 分析表。
5. **对标真实交易**：把 BMW 2023-01 的 revolving 结构（文档有完整代码）跑通，和本项目逐项对照。
