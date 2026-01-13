# OpenPulse - 开源社区数据分析平台

## 项目简介

OpenPulse 是一个开源项目数据分析平台，通过可视化展示 GitHub 项目的 Star、Fork、Watch、Issue、Comment 等数据趋势，帮助开发者了解开源项目的发展状况。

## 当前功能

### 已完成 ✅
- 项目搜索（按关键词、Star数量过滤）
- Star/Fork/Watch 趋势图表
- 项目摘要数据展示
- 深色主题现代 UI

### 开发中 🚧
- 贡献者分布分析
- Comment 数据展示
- 项目详情页完善

### 规划中 📋
- 社区健康度评分
- 贡献者关系网络图
- 项目对比功能

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **MySQL** - 数据存储
- **Pydantic** - 数据验证

### 前端
- **React 18** - UI 框架
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Recharts** - 图表库
- **Axios** - HTTP 客户端

## 快速开始

### 1. 环境准备

- Python 3.10+
- Node.js 18+
- MySQL 8.0+ (或 Docker)

### 2. 启动 MySQL

```bash
# 使用 Docker 启动 MySQL
docker run -d \
  --name openpulse_mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=github_data \
  -p 3306:3306 \
  mysql:8.0
```

### 3. 配置环境变量

后端环境变量（创建 `backend/.env` 文件）：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=github_data
```

爬虫环境变量（创建项目根目录 `.env` 文件）：

```env
GITHUB_TOKENS=your_token1,your_token2,your_token3
```

### 4. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端运行在 http://localhost:8000

API 文档：http://localhost:8000/docs

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000

## API 接口

### 搜索接口
- `GET /api/v1/search/projects` - 搜索项目
- `GET /api/v1/search/projects/list` - 获取项目列表

### 统计接口
- `GET /api/v1/stats/project/summary` - 项目摘要
- `GET /api/v1/stats/project/trends` - 项目趋势数据
- `GET /api/v1/stats/stars/trend` - Star 趋势
- `GET /api/v1/stats/forks/trend` - Fork 趋势
- `GET /api/v1/stats/watches/trend` - Watch 趋势
- `GET /api/v1/stats/contributors` - 贡献者分布

## 项目结构

```
openrankdata/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── infrastructure/ # 数据库连接
│   │   ├── models/         # Pydantic 模型
│   │   ├── repository/     # 数据访问层
│   │   ├── services/       # 业务逻辑层
│   │   └── config.py       # 配置
│   ├── main.py             # FastAPI 入口
│   └── requirements.txt
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面组件
│   │   └── App.jsx
│   └── package.json
├── data/                   # 爬取的数据
│   ├── comment_cleaned/   # 清洗后的评论数据
│   ├── star/              # Star 数据
│   ├── fork/              # Fork 数据
│   └── ...
└── crawl_*.py             # 数据爬虫脚本
```

## 数据来源

数据通过 GitHub API 爬取，包含 Top 300 开源项目的：
- Star/Fork/Watch 历史数据
- Issue 及评论数据
- 时间范围：2022-03 至 2023-03

## 许可证

MIT License
