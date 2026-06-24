# 🚀 Event Horizon Lab - 职位数据提取工具

> AI驱动的职位信息提取服务，使用 Claude AI 从招聘文本中提取结构化数据并写入 Google Sheets

## ✨ 功能特点

- 🤖 **Claude AI 智能提取**：使用 Claude Sonnet 模型理解职位描述，准确提取 44 个结构化字段
- 📝 **文本输入模式**：复制粘贴职位描述即可，无需处理复杂的网页抓取
- ✅ **半自动审核**：AI 提取后可预览确认，确保数据准确
- 📊 **实时写入**：一键保存到 Google Sheets，44 列完整数据
- 🎨 **简洁界面**：优雅的 Web 界面，操作简单直观
- 🔍 **签证智能分析**：结合公司历史数据库，智能预测签证赞助可能性
- 📈 **职位评分系统**：自动计算优先级、紧急度、质量等多个维度分数

---

## 📋 系统架构

```
用户输入职位描述文本
    ↓
Claude AI 提取结构化数据
    ↓
公司信息增强（数据库/AI）
    ↓
签证信息增强（历史数据库）
    ↓
职位评分计算
    ↓
用户预览确认
    ↓
写入 Google Sheets（44列）
```

---

## 📊 数据字段（44列）

### 基础信息（A列-H列）
- ID、公司名称、职位名称、行业、地点、薪资、签证状态、截止日期

### 学位与要求（I列-K列）
- 优选专业、目标年级、学位要求

### 职位详情（L列-U列）
- 职位类型、描述、申请链接、状态、技能标签、部门、职级、工作模式、目标受众、薪资范围

### 公司信息（V列-AC列）
- 公司规模、员工数、融资阶段、总部地点、成立年份、公司层级、官网、域名

### 精确解析字段（AD列-AH列）
- 最低学位、优选学位、签证提及状态、签证备注、原始描述

### 评分字段（AI列-AN列）
- 优先级分数、紧急度分数、新鲜度分数、质量分数、可匹配性分数、计算时间

### 增强字段（AO列-AR列）
- 职位要求、福利待遇、签证信息来源、签证可能性

---

## 🚀 快速开始

### 方式1：使用在线版本

直接访问已部署的 Web 应用（无需安装）：
```
https://your-deployed-domain.com
```

### 方式2：本地开发运行

#### 前置条件

- Python 3.9+
- Claude API 密钥
- Google Sheets 配置

#### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/event-horizon-lab.git
cd event-horizon-lab/job-scraper-service

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 6. 启动应用
python app.py
```

应用将在 http://localhost:5001 启动

---

## ⚙️ 配置指南

### 1. 获取 Claude API 密钥

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 创建新的 API 密钥
3. 复制密钥

### 2. 配置 Google Sheets

1. 创建 Google Cloud 项目
2. 启用 Google Sheets API
3. 创建服务账号
4. 下载 JSON 密钥文件
5. 在 Google Sheets 中共享给服务账号邮箱（编辑者权限）
6. 记录 Spreadsheet ID（从 URL 中获取）

### 3. 环境变量

在 `.env` 文件中配置：

```bash
# Claude API
CLAUDE_API_KEY=sk-ant-api03-xxxxx
AI_MODEL=claude-sonnet-4-6
AI_TEMPERATURE=0.1
AI_SIMPLE_MODE=True

# Google Sheets
GOOGLE_SHEET_ID=1isZ5XwcafEkDBG-kkQkZIWXVyqiEEHS_b4TO-XwTjQ8
GOOGLE_SHEET_NAME=职位数据
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...",...}

# Scraper Configuration
HEADLESS_BROWSER=True
PAGE_TIMEOUT=60000
DELAY_BETWEEN_REQUESTS=2

# Application
DEBUG=True
LOG_LEVEL=INFO
PORT=5001
```

**重要**：`GOOGLE_CREDENTIALS_JSON` 需要粘贴整个服务账号 JSON 文件的内容（转义为一行）

---

## 📖 使用教程

### 基本流程

1. **打开网站**
   - 访问部署的 URL 或本地 http://localhost:5001

2. **输入职位描述**
   - 从招聘网站复制职位描述文本
   - 粘贴到输入框
   - 点击"提取数据"

3. **检查提取结果**
   - Claude AI 自动填充所有 44 个字段
   - **重点检查**：签证赞助、截止日期、学位要求
   - 发现错误可直接修改

4. **确认写入**
   - 点击"保存到 Google Sheets"
   - 职位保存到指定工作表

### 推荐使用方式

| 来源 | 操作 | 说明 |
|------|------|------|
| 咨询公司官网 | 复制 JD 文本 | McKinsey, BCG, Bain 等 |
| 投行官网 | 复制 JD 文本 | Goldman Sachs, JPMorgan 等 |
| Greenhouse | 复制 JD 文本 | 统一格式，效果最佳 |
| LinkedIn | 复制 JD 文本 | 需要手动打开职位页面 |
| Workday | 复制 JD 文本 | 部分职位可以 |

---

## 📊 评分系统说明

### 优先级分数 (Priority Score)
用于职位列表排序，综合考虑：
- 截止日期紧迫度（30%）
- 签证赞助情况（20%）
- 公司层级（25%）
- 数据完整度（15%）
- 薪资信息（10%）

### 紧急度分数 (Urgency Score)
标记即将关闭的职位：
- 80-100：非常紧急（7天内截止）
- 50-79：紧急（30天内截止）
- 20-49：一般（60天内截止）
- 0-19：不急

### 质量分数 (Quality Score)
用于过滤低质量职位：
- 数据完整度（50%）
- 公司层级（30%）
- 职位清晰度（20%）

### 可匹配性分数 (Matchability Score)
用于个性化推荐：
- 签证信息（20%）
- 学位要求（20%）
- 技能标签（20%）
- 专业偏好（15%）
- 目标受众（10%）

---

## 💰 成本估算

| 项目 | 成本 |
|------|------|
| Claude API (Sonnet) | ~$0.003/职位 |
| Railway 免费套餐 | $0 |
| Google Sheets API | 免费 |
| **总计** | ~$0.30/100职位 |

---

## 🔒 安全说明

1. **API 密钥**
   - 不要提交到 Git
   - 使用环境变量
   - `.env` 文件已加入 `.gitignore`

2. **Google 凭证**
   - 服务账号 JSON 文件不要提交
   - 在 Railway 使用环境变量
   - 限制服务账号权限为仅 Sheets 编辑

---

## 🐛 故障排除

### 问题1：提取失败

**解决方案**：
- 检查 Claude API 密钥是否有效
- 确认账户有足够额度
- 检查网络连接

### 问题2：无法写入 Google Sheets

**解决方案**：
- 检查服务账号权限
- 确认已共享表格给服务账号邮箱
- 验证 `GOOGLE_CREDENTIALS_JSON` 格式正确

### 问题3：某些字段未提取

**解决方案**：
- 检查输入的职位描述是否完整
- 某些公司 JD 格式特殊，可能需要手动补充
- 使用详细模式（设置 `AI_SIMPLE_MODE=False`）

---

## 📞 技术支持

- 📧 邮箱：[your-email@example.com]
- 💬 微信：[your-wechat]

---

## 📝 许可证

MIT License

---

## 🎉 致谢

- [Claude AI](https://www.anthropic.com/) - Anthropic 的 AI 模型
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架
- [gspread](https://github.com/burnash/gspread) - Google Sheets API 库
- [Railway](https://railway.app/) - 简单的部署平台

---

**Made with ❤️ for Event Horizon Lab**
