# Bot数据清洗工具使用说明

## 📋 概述

本工具用于清除GitHub项目的comments和issues数据中的bot信息。通过检查`user`字段中是否包含"bot"关键词（不区分大小写）来识别bot用户。

## 📁 文件说明

- **`preview_bot_data.py`** - 预览脚本，统计bot数据但不修改文件
- **`clean_bot_data.py`** - 清洗脚本，删除bot数据（可选择备份）

## 🔍 识别策略

Bot用户识别规则：
- user字段包含"bot"关键词（不区分大小写）
- 示例：`github-actions[bot]`, `dependabot[bot]`, `k8s-ci-robot`, `adguard-bot` 等

## 📊 数据统计（预览结果）

### 总体统计
- **总文件数**: 584 个 (292 comments + 292 issues)
- **总数据量**: 9,163,395 条
- **Bot数据**: 1,774,617 条 (19.37%)
- **清洗后保留**: 7,388,778 条

### Comments目录
- 数据总数: 6,336,365 条
- Bot数据: 1,485,168 条 (23.44%)
- 包含Bot的文件: 236/292 个

### Issues目录
- 数据总数: 2,827,030 条
- Bot数据: 289,449 条 (10.24%)
- 包含Bot的文件: 278/292 个

### Top 20 Bot用户

| 排名 | Bot用户名 | 数据量 |
|------|-----------|--------|
| 1 | github-actions[bot] | 394,747 |
| 2 | dependabot[bot] | 54,992 |
| 3 | k8s-ci-robot | 49,454 |
| 4 | wingetbot | 46,155 |
| 5 | google-cla[bot] | 43,711 |
| 6 | openshift-ci[bot] | 41,736 |
| 7 | fw-bot | 38,011 |
| 8 | webcompat-bot | 36,089 |
| 9 | grafanabot | 35,881 |
| 10 | conan-center-bot | 33,842 |
| 11 | adguard-bot | 31,508 |
| 12 | azure-pipelines[bot] | 30,767 |
| 13 | gopherbot | 27,164 |
| 14 | openshift-cherrypick-robot | 25,569 |
| 15 | openjdk[bot] | 24,339 |
| 16 | stale[bot] | 22,552 |
| 17 | netlify[bot] | 21,590 |
| 18 | BrewTestBot | 21,474 |
| 19 | facebook-github-bot | 21,271 |
| 20 | codecov[bot] | 20,155 |

*还有 1082 个其他bot用户*

### Bot占比最高的文件

| 文件名 | 总数 | Bot数 | 占比 |
|--------|------|-------|------|
| JacksonKearl_testissues.json (issue) | 1,534 | 1,512 | 98.57% |
| openjournals_joss-reviews.json | 2,018 | 1,988 | 98.51% |
| zero-to-mastery_start-here-guidelines.json | 12,384 | 12,142 | 98.05% |
| JacksonKearl_testissues.json (comment) | 9,114 | 8,912 | 97.78% |
| webcompat_web-bugs.json | 39,674 | 35,545 | 89.59% |

## 🚀 使用步骤

### 步骤1: 预览（推荐先执行）

```bash
python preview_bot_data.py
```

此命令会：
- ✅ 统计bot数据量
- ✅ 显示Top bot用户
- ✅ 显示bot占比最高的文件
- ❌ **不会修改任何文件**

### 步骤2: 执行清洗

```bash
python clean_bot_data.py
```

执行时会询问：
1. **是否备份原始文件?** (y/n, 默认y)
   - 选择 `y`: 会创建 `.backup` 备份文件
   - 选择 `n`: 不创建备份（**谨慎！**）

2. **确认开始清洗?** (y/n)
   - 选择 `y`: 开始清洗
   - 选择 `n`: 取消操作

## ⚠️ 注意事项

### 1. 备份建议
- **强烈建议**在首次运行时选择备份（y）
- 备份文件将以 `.backup` 后缀保存在原文件旁边
- 示例：`microsoft_vscode.json` → `microsoft_vscode.json.backup`

### 2. JSON格式错误
部分文件（约49个）可能因包含特殊控制字符而无法处理，这些文件会被跳过并显示错误信息。

### 3. 磁盘空间
- 原始数据约占用 **~2-3GB**
- 如果选择备份，需要额外 **~2-3GB** 空间
- 清洗后数据约占用 **~1.6-2.4GB** (减少约19%)

### 4. 处理时间
- 预览脚本: 约 5-10 分钟
- 清洗脚本: 约 10-20 分钟（取决于磁盘速度）

### 5. 可恢复性
如果清洗后发现问题，可以：
```bash
# 恢复单个文件
copy data\comment\microsoft_vscode.json.backup data\comment\microsoft_vscode.json

# 批量恢复所有备份（PowerShell）
Get-ChildItem -Path data\comment\*.backup | ForEach-Object { Copy-Item $_.FullName ($_.FullName -replace '\.backup$','') -Force }
Get-ChildItem -Path data\issue\*.backup | ForEach-Object { Copy-Item $_.FullName ($_.FullName -replace '\.backup$','') -Force }
```

## 📝 清洗后的数据

清洗后的JSON文件将：
- ✅ 移除所有user字段包含"bot"的条目
- ✅ 保持原有的JSON数组格式
- ✅ 保持UTF-8编码
- ✅ 保持缩进格式（2空格）

## 🔄 重新运行

脚本支持重复运行：
- 预览脚本可以随时运行
- 清洗脚本可以多次运行（幂等操作）
- 如果数据已清洗，再次运行不会有任何变化

## ❓ 常见问题

### Q1: 会删除哪些数据？
A: 所有user字段包含"bot"关键词的comments和issues条目。

### Q2: 会影响原始JSON文件结构吗？
A: 不会，只是删除数组中的部分元素，整体结构保持不变。

### Q3: 如果出错了怎么办？
A: 如果选择了备份，可以从`.backup`文件恢复原始数据。

### Q4: 需要多少时间？
A: 预览约5-10分钟，实际清洗约10-20分钟。

### Q5: 可以自定义过滤规则吗？
A: 可以修改脚本中的`is_bot_user()`函数来自定义规则。

## 📞 技术支持

如遇问题，请检查：
1. Python版本 >= 3.7
2. 磁盘空间是否充足
3. 文件权限是否正确
4. JSON文件格式是否完整

---

**最后提醒**: 建议在执行清洗前，先运行预览脚本了解数据情况，并选择备份选项！
