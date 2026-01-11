# Project Health Assessment Model (PHAM)

## 1. 简介 / Overview

本项目用于评估开源项目的健康程度。

原有的评估模型存在量纲不统一、负分风险等问题。本文档定义了 **v2.0 改进版** 计算逻辑。

该算法基于四个维度进行加权评分，最终输出一个 **0 ~ 100 分** 的健康度数值 ***M***。

### 核心改进点

- **归一化处理**：所有指标均映射到 0-100 或 0-1 区间，防止某个数值过大主导结果。
- **防错处理**：所有作为分母的数值均加入平滑因子（epsilon），防止 Division by Zero。
- **逻辑修正**：修正了代码变动（Code Churn）的计算方式，不再惩罚重构行为。

---

## 2. 输入数据定义 / Input Data Dictionary

后端需要准备以下原始数据（Raw Data）：

| 符号 | 变量名 (建议) | 描述 | 类型 | 备注 |
|:----:|--------------|------|:----:|------|
| **Star** | | | | |
| Sᶜᵘʳ | `star_current_month` | 本月新增 Star 数 | Int | |
| Sₐᵥₘ | `star_avg_prev_3m` | 前三个月平均 Star 数 | Float | |
| **Fork** | | | | |
| Fᶜᵘʳ | `fork_current_month` | 本月新增 Fork 数 | Int | |
| Fₐᵥₘ | `fork_avg_prev_3m` | 前三个月平均 Fork 数 | Float | |
| **Activity (Commit)** | | | | |
| Cₗₐₛₜ | `commit_avg_last_week` | 最后一周平均 Commit 数 | Float | |
| Cₘₒₙₜₕ | `commit_avg_month` | 本月平均 Commit 数 | Float | |
| m | `opendigger_activity` | OpenDigger Activity 指标 | Float | 外部数据源 |
| **Contribution (PR)** | | | | |
| Pₗₐₛₜ | `pr_avg_last_week` | 最后一周平均 PR 数 | Float | |
| Pₘₒₙₜₕ | `pr_avg_month` | 本月平均 PR 数 | Float | |
| **Code Churn** | | | | |
| add | `pull_additions` | 代码添加行数 | Int | |
| del | `pull_deletions` | 代码删除行数 | Int | |

---

## 3. 计算逻辑详细说明 / Calculation Logic

最终分数 **M** 由四个部分加权组成：

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   M  =  0.2 × Score_Growth  +  0.4 × Score_Activity  +  0.2 × Score_Contrib     │
│                                                                                 │
│                             +  0.2 × Score_Code                                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.1 关注度增长 (Growth) — 权重 20%

**逻辑**：计算相对于前三个月的增长率。

**限制**：增长率上限设为 200%（即得分为 100），防止小项目因基数小导致分数爆炸。

#### 计算 Star 增长得分

```
            Sᶜᵘʳ
    x  =  ─────────  ×  100
          Sₐᵥₘ + 1
```

> ⚠️ 注意：分母加 1 防止除零。

```
                min(x, 200)
    Score_x  =  ───────────
                    2
```

（将 0-200 的范围映射回 0-100 分）

#### 计算 Fork 增长得分

```
            Fᶜᵘʳ
    y  =  ─────────  ×  100
          Fₐᵥₘ + 1
```

```
                min(y, 200)
    Score_y  =  ───────────
                    2
```

#### 最终 Growth 得分

```
    Score_Growth  =  0.5 × Score_x  +  0.5 × Score_y
```

---

### 3.2 活跃度 (Activity) — 权重 40%

**逻辑**：结合 Commit 的近期趋势（是否在加速开发）和 OpenDigger 的综合活跃度。

#### 计算 Commit 趋势 (z)

```
              Cₗₐₛₜ + 1
    Ratio_z = ──────────
              Cₘₒₙₜₕ + 1
```

- 若 `Ratio > 1` → 活跃度在 **上升** ↑
- 若 `Ratio < 1` → 活跃度在 **下降** ↓

映射到 0-100 分：

```
    Score_z  =  min( 100,  max( 0,  50 + (Ratio_z − 1) × 50 ))
```

> 💡 解释：基准分 50。如果最后一周是本月平均的 2 倍，得 100 分；如果是 0，得 0 分。

#### OpenDigger 活跃度 (m)

假设 OpenDigger 的 activity 正常范围是 0~10，极大值可能到 20+。

```
    Score_m  =  min( 100,  m × 10 )
```

> 📝 建议：根据实际数据分布调整系数 10，目标是让优秀项目的得分在 80-100 之间。

#### 最终 Activity 得分

```
    Score_Activity  =  0.3 × Score_z  +  0.7 × Score_m
```

---

### 3.3 贡献度 (Contribution) — 权重 20%

**逻辑**：通过 PR (Pull Request) 的趋势判断社区贡献热度。

#### 计算 PR 趋势 (n)

```
              Pₗₐₛₜ + 1
    Ratio_n = ──────────
              Pₘₒₙₜₕ + 1
```

```
    Score_Contrib  =  min( 100,  max( 0,  50 + (Ratio_n − 1) × 50 ))
```

---

### 3.4 代码健康度 (Code Churn) — 权重 20%

**逻辑**：使用代码变动总量（Add + Del）衡量开发吞吐量。使用对数函数 log 平滑处理，鼓励活跃但边际效应递减。

#### 计算总变动量 (q)

