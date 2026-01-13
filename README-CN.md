# OpenPulse

[![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-red)](https://www.python.org/)[![MySQL](https://img.shields.io/badge/MySQL-%3E%3D8.0-blue)](https://www.mysql.com/)[![EN](https://img.shields.io/badge/English-README.md-orange)](README.md)

> **开源社区健康评估与可视化平台** — 洞察社区脉搏，量化健康程度

## 目录
- [背景](#背景)
- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [健康评估算法](#健康评估算法)
- [开发计划](#开发计划)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

## 背景
在快速发展的开源生态系统中，理解项目的健康状况和活力对于开发者、维护者和组织来说变得越来越重要。OpenPulse 正是为解决这一需求而创建，提供一个全面的开源社区健康评估与可视化平台。通过结合多维度指标与智能分析，OpenPulse 为项目的可持续性和增长潜力提供深度洞察。

## 项目简介
**OpenPulse** 是一个全方位的开源社区健康评估平台，通过多维度可视化与智能分析，深度挖掘社区的脉搏与生命力。系统集成 OpenDigger 数据，并利用 AI 驱动的多智能体协作进行实时分析。

**核心能力：**
- **社区全景** — 多维健康度量，3D可视化协作关系
- **生命周期** — 历史回溯 + 趋势预测，结合 OpenDigger 数据
- **智能协作** — MaxKB 智能体协助数据分析
- **智能搜索** — 热度榜单、智能排序、贡献者画像

## 核心功能
![项目演示](./images/table.png)
1. **多维度健康评估**
   - 项目健康评分（0-100分）
   - 增长指标（Star/Fork 趋势）
   - 活跃度监控（Commit/PR 分析）
   - 代码变动量评估

2. **交互式可视化**
   - 展示协作网络
   - 历史趋势图与分析

3. **智能分析**
   - MaxKB 智能体协作
  ![项目演示](./images/ai.png)

4. **搜索与发现**
   - 每日热门项目排行榜
   - 按活跃度和匹配度智能排序
   - 贡献者画像与匹配

## 技术架构

### 前端技术栈
| 技术 | 用途 |
|------|------|
| React | Web 框架 |
| D3.js / Three.js | 可视化引擎（3D 球状图） |
| Tailwind CSS | 样式框架 |
| Vite | 构建工具 |

### 后端技术栈
| 技术 | 用途 |
|------|------|
| Python + FastAPI | Web 服务框架 |
| Pandas / NumPy | 数据分析 |
| MySQL | 数据存储 |
| OpenDigger API | 开源指标数据 |

### AI 与智能体
| 技术 | 用途 |
|------|------|
| MaxKB | 智能体协作 |

## 安装部署

### 环境要求
- Python 3.8+
- Node.js 18+
- MySQL 8.0+
- Git

### 1. 克隆仓库
```bash
git clone https://github.com/YourUsername/OpenPulse.git
cd OpenPulse
```

### 2. 后端部署
```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
# 创建 .env 文件并添加以下配置：
```

| 变量 | 说明 | 必填 |
|------|------|:----:|
| `GITHUB_TOKEN` | GitHub API 访问令牌 | 是 |
| `MYSQL_HOST` | MySQL 数据库地址 | 是 |
| `MYSQL_USER` | 数据库用户名 | 是 |
| `MYSQL_PASSWORD` | 数据库密码 | 是 |
| `MYSQL_DATABASE` | 数据库名称（默认 `openrank`） | 否 |
| `OPENDIGGER_API` | OpenDigger 数据接口地址 | 否 |

完整配置项参考 `.env.example`

```bash
# 启动后端服务
python main.py
```

### 3. 前端部署
```bash
# 返回项目根目录并进入前端目录
cd ../frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统
在浏览器中访问 `http://127.0.0.1:5173` 进入平台。

## 使用指南

### 首页与搜索
- **浏览热榜** — 查看每日更新的热门项目
- **搜索项目** — 输入项目名称，按匹配度和活跃度排序展示
![项目演示](./images/search.png)
### 项目大屏
- **总览图** — 观察紧密度折线图、活跃度直方图
- **健康度分析** — 查看这个项目在PHAM模型下面计算得出来的健康程度
![项目演示](./images/health.png)
### 关系网络交互
- **查看健康度相似的项目** — 在列表中查看健康度相似的项目
![项目演示](./images/similar.png)
- **贡献详情** — 观看这个项目的贡献者
![项目演示](./images/contributer.png)
 **智能问答** — 使用智能体获取项目分析


## 健康评估算法

### PHAM - 项目健康评估模型
核心算法，量化评估开源项目健康程度，输出 **0 ~ 100** 分。

### 总体公式
```
M = 0.2 × Growth + 0.4 × Activity + 0.2 × Contribution + 0.2 × Code
```

### 四维评估体系

| 维度 | 权重 | 核心指标 | 说明 |
|------|:----:|----------|------|
| **Growth** | 20% | Star / Fork 增长率 | 社区关注热度 |
| **Activity** | 40% | Commit 趋势 + OpenDigger | 开发活跃度（核心） |
| **Contribution** | 20% | PR 趋势 | 社区贡献热度 |
| **Code Churn** | 20% | 代码变动量（对数） | 开发吞吐量 |

### 详细计算逻辑

#### ⭐ Growth（关注度增长）— 20%
```
Star 增长率:  x = (本月Star / (前3月平均Star + 1)) × 100
Fork 增长率:  y = (本月Fork / (前3月平均Fork + 1)) × 100

Score_Growth = 0.5 × min(x, 200)/2 + 0.5 × min(y, 200)/2

⚠️ 增长率上限 200%（得分 100），防止小项目因基数小导致分数爆炸
```

#### 🔥 Activity（活跃度）— 40%
```
Commit 趋势:
Ratio_z = (最后一周平均Commit + 1) / (本月平均Commit + 1)
Score_z = clamp(0, 100, 50 + (Ratio_z − 1) × 50)

OpenDigger 活跃度:
Score_m = min(100, OpenDigger_Activity × 10)

最终得分:
Score_Activity = 0.3 × Score_z + 0.7 × Score_m
```

| Ratio 值 | 含义 | 得分趋势 |
|:--------:|------|:--------:|
| `> 1` | 活跃度上升 ↑ | `> 50` |
| `= 1` | 保持稳定 → | `= 50` |
| `< 1` | 活跃度下降 ↓ | `< 50` |

#### 🤝 Contribution（贡献度）— 20%
```
Ratio_n = (最后一周平均PR + 1) / (本月平均PR + 1)
Score_Contrib = clamp(0, 100, 50 + (Ratio_n − 1) × 50)
```

#### 💻 Code Churn（代码健康度）— 20%
```
总变动量:  q = 代码添加行数 + 代码删除行数
Score_Code = min(100, 20 × log₁₀(q + 1))
```

| 变动量 q | log₁₀(q+1) | 得分 |
|:--------:|:----------:|:----:|
| 100 行 | ≈ 2 | 40 |
| 1,000 行 | ≈ 3 | 60 |
| 10,000 行 | ≈ 4 | 80 |
| 100,000 行 | ≈ 5 | 100 |

### 算法实现

```python
import math

def calculate_health_score(data):
    """
    计算项目健康度评分
    
    Args:
        data: dict, 包含以下字段:
            - star_current_month      本月新增 Star 数
            - star_avg_prev_3m        前三个月平均 Star 数
            - fork_current_month      本月新增 Fork 数
            - fork_avg_prev_3m        前三个月平均 Fork 数
            - commit_avg_last_week    最后一周平均 Commit 数
            - commit_avg_month        本月平均 Commit 数
            - opendigger_activity     OpenDigger Activity 指标
            - pr_avg_last_week        最后一周平均 PR 数
            - pr_avg_month            本月平均 PR 数
            - pull_additions          代码添加行数
            - pull_deletions          代码删除行数
    
    Returns:
        float: 健康度评分 (0-100)
    """
    
    # 1. Growth (Star & Fork) - 20%
    s_score = min((data['star_current_month'] / (data['star_avg_prev_3m'] + 1)) * 100, 200) / 2
    f_score = min((data['fork_current_month'] / (data['fork_avg_prev_3m'] + 1)) * 100, 200) / 2
    score_growth = 0.5 * s_score + 0.5 * f_score

    # 2. Activity (Commit & OpenDigger) - 40%
    c_ratio = (data['commit_avg_last_week'] + 1) / (data['commit_avg_month'] + 1)
    score_z = max(0, min(100, 50 + (c_ratio - 1) * 50))
    score_m = min(100, data['opendigger_activity'] * 10)
    score_activity = 0.3 * score_z + 0.7 * score_m

    # 3. Contribution (PR Trend) - 20%
    p_ratio = (data['pr_avg_last_week'] + 1) / (data['pr_avg_month'] + 1)
    score_contrib = max(0, min(100, 50 + (p_ratio - 1) * 50))

    # 4. Code Churn - 20%
    total_churn = data['pull_additions'] + data['pull_deletions']
    score_code = min(100, 20 * math.log10(total_churn + 1))

    # Final Aggregation
    final_score = (
        0.2 * score_growth +
        0.4 * score_activity +
        0.2 * score_contrib +
        0.2 * score_code
    )

    return round(final_score, 2)
```

##项目后台报错
后端数据无法传输到前端的时候，会在前端弹出一个提示，开发人员可通过这个提示进行后端的改进
![项目演示](./images/error.png)

## 开发计划
- [x] 基础框架搭建
- [x] 健康评估算法实现
- [x] 可视化引擎开发
- [x] OpenDigger 数据集成
- [×] 完善多智能体协作流程
- [ ] 优化 3D 渲染性能
- [ ] 接入更多开源数据源
- [ ] 推出移动端适配版本
- [ ] 支持自定义权重配置

## 参与贡献
欢迎提交 Issue 和 Pull Request 参与项目改进。提交前请确保：
1. Issue 描述清晰完整
2. Pull Request 包含详细说明
3. 代码符合项目规范
4. 提供必要的测试用例

## 许可证
本项目采用 [MIT License](LICENSE) 许可证。

---

<p align="center">
<strong>OpenPulse</strong> — 洞察开源社区的脉搏与生命力
</p>
