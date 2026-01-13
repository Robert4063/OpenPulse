# OpenPulse - GitHub数据搜索与可视化系统

根据 `目标.txt` 中的架构设计，这是一个最小可用的GitHub开源数据搜索与可视化系统。

## 项目架构

```
openrankdata/
├── backend/              # FastAPI后端
│   ├── app/
│   │   ├── api/         # API接口层
│   │   ├── services/    # 业务服务层
│   │   ├── repository/  # 数据访问层
│   │   ├── models/      # 数据模型
│   │   └── infrastructure/  # 基础设施（数据库连接）
│   └── main.py
│
├── frontend/            # React前端
│   ├── src/
│   │   ├── api/        # API客户端
│   │   ├── pages/      # 页面组件
│   │   └── App.jsx
│   └── package.json
│
└── 目标.txt            # 架构设计文档
```

## 快速开始

### 前置要求

1. **Docker MySQL容器运行中**
   ```bash
   # 确保MySQL容器正在运行
   docker ps | grep mysql
   
   # 如果没有运行，启动容器
   docker run -d \
     --name openpulse_mysql \
     -e MYSQL_ROOT_PASSWORD=root \
     -e MYSQL_DATABASE=github_data \
     -p 3306:3306 \
     mysql:8.0
   ```

2. **Python 3.8+**
3. **Node.js 16+**

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

## 数据库配置

默认配置（可在 `backend/app/config.py` 或环境变量中修改）：

- **Host**: localhost
- **Port**: 3306
- **User**: root
- **Password**: root
- **Database**: github_data

### 环境变量（可选）

在 `backend/` 目录创建 `.env` 文件：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=github_data
```

## 功能特性

### 1. 搜索功能

- 按仓库名称关键词搜索
- 按Stars范围筛选
- 按Forks范围筛选
- 分页显示结果

**API**: `GET /api/v1/search/repositories`

### 2. 提交趋势图

- 按天/周/月查看提交趋势
- 时间范围筛选
- 折线图可视化

**API**: `GET /api/v1/stats/commits/trend`

### 3. 贡献者分布图

- Top N贡献者统计
- 饼图可视化
- 自动计算Others

**API**: `GET /api/v1/stats/contributors`

## API端点

### 搜索接口

```
GET /api/v1/search/repositories
参数:
  - keyword: 仓库名称关键词
  - stars_min: 最小stars数
  - stars_max: 最大stars数
  - forks_min: 最小forks数
  - forks_max: 最大forks数
  - limit: 返回数量（默认50）
  - offset: 偏移量（默认0）
```

### 统计接口

```
GET /api/v1/stats/commits/trend
参数:
  - repo_id: 仓库ID（可选）
  - repo_name: 仓库名称（可选，格式：owner/repo）
  - start_date: 开始日期（YYYY-MM-DD，可选）
  - end_date: 结束日期（YYYY-MM-DD，可选）
  - group_by: 分组方式（day/week/month，默认month）

GET /api/v1/stats/contributors
参数:
  - repo_id: 仓库ID（可选）
  - repo_name: 仓库名称（可选，格式：owner/repo）
  - top_n: Top N贡献者（默认10）
```

## 数据库表结构

系统假设 `github_data` 数据库包含以下表：

- `repositories` - 仓库基本信息
  - id, repo_name, stars, forks, created_at, updated_at

- `commits` - 提交记录
  - id, repo_id, contributor_name, created_at

- `contributors` - 贡献者信息（可选）

## 开发说明

### 架构原则

1. **最小可用** - 只实现搜索和可视化功能
2. **职责单一** - 每层只做一件事
3. **纯查询** - 后端只做数据查询和聚合，不进行计算
4. **前端可视化** - 前端负责图表展示，后端只返回数据

### 代码结构

- **API层** (`app/api/`): 接收HTTP请求，返回JSON
- **Service层** (`app/services/`): 业务编排，组装查询条件
- **Repository层** (`app/repository/`): 纯SQL查询
- **Model层** (`app/models/`): Pydantic数据模型
- **Infrastructure层** (`app/infrastructure/`): 数据库连接池

## 常见问题

### 1. 数据库连接失败

- 检查Docker容器是否运行：`docker ps`
- 检查端口是否正确：`netstat -an | grep 3306`
- 检查数据库名称是否为 `github_data`

### 2. 前端无法连接后端

- 检查后端是否在 8000 端口运行
- 检查 `frontend/vite.config.js` 中的代理配置
- 检查CORS配置

### 3. 查询结果为空

- 检查数据库中是否有数据
- 检查表名是否正确（repositories, commits）
- 查看后端日志确认SQL查询是否正确

## 下一步

根据 `目标.txt` 的建议，当前版本只实现基础功能。未来可以考虑：

- 更多图表类型
- 更复杂的搜索条件
- 数据缓存
- 性能优化

但记住：**先让系统可用，再考虑优化**。
