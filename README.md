# OpenPulse

[![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-red)](https://www.python.org/)[![MySQL](https://img.shields.io/badge/MySQL-%3E%3D8.0-blue)](https://www.mysql.com/)[![CN](https://img.shields.io/badge/简体中文-README--CN.md-orange)](README-CN.md)

> **Open Source Community Health Assessment & Visualization Platform** — Insight into Community Pulse, Quantifying Vitality

## Table of Contents
- [Background](#background)
- [Introduction](#introduction)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Health Assessment Algorithm](#health-assessment-algorithm)
- [Development Plan](#development-plan)
- [Contributing](#contributing)
- [License](#license)

## Background
In the rapidly evolving open source ecosystem, understanding the health and vitality of a project has become increasingly important for developers, maintainers, and organizations. OpenPulse was created to address this need by providing a comprehensive platform for assessing and visualizing open source community health. By combining multi-dimensional metrics with intelligent analysis, OpenPulse offers deep insights into project sustainability and growth potential.

## Introduction
OpenPulse is a comprehensive open source community health assessment platform that provides multi-dimensional visualization and intelligent analysis to deeply explore the pulse and vitality of communities. The system integrates with OpenDigger data and leverages AI-powered multi-agent collaboration for real-time analysis.

**Core Capabilities:**
- **Community Panorama** — Multi-dimensional health metrics with cyber-style collaboration visualization
- **Lifecycle Analysis** — Historical retrospection + trend prediction with OpenDigger data integration
- **Intelligent Collaboration** — MaxKB multi-agent real-time analysis and proactive governance
- **Smart Search** — Trending rankings, intelligent sorting, six-dimensional contributor profiling

## Features

1. **Multi-dimensional Health Assessment**
   - Project Health Score (0-100)
   - Growth metrics (Star/Fork trends)
   - Activity monitoring (Commit/PR analysis)
   - Code churn evaluation

2. **Interactive Visualization**
   - Force-directed graph for collaboration networks
   - 3D cyber-style relationship spheres
   - Historical trend charts with predictions
   - Six-dimensional radar charts for contributors

3. **Intelligent Analysis**
   - MaxKB multi-agent collaboration
   - NLP-based sentiment analysis for relationships
   - Epidemiological model for trend prediction
   - Personalized project recommendations

4. **Search & Discovery**
   - Daily trending projects leaderboard
   - Smart ranking by activity and relevance
   - Contributor profiling and matching

## Technical Architecture

### Frontend Stack
| Technology | Purpose |
|------------|---------|
| React | Web Framework |
| D3.js / Three.js | Visualization Engine (3D Cyber Sphere) |
| Tailwind CSS | Styling Framework |
| Vite | Build Tool |

### Backend Stack
| Technology | Purpose |
|------------|---------|
| Python + FastAPI | Web Service Framework |
| Pandas / NumPy | Data Analysis |
| MySQL | Data Storage |
| OpenDigger API | Open Source Metrics |

### AI & Agents
| Technology | Purpose |
|------------|---------|
| MaxKB | Multi-agent Collaboration |
| NLP Models | Sentiment Analysis |
| Epidemiological Models | Trend Prediction |

## Installation

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

### 2. Backend Setup
```bash
# Enter backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with the following:
```

| Variable | Description | Required |
|----------|-------------|:--------:|
| `GITHUB_TOKEN` | GitHub API access token | Yes |
| `MYSQL_HOST` | MySQL database address | Yes |
| `MYSQL_USER` | Database username | Yes |
| `MYSQL_PASSWORD` | Database password | Yes |
| `MYSQL_DATABASE` | Database name (default: `openrank`) | No |
| `OPENDIGGER_API` | OpenDigger data API address | No |

See `.env.example` for complete configuration reference.

```bash
# Start backend service
python main.py
```

### 3. Frontend Setup
```bash
# Return to project root and enter frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access System
Visit `http://127.0.0.1:5173` in your browser to access the platform.

## Usage Guide

### Home & Search
- **Browse Trending** — View daily updated popular projects
- **Search Projects** — Input project name, results sorted by match and activity

### Project Dashboard
- **Overview Chart** — View closeness line charts and activity histograms
- **Prediction Analysis** — Check future trend predictions (dashed lines)

### Relationship Network
- **Personnel Relations** — View collaboration networks in 3D sphere
- **Contribution Details** — Click spheres to view six-dimensional radar charts
- **AI Q&A** — Use intelligent agents for project analysis

## Health Assessment Algorithm

### PHAM - Project Health Assessment Model
Core algorithm that quantifies open source project health with a score from **0 to 100**.

### Overall Formula
```
M = 0.2 × Growth + 0.4 × Activity + 0.2 × Contribution + 0.2 × Code
```

### Four-Dimensional Assessment System

| Dimension | Weight | Core Metrics | Description |
|-----------|:------:|--------------|-------------|
| **Growth** | 20% | Star/Fork growth rate | Community attention |
| **Activity** | 40% | Commit trends + OpenDigger | Development activity (core) |
| **Contribution** | 20% | PR trends | Community contribution |
| **Code Churn** | 20% | Code changes (logarithmic) | Development throughput |

### Detailed Calculation Logic

#### ⭐ Growth (Attention Growth) — 20%
```
Star Growth Rate:  x = (Current Month Star / (Avg 3-Month Star + 1)) × 100
Fork Growth Rate:  y = (Current Month Fork / (Avg 3-Month Fork + 1)) × 100

Score_Growth = 0.5 × min(x, 200)/2 + 0.5 × min(y, 200)/2

⚠️ Growth rate capped at 200% (score 100) to prevent small projects from score explosion
```

#### 🔥 Activity — 40%
```
Commit Trend:
Ratio_z = (Last Week Avg Commit + 1) / (Month Avg Commit + 1)
Score_z = clamp(0, 100, 50 + (Ratio_z − 1) × 50)

OpenDigger Activity:
Score_m = min(100, OpenDigger_Activity × 10)

Final Score:
Score_Activity = 0.3 × Score_z + 0.7 × Score_m
```

| Ratio Value | Meaning | Score Trend |
|:-----------:|---------|:-----------:|
| `> 1` | Activity Rising ↑ | `> 50` |
| `= 1` | Stable → | `= 50` |
| `< 1` | Activity Declining ↓ | `< 50` |

#### 🤝 Contribution — 20%
```
Ratio_n = (Last Week Avg PR + 1) / (Month Avg PR + 1)
Score_Contrib = clamp(0, 100, 50 + (Ratio_n − 1) × 50)
```

#### 💻 Code Churn — 20%
```
Total Churn: q = Lines Added + Lines Deleted
Score_Code = min(100, 20 × log₁₀(q + 1))
```

| Churn q | log₁₀(q+1) | Score |
|:-------:|:----------:|:-----:|
| 100 lines | ≈ 2 | 40 |
| 1,000 lines | ≈ 3 | 60 |
| 10,000 lines | ≈ 4 | 80 |
| 100,000 lines | ≈ 5 | 100 |

### Algorithm Implementation

```python
import math

def calculate_health_score(data):
    """
    Calculate project health score
    
    Args:
        data: dict containing:
            - star_current_month      Current month new Stars
            - star_avg_prev_3m        Average Stars over previous 3 months
            - fork_current_month      Current month new Forks
            - fork_avg_prev_3m        Average Forks over previous 3 months
            - commit_avg_last_week    Average Commits last week
            - commit_avg_month        Average Commits this month
            - opendigger_activity     OpenDigger Activity metric
            - pr_avg_last_week        Average PRs last week
            - pr_avg_month            Average PRs this month
            - pull_additions          Lines added
            - pull_deletions          Lines deleted
    
    Returns:
        float: Health score (0-100)
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

## Development Plan
- [x] Basic framework setup
- [x] Health assessment algorithm implementation
- [x] Visualization engine development
- [x] OpenDigger integration
- [ ] Enhanced multi-agent collaboration workflow
- [ ] 3D rendering performance optimization
- [ ] Additional open source data source integration
- [ ] Mobile-responsive version
- [ ] Custom weight configuration support

## Contributing
Welcome to submit Issues and Pull Requests to participate in project improvement. Before submitting, please ensure:
1. Issue description is clear and complete
2. Pull Request includes detailed explanation
3. Code complies with project standards
4. Necessary test cases are provided

## License
This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
<strong>OpenPulse</strong> — Insight into Open Source Community Pulse and Vitality
</p>
