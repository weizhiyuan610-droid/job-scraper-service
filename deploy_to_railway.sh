#!/bin/bash

# Railway Deploy Helper Script
# 这个脚本会帮助你部署到Railway

set -e

echo "=========================================="
echo "🚀 Event Horizon Lab - Railway Deploy"
echo "=========================================="
echo ""

# 检查railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "请先运行: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI已安装"
echo ""

# 检查登录状态
echo "📝 检查Railway登录状态..."
if railway status &> /dev/null; then
    echo "✅ 已登录Railway"
else
    echo "❌ 未登录Railway"
    echo ""
    echo "请在你的终端运行:"
    echo "  railway login"
    echo ""
    echo "然后重新运行这个脚本"
    exit 1
fi

echo ""
echo "=========================================="
echo "📦 开始部署"
echo "=========================================="
echo ""

cd /Users/liyueheng/event-horizon-lab/job-scraper-service

# 初始化项目
echo "1️⃣  初始化Railway项目..."
railway init

echo ""
echo "2️⃣  设置环境变量..."
echo "请输入你的配置:"
echo ""

read -p "GEMINI_API_KEY: " gemini_key
read -p "GOOGLE_SHEET_ID: " sheet_id
read -p "GOOGLE_SHEET_NAME (职位数据): " sheet_name
read -p "GOOGLE_CREDENTIALS_JSON (粘贴JSON内容): " credentials

railway variables set GEMINI_API_KEY="$gemini_key"
railway variables set GOOGLE_SHEET_ID="$sheet_id"
railway variables set GOOGLE_SHEET_NAME="$sheet_name"
railway variables set GOOGLE_CREDENTIALS_JSON="$credentials"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set DEBUG="False"

echo ""
echo "3️⃣  部署到Railway..."
railway up

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "查看你的应用:"
railway domain
echo ""
