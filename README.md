# OpenPulse

![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen) ![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-red) ![MySQL Version](https://img.shields.io/badge/MySQL-%3E%3D8.0-blue)[![EN](https://img.shields.io/badge/中文-README.md-orange)](README-CN.md)

> **Open Source Community Health Assessment & Visualization Platform** — Insight into community pulse, quantifying health levels.

![Project Demo](./images/table.png)

## Table of Contents

- [Background](#background)
- [Introduction](#introduction)
- [Core Features](#core-features)
- [Technical Architecture](#technical-architecture)
- [Installation & Deployment](#installation--deployment)
- [Usage Guide](#usage-guide)
- [Health Assessment Algorithm](#health-assessment-algorithm)
- [Roadmap](#roadmap)
- [Contribution](#contribution)
- [Team Roles](#team-roles)
- [License](#license)

## Background

In the rapidly evolving open source ecosystem, understanding the health and vitality of projects has become increasingly important for developers, maintainers, and organizations. **OpenPulse** was created to address this need, providing a comprehensive platform for open source community health assessment and visualization. By combining multi-dimensional metrics with intelligent analysis, OpenPulse offers deep insights into project sustainability and growth potential.

## Introduction

**OpenPulse** is an all-encompassing open source community health assessment platform. Through multi-dimensional visualization and intelligent analysis, it deeply mines the pulse and vitality of communities. The system integrates OpenDigger data and utilizes AI-driven agent collaboration for real-time analysis.

**Core Capabilities:**
- **Community Panorama** — Multi-dimensional health metrics presenting comprehensive health reports.
- **Lifecycle** — Historical backtracking + trend prediction, combined with OpenDigger data.
- **Intelligent Collaboration** — MaxKB agents assisting in data analysis.
- **Smart Search** — Trending leaderboards, intelligent sorting, and contributor profiling.

## Core Features

1. **Multi-dimensional Health Assessment**
   - Project Health Score (0-100)
   - Growth Metrics (Star/Fork trends)
   - Activity Monitoring (Commit/PR analysis)
   - Code Churn Assessment

2. **Interactive Visualization**
   - Collaboration network display
   - Historical trend charts and analysis

3. **Intelligent Analysis**
   - MaxKB agent collaboration
   ![AI Demo](./images/ai.png)

4. **Search & Discovery**
   - Daily trending project leaderboards
   - Intelligent sorting by activity and relevance
   - Contributor profiles and matching

## Technical Architecture

### Frontend Stack

| Technology | Purpose |
|------------|---------|
| React | Web Framework |
| Tailwind CSS | Styling Framework |
| Vite | Build Tool |

### Backend Stack

| Technology | Purpose |
|------------|---------|
| Python + FastAPI | Web Service Framework |
| Pandas / NumPy | Data Analysis |
| MySQL | Data Storage |
| OpenDigger API | Open Source Metrics Data |

### AI & Agents

| Technology | Purpose |
|------------|---------|
| MaxKB | Agent Collaboration |

## Installation & Deployment

### Requirements
- Python 3.8+
- Node.js 18+
- MySQL 8.0+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/YourUsername/OpenPulse.git 
cd OpenPulse
```

### 2. Backend Deployment
```bash
# Enter backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Create a .env file and add the following configuration:
```

| Variable | Description | Required |
|----------|-------------|:--------:|
| GITHUB_TOKEN | GitHub API Access Token | Yes |
| MYSQL_HOST | MySQL Host Address | Yes |
| MYSQL_USER | Database Username | Yes |
| MYSQL_PASSWORD | Database Password | Yes |
| MYSQL_DATABASE | Database Name (default: openrank) | No |
| OPENDIGGER_API | OpenDigger API Address | No |

*See `.env.example` for full configuration options.*

```bash
# Start backend service
python main.py
```

### 3. Frontend Deployment
```bash
# Return to root and enter frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access System
Open your browser and visit `http://127.0.0.1:5173` to enter the platform.

## Usage Guide

### Home & Search
- **Browse Trends** — View daily updated trending projects.
![项目演示](./images/trend.png)
- **Search Projects** — Enter project names, displayed sorted by relevance and activity.
![Search Demo](./images/search.png)

### Project Dashboard
- **Overview** — Observe tightness line charts and activity histograms.
- **Health Analysis** — View the health score calculated using the PHAM model.
![Health Demo](./images/health.png)

### Network Interaction
- **Similar Projects** — View projects with similar health scores in the list.
![Similar Demo](./images/similar.png)
- **Contribution Details** — View contributors of the project.
![Contributor Demo](./images/contributer.png)
![Tech Stack Demo](./images/techstack.png)

**Intelligent Q&A** — Use the agent to get project analysis.

## Health Assessment Algorithm

### PHAM - Project Health Assessment Model
The core algorithm that quantifies open source project health, outputting a score from **0 to 100**.

### General Formula
$$ M = 0.2 \times Growth + 0.4 \times Activity + 0.2 \times Contribution + 0.2 \times Code $$

### Four-Dimensional Assessment System

| Dimension | Weight | Core Metric | Description |
|-----------|:------:|-------------|-------------|
| **Growth** | 20% | Star / Fork Growth Rate | Community Interest Heat |
| **Activity** | 40% | Commit Trend + OpenDigger | Development Activity (Core) |
| **Contribution** | 20% | PR Trend | Community Contribution Heat |
| **Code Churn** | 20% | Code Churn (Logarithmic) | Development Throughput |

### Detailed Calculation Logic

#### ⭐ Growth (Interest Growth) — 20%
- **Star Growth Rate**: $x = (\text{This Month Star} / (\text{Prev 3 Months Avg Star} + 1)) \times 100$
- **Fork Growth Rate**: $y = (\text{This Month Fork} / (\text{Prev 3 Months Avg Fork} + 1)) \times 100$

$$ Score\_Growth = 0.5 \times \min(x, 200)/2 + 0.5 \times \min(y, 200)/2 $$

⚠️ *Growth rate capped at 200% (Score 100) to prevent small projects from exploding scores due to small baselines.*

#### 🔥 Activity — 40%
- **Commit Trend**:
  $$ Ratio\_z = (\text{Last Week Avg Commit} + 1) / (\text{This Month Avg Commit} + 1) $$
  $$ Score\_z = \text{clamp}(0, 100, 50 + (Ratio\_z - 1) \times 50) $$

- **OpenDigger Activity**:
  $$ Score\_m = \min(100, OpenDigger\_Activity \times 10) $$

- **Final Score**:
  $$ Score\_Activity = 0.3 \times Score\_z + 0.7 \times Score\_m $$

| Ratio Value | Meaning | Score Trend |
|:-----------:|---------|:-----------:|
| > 1 | Activity Rising ↑ | > 50 |
| = 1 | Stable → | = 50 |
| < 1 | Activity Falling ↓ | < 50 |

#### 🤝 Contribution — 20%
$$ Ratio\_n = (\text{Last Week Avg PR} + 1) / (\text{This Month Avg PR} + 1) $$
$$ Score\_Contrib = \text{clamp}(0, 100, 50 + (Ratio\_n - 1) \times 50) $$

#### 💻 Code Churn (Code Health) — 20%
- **Total Churn**: $q = \text{Lines Added} + \text{Lines Deleted}$
$$ Score\_Code = \min(100, 20 \times \log_{10}(q + 1)) $$

| Churn $q$ | $\log_{10}(q+1)$ | Score |
|:---------:|:----------------:|:-----:|
| 100 Lines | ≈ 2 | 40 |
| 1,000 Lines | ≈ 3 | 60 |
| 10,000 Lines | ≈ 4 | 80 |
| 100,000 Lines | ≈ 5 | 100 |

### Algorithm Implementation

```python
import math

def calculate_health_score(data):
    """
    Calculate Project Health Score
    
    Args:
        data: dict, containing the following fields:
            - star_current_month      New Stars this month
            - star_avg_prev_3m        Avg Stars previous 3 months
            - fork_current_month      New Forks this month
            - fork_avg_prev_3m        Avg Forks previous 3 months
            - commit_avg_last_week    Avg Commits last week
            - commit_avg_month        Avg Commits this month
            - opendigger_activity     OpenDigger Activity Metric
            - pr_avg_last_week        Avg PRs last week
            - pr_avg_month            Avg PRs this month
            - pull_additions          Lines of code added
            - pull_deletions          Lines of code deleted
    
    Returns:
        float: Health Score (0-100)
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

## Project Backend Errors
When backend data fails to transmit to the frontend, a prompt will appear on the frontend, allowing developers to improve the backend based on this hint.
![Error Demo](./images/error.png)

## Roadmap

- [x] Basic Framework Setup
- [x] Health Assessment Algorithm Implementation
- [x] Visualization Engine Development
- [x] OpenDigger Data Integration
- [x] Multi-Agent Collaboration Workflow Refinement
- [ ] Optimize 3D Rendering Performance
- [ ] Integrate More Open Source Data Sources
- [ ] Mobile Adaptation
- [ ] Support Custom Weight Configuration

## Contribution

Contributions via Issues and Pull Requests are welcome. Before submitting, please ensure:
1. Issue description is clear and complete.
2. Pull Request contains detailed explanation.
3. Code follows project standards.
4. Necessary test cases are provided.

## Team Roles

- Leader:**[@Robert4063 杨家辉](https://github.com/Robert4063)** — React frontend framework construction, GitHub Issue/Comments data crawling/cleaning and dimension import, OpenDigger data crawling, backend tech stack/database connection and architecture, frontend-backend response system construction, conceptualizing the 4-dimensional assessment system, building the PHAM v2.0 model, contributor analysis dimension decision-making.
- Member:**[@pyf060502-glitch 庞毅飞](https://github.com/pyf060502-glitch)** — MaxKB agent local deployment, network connection and (knowledge base, model) construction, GitHub Star/Fork data crawling/cleaning/organization, feasibility analysis of PHAM v2.0 model construction, market demand research and related data analysis, PPT production and report writing.

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <strong>OpenPulse</strong> — Insight into the pulse and vitality of the open source community
</p>
