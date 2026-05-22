# Job Scraper Service 部署指南

## 🔴 Railway 故障状态（2026-05-19）

Railway 正在经历重大服务中断（Google Cloud 账户被封锁），暂时无法使用。

## ✅ 替代部署方案

### 方案 1: Render（推荐）

#### 步骤：

1. **注册 Render 账号**
   - 访问：https://render.com/
   - 使用 GitHub 登录

2. **创建新的 Web Service**
   - 点击 "New" → "Web Service"
   - 连接 GitHub 仓库
   - 选择 `job-scraper-service` 仓库

3. **配置部署**
   - Name: `job-scraper-service`
   - Environment: `Docker`
   - Docker Context: `/`
   - Dockerfile Path: `Dockerfile`

4. **设置环境变量**（在 "Advanced" 部分）
   ```
   PORT=5000
   GEMINI_API_KEY=your_actual_key
   GOOGLE_SHEET_ID=your_actual_sheet_id
   GOOGLE_CREDENTIALS_JSON=your_actual_credentials_json
   SECRET_KEY=your_secret_key
   ```

5. **部署**
   - 点击 "Create Web Service"
   - Render 会自动构建和部署
   - 等待 5-10 分钟

6. **获取 URL**
   - 部署成功后，Render 会提供 URL：
   - 格式：`https://job-scraper-service.onrender.com`

7. **验证部署**
   ```bash
   # 访问健康检查
   curl https://job-scraper-service.onrender.com/health

   # 应该返回：
   # {"status":"healthy","app":"Job Scraper Service","version":"1.0.0"}
   ```

---

### 方案 2: Fly.io

#### 步骤：

1. **安装 Fly CLI**
   ```bash
   brew install flyctl
   ```

2. **登录 Fly**
   ```bash
   flyctl auth signup
   flyctl auth login
   ```

3. **部署应用**
   ```bash
   cd /Users/liyueheng/event-horizon-lab/job-scraper-service

   # 启动应用
   flyctl launch

   # 设置环境变量
   flyctl secrets set PORT=5000
   flyctl secrets set GEMINI_API_KEY=your_key
   flyctl secrets set GOOGLE_SHEET_ID=your_id
   flyctl secrets set GOOGLE_CREDENTIALS_JSON=your_creds
   flyctl secrets set SECRET_KEY=your_secret

   # 部署
   flyctl deploy
   ```

---

### 方案 3: Vercel（需要修改配置）

Vercel 更适合 Next.js/Node.js 应用，对于 Python 应用需要额外配置。

---

### 方案 4: Heroku

#### 步骤：

1. **安装 Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **登录**
   ```bash
   heroku login
   ```

3. **创建应用**
   ```bash
   cd /Users/liyueheng/event-horizon-lab/job-scraper-service
   heroku create job-scraper-service
   ```

4. **设置环境变量**
   ```bash
   heroku config:set PORT=5000
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set GOOGLE_SHEET_ID=your_id
   heroku config:set GOOGLE_CREDENTIALS_JSON=your_creds
   heroku config:set SECRET_KEY=your_secret
   ```

5. **部署**
   ```bash
   git push heroku main
   # 或者
   heroku container:push web --app job-scraper-service
   heroku container:release web --app job-scraper-service
   ```

---

## 📊 平台对比

| 平台 | 免费套餐 | Docker 支持 | 推荐度 | 当前可用性 |
|------|---------|------------|--------|----------|
| Render | ✅ 750小时/月 | ✅ | ⭐⭐⭐⭐⭐ | ✅ 正常 |
| Fly.io | ✅ 3个小型 VM | ✅ | ⭐⭐⭐⭐ | ✅ 正常 |
| Heroku | ❌ 已取消免费 | ✅ | ⭐⭐⭐ | ✅ 正常 |
| Vercel | ✅ | ⚠️ 需配置 | ⭐⭐ | ✅ 正常 |
| Railway | ✅ | ✅ | ⭐⭐⭐⭐⭐ | ❌ 故障中 |

---

## 🎯 我的推荐

**立即使用 Render**，原因：
1. ✅ 服务正常
2. ✅ 免费套餐慷慨
3. ✅ 配置简单（类似 Railway）
4. ✅ 支持 Docker（无需修改代码）
5. ✅ 自动 HTTPS
6. ✅ 良好的文档和支持

---

## 🔄 从 Railway 迁移到 Render

如果您之前在 Railway 上部署过：

1. **导出环境变量**（从 Railway Dashboard，等恢复后）
2. **在 Render 重新部署**（按上述步骤）
3. **更新任何使用旧 Railway URL 的地方**

---

## 📝 部署后检查清单

部署成功后，确保：
- [ ] `/health` 端点返回 200
- [ ] `/` 页面可以访问
- [ ] `/api/scrape` 端点工作正常
- [ ] Google Sheets 集成正常
- [ ] 日志中没有错误

---

## 💡 提示

- **Render 免费套餐会在 15 分钟无活动后休眠**
- **首次访问可能需要等待 30-60 秒启动**
- **升级到付费套餐可以避免休眠**

---

**最后更新**: 2026-05-20
**状态**: Railway 故障中，建议使用 Render
