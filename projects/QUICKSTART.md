# 快速启动指南

## 1. 确保Docker MySQL运行

```bash
# 检查MySQL容器是否运行
docker ps | grep mysql

# 如果没有运行，启动容器
docker run -d \
  --name openpulse_mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=github_data \
  -p 3306:3306 \
  mysql:8.0
```

## 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端将在 http://localhost:8000 启动

## 3. 启动前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3000 启动

## 4. 访问应用

打开浏览器访问：http://localhost:3000

## 测试API

访问API文档：http://localhost:8000/docs

### 测试搜索接口

```bash
curl "http://localhost:8000/api/v1/search/repositories?keyword=react&stars_min=1000&limit=10"
```

### 测试统计接口

```bash
# 提交趋势
curl "http://localhost:8000/api/v1/stats/commits/trend?repo_name=facebook/react&group_by=month"

# 贡献者分布
curl "http://localhost:8000/api/v1/stats/contributors?repo_name=facebook/react&top_n=10"
```

## 常见问题

### 数据库连接失败

1. 确认MySQL容器运行：`docker ps`
2. 测试连接：`mysql -h 127.0.0.1 -P 3306 -u root -proot`
3. 确认数据库存在：`SHOW DATABASES;` 应该看到 `github_data`

### 前端无法连接后端

1. 确认后端在8000端口运行
2. 检查浏览器控制台错误
3. 确认 `frontend/vite.config.js` 中的代理配置正确

### 查询结果为空

1. 确认数据库中有数据
2. 检查表名是否正确（repositories, commits）
3. 查看后端日志确认SQL查询
