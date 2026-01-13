# OpenPulse Frontend

GitHub 开源数据搜索与可视化系统 - 前端应用

## 技术栈

- **React 18** - UI 框架
- **Vite** - 构建工具
- **React Router** - 路由管理
- **Tailwind CSS** - 样式框架
- **Recharts** - 图表可视化
- **Axios** - HTTP 客户端

## 项目结构

```
frontend/
├── src/
│   ├── api/
│   │   └── github.js         # API 接口封装
│   ├── components/
│   │   ├── AiAssistant.jsx   # AI 小助手组件
│   │   ├── ContributorsChart.jsx  # 贡献者图表
│   │   ├── ErrorLogModal.jsx # 错误日志弹窗
│   │   ├── HealthScore.jsx   # 项目健康度评分组件
│   │   ├── HelpModal.jsx     # 帮助弹窗
│   │   ├── SimilarProjectsModal.jsx  # 相似项目推荐
│   │   └── TrendChart.jsx    # 趋势图表组件
│   ├── pages/
│   │   ├── HomePage.jsx      # 首页（搜索 + 项目列表）
│   │   └── ProjectPage.jsx   # 项目详情页
│   ├── App.jsx               # 根组件
│   ├── main.jsx              # 入口文件
│   └── index.css             # 全局样式
├── public/                   # 静态资源
├── index.html                # HTML 模板
├── package.json
├── vite.config.js            # Vite 配置
├── tailwind.config.js        # Tailwind 配置
└── postcss.config.js         # PostCSS 配置
```

## 功能模块

### 首页 (HomePage)
- 项目搜索（支持名称搜索、Star 数量筛选）
- 项目列表展示（分页、排序）
- 快速跳转到项目详情

### 项目详情页 (ProjectPage)
- 项目基本信息展示
- **Star/Fork/Issue/Comment 趋势图表**
- **贡献者分布饼状图**
- **项目健康度评分（PHAM v2.0）**
  - 关注度增长
  - 开发活跃度
  - 社区贡献度
  - 代码健康度
- 相似项目推荐

### 组件说明

#### HealthScore 健康度评分
基于 PHAM (Project Health Assessment Model) v2.0，从四个维度评估项目健康度：
- 关注度增长 (20%): Star/Fork 增长趋势
- 开发活跃度 (40%): Commit 频率和活跃度指标
- 社区贡献度 (20%): PR 提交趋势
- 代码健康度 (20%): 代码变动量

#### TrendChart 趋势图表
支持多种数据类型的时间序列可视化：
- Star 趋势
- Fork 趋势
- Issue 趋势
- Comment 趋势

## 安装与运行

### 环境要求
- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 生产构建

```bash
npm run build
```

构建产物输出到 `dist/` 目录

### 预览构建

```bash
npm run preview
```

## 环境配置

### API 后端地址

编辑 `vite.config.js` 中的代理配置：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端地址
        changeOrigin: true,
      }
    }
  }
})
```

## 界面特点

- **深色主题** - 现代化暗色设计
- **响应式布局** - 适配桌面和移动端
- **棱角线条风格** - 独特的 UI 美学
- **交互动画** - 流畅的过渡效果

## 与后端配合

前端需要配合后端 API 使用，主要接口：

- `GET /api/v1/search/projects` - 搜索项目
- `GET /api/v1/stats/project/summary` - 项目摘要
- `GET /api/v1/stats/project/trends` - 趋势数据
- `GET /api/v1/stats/contributors` - 贡献者数据
- `GET /api/v1/stats/health/{project}` - 健康度评分

## 许可证

MIT License
