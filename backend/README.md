# OpenPulse Backend

GitHub开源数据搜索与可视化系统 - 后端服务

## 架构

```
backend/
├── app/
│   ├── api/                    # 对外接口（HTTP）
│   │   ├── search.py            # 搜索类接口
│   │   └── stats.py             # 图表/统计接口
│   ├── services/               # 业务编排（不写 SQL）
│   │   └── search_service.py
│   ├── repository/             # 纯数据库访问
│   │   └── github_repo.py
│   ├── models/
│   │   └── schemas.py           # Pydantic 返回模型
│   ├── infrastructure/
│   │   └── database.py          # MySQL 连接池
│   └── config.py
└── main.py                     # FastAPI 入口
```

## 环境配置

创建 `.env` 文件（可选，默认使用以下配置）：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=github_data
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### 搜索接口

- `GET /api/v1/search/repositories` - 搜索仓库
  - 参数：keyword, stars_min, stars_max, forks_min, forks_max, limit, offset

### 统计接口

- `GET /api/v1/stats/commits/trend` - 获取提交趋势图数据
  - 参数：repo_id 或 repo_name, start_date, end_date, group_by

- `GET /api/v1/stats/contributors` - 获取贡献者分布数据
  - 参数：repo_id 或 repo_name, top_n
