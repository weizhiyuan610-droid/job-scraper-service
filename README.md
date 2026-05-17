# 🚀 Event Horizon Lab - 职位抓取工具

> AI驱动的职位信息抓取服务，自动从招聘网站提取职位数据并写入Google Sheets

## ✨ 功能特点

- 🤖 **AI智能提取**：使用Gemini AI理解网页内容，准确提取职位信息
- 🌐 **通用抓取**：支持任何招聘网站（LinkedIn、公司官网、第三方平台）
- ✅ **半自动审核**：AI提取后可预览确认，确保数据准确
- 📊 **实时写入**：一键保存到Google Sheets，网站自动更新
- 🎨 **优雅界面**：简洁的Web界面，傻瓜式操作
- 🚀 **云端部署**：部署在Railway，随时随地访问

---

## 📋 系统架构

```
用户输入URL
    ↓
Playwright 抓取网页
    ↓
Gemini AI 提取数据
    ↓
用户预览确认
    ↓
写入 Google Sheets
```

---

## 🚀 快速开始

### 方式1：使用在线版本（推荐助理使用）

直接访问已部署的Web应用：
```
https://job-scraper.your-domain.com
```

**无需安装任何东西！**

---

### 方式2：本地开发运行

#### 前置条件

- Python 3.10+
- Gemini API密钥
- Google Sheets配置

#### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/event-horizon-lab.git
cd event-horizon-lab/job-scraper-service

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装Playwright浏览器
playwright install chromium

# 6. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥

# 7. 启动应用
python app.py
```

应用将在 http://localhost:5000 启动

---

## ⚙️ 配置指南

### 1. 获取Gemini API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 复制密钥

### 2. 配置Google Sheets

1. 创建Google Cloud项目
2. 启用Google Sheets API
3. 创建服务账号
4. 下载JSON密钥文件
5. 在Google Sheets中共享给服务账号邮箱
6. 记录Spreadsheet ID（从URL中获取）

详细步骤请参考：[SERVICE_ACCOUNT_SETUP.md](../../SERVICE_ACCOUNT_SETUP.md)

### 3. 环境变量

在 `.env` 文件中配置：

```bash
# Gemini API
GEMINI_API_KEY=your_api_key_here

# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SHEET_NAME=职位数据

# Flask
SECRET_KEY=your_secret_key
DEBUG=False
```

---

## 🚀 Railway部署

### 自动部署（推荐）

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "Add job scraper service"
   git push origin main
   ```

2. **在Railway创建新项目**
   - 访问 [Railway](https://railway.app)
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置环境变量**
   在Railway项目中添加以下环境变量：

   ```bash
   GEMINI_API_KEY=your_api_key
   GOOGLE_SHEET_ID=your_sheet_id
   GOOGLE_SHEET_NAME=职位数据
   GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
   ```

   **重要**：`GOOGLE_CREDENTIALS_JSON` 需要粘贴整个服务账号JSON文件的内容（一行）

4. **部署完成**
   - Railway会自动构建和部署
   - 获得一个类似 `https://job-scraper-production.up.railway.app` 的域名
   - 可以绑定自定义域名

---

## 📖 使用教程

### 基本流程

1. **打开网站**
   - 访问部署的URL
   - 或本地运行 http://localhost:5000

2. **输入职位链接**
   - 从招聘网站复制职位URL
   - 粘贴到输入框
   - 点击"开始抓取"

3. **检查提取结果**
   - AI自动填充所有字段
   - **重点检查**：签证赞助、截止日期
   - 发现错误可直接修改

4. **确认写入**
   - 点击"确认写入"
   - 职位保存到Google Sheets
   - 5分钟内自动更新到网站

### 支持的网站

| 网站类型 | 难度 | 说明 |
|---------|------|------|
| 咨询公司官网 | ⭐ 容易 | McKinsey, BCG, Bain等 |
| 投行官网 | ⭐ 容易 | Goldman Sachs, JPMorgan等 |
| Greenhouse | ⭐ 容易 | 统一格式 |
| LinkedIn | ⭐⭐⭐ 困难 | 需要登录，不建议 |
| Workday | ⭐⭐ 中等 | 部分可抓取 |

---

## 💰 成本估算

| 项目 | 成本 |
|------|------|
| Gemini API | ~$0.002/职位 |
| Railway免费套餐 | $0 |
| **总计** | ~$0.20/100职位 |

---

## 📊 数据字段

工具会提取以下20个字段：

- ✅ 公司名称
- ✅ 职位名称
- ✅ 行业分类
- ✅ 工作地点
- ✅ 职位类型
- ✅ 学历要求
- ✅ 签证赞助 ⭐
- ✅ 截止日期 ⭐
- ✅ 目标年级
- ✅ 薪资范围
- ✅ 申请链接
- ✅ 职位描述

---

## 🔒 安全说明

1. **API密钥**
   - 不要提交到Git
   - 使用环境变量
   - `.env` 文件已加入 `.gitignore`

2. **Google凭证**
   - 服务账号JSON文件不要提交
   - 在Railway使用环境变量
   - 限制服务账号权限

---

## 🐛 故障排除

### 问题1：抓取失败

**解决方案**：
- 检查网络连接
- 确认URL可以访问
- 某些网站（LinkedIn）需要登录，无法抓取

### 问题2：AI提取错误

**解决方案**：
- 点击"重新抓取"
- 手动修改错误字段
- 检查网页结构是否特殊

### 问题3：无法写入Google Sheets

**解决方案**：
- 检查服务账号权限
- 确认已共享表格给服务账号邮箱
- 查看Railway日志

---

## 📞 技术支持

- 📧 邮箱：[your-email@example.com]
- 💬 微信：[your-wechat]
- 📱 工作时间：周一至周五 9:00-18:00

---

## 📝 许可证

MIT License

---

## 🎉 致谢

- [Playwright](https://playwright.dev/) - 强大的网页抓取工具
- [Gemini AI](https://ai.google.dev/) - Google的AI模型
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [Railway](https://railway.app/) - 简单的部署平台

---

**Made with ❤️ for Event Horizon Lab**