```
    q  =  add  +  del
```

#### 计算对数得分

```
    Score_Code  =  min( 100,  20 × log₁₀(q + 1) )
```

#### 示例对应关系

| 变动量 q | log₁₀(q+1) | 得分 |
|:--------:|:----------:|:----:|
| 100 行 | ≈ 2 | 40 |
| 1,000 行 | ≈ 3 | 60 |
| 10,000 行 | ≈ 4 | 80 |
| 100,000 行 | ≈ 5 | 100 |

---

## 4. 公式速查表 / Formula Quick Reference

```
┌────────────────────────────────────────────────────────────────────────────────┐
│  📊 FINAL SCORE                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│    M = 0.2×Growth + 0.4×Activity + 0.2×Contrib + 0.2×Code                      │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│  ⭐ GROWTH (20%)                                                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│    Score_x = min(Sᶜᵘʳ/(Sₐᵥₘ+1)×100, 200) / 2                                  │
│    Score_y = min(Fᶜᵘʳ/(Fₐᵥₘ+1)×100, 200) / 2                                  │
│    Score_Growth = 0.5×Score_x + 0.5×Score_y                                    │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│  🔥 ACTIVITY (40%)                                                             │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│    Ratio_z = (Cₗₐₛₜ+1) / (Cₘₒₙₜₕ+1)                                            │
│    Score_z = clamp(0, 100, 50 + (Ratio_z−1)×50)                                │
│    Score_m = min(100, m×10)                                                    │
│    Score_Activity = 0.3×Score_z + 0.7×Score_m                                  │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│  🤝 CONTRIBUTION (20%)                                                         │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│    Ratio_n = (Pₗₐₛₜ+1) / (Pₘₒₙₜₕ+1)                                            │
│    Score_Contrib = clamp(0, 100, 50 + (Ratio_n−1)×50)                          │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│  💻 CODE CHURN (20%)                                                           │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│    q = add + del                                                               │
│    Score_Code = min(100, 20×log₁₀(q+1))                                        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 伪代码实现 / Reference Implementation (Python)

```python
import math

def calculate_health_score(data):
    """
    data: dict, containing all keys defined in Section 2
    """
    
    # ═══════════════════════════════════════════════════════════════
    # 1. Growth (Star & Fork)
    # ═══════════════════════════════════════════════════════════════
    # Formula: min((current / (avg + 1)) × 100, 200) / 2
    # Result range: 0 ~ 100
    
    s_score = min((data['star_current_month'] / (data['star_avg_prev_3m'] + 1)) * 100, 200) / 2
    f_score = min((data['fork_current_month'] / (data['fork_avg_prev_3m'] + 1)) * 100, 200) / 2
    
    score_growth = 0.5 * s_score + 0.5 * f_score

    # ═══════════════════════════════════════════════════════════════
    # 2. Activity (Commit & OpenDigger)
    # ═══════════════════════════════════════════════════════════════
    # Z-Trend Logic: Base 50, fluctuates based on ratio. Cap at 0-100.
    c_ratio = (data['commit_avg_last_week'] + 1) / (data['commit_avg_month'] + 1)
    score_z = max(0, min(100, 50 + (c_ratio - 1) * 50))
    
    # OpenDigger Logic: Scaling raw activity. 
    # Configurable Factor: 10 (Assumes activity ~10 is very good)
    score_m = min(100, data['opendigger_activity'] * 10)
    
    score_activity = 0.3 * score_z + 0.7 * score_m

    # ═══════════════════════════════════════════════════════════════
    # 3. Contribution (PR Trend)
    # ═══════════════════════════════════════════════════════════════
    p_ratio = (data['pr_avg_last_week'] + 1) / (data['pr_avg_month'] + 1)
    score_contrib = max(0, min(100, 50 + (p_ratio - 1) * 50))

    # ═══════════════════════════════════════════════════════════════
    # 4. Code Churn
    # ═══════════════════════════════════════════════════════════════
    # Logic: Logarithmic scale of total churn
    total_churn = data['pull_additions'] + data['pull_deletions']
    # +1 inside log to handle 0 changes
    score_code = min(100, 20 * math.log10(total_churn + 1))

    # ═══════════════════════════════════════════════════════════════
    # Final Aggregation
    # ═══════════════════════════════════════════════════════════════
    final_score = (
        0.2 * score_growth +
        0.4 * score_activity +
        0.2 * score_contrib +
        0.2 * score_code
    )

    return round(final_score, 2)
```

---

## 6. 配置与注意事项 / Config & Notes

### 平滑因子

所有除法运算分母必须 **+1**（或 +0.01），严禁直接除以变量。

### 权重调整

当前权重配置：

| 维度 | 权重 | 说明 |
|:----:|:----:|------|
| Growth | 20% | 关注度增长 |
| Activity | 40% | 开发活跃度 (核心指标) |
| Contribution | 20% | 社区贡献度 |
| Code | 20% | 代码健康度 |

> 💡 建议将这些权重定义为常量（CONST），方便后续根据业务需求调整。

### OpenDigger 归一化

`score_m` 的系数（当前为 10）可能需要根据实际抓取的 OpenDigger 数据分布进行微调：

| 情况 | 建议操作 |
|------|----------|
| 所有项目都满分 | ⬇️ **降低** 系数 |
| 所有项目都很低 | ⬆️ **提高** 系数 |
