#!/bin/bash

# Railway Automated Setup Script
# This script will deploy job-scraper-service to Railway using the new repository

set -e

echo "=========================================="
echo "🚀 Job Scraper Service - Railway Setup"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI is ready"
echo ""

# Check login status
echo "📝 Checking Railway login status..."
if ! railway status &> /dev/null; then
    echo "⚠️  You need to login to Railway"
    echo "Opening browser for authentication..."
    railway login || {
        echo ""
        echo "❌ Login failed. Please run: railway login"
        exit 1
    }
fi

echo "✅ Logged in to Railway"
echo ""

# Navigate to job-scraper-service directory
cd /Users/liyueheng/event-horizon-lab/job-scraper-service

# Link to existing project
echo "📦 Linking to Railway project..."
railway link --project welcoming-surprise || {
    echo "⚠️  Project link failed, trying init..."
    railway init
}

echo ""
echo "=========================================="
echo "🔧 Setting Environment Variables"
echo "=========================================="
echo ""

# Set environment variables
echo "Setting PYTHONPATH and PORT..."
railway variables set PYTHONPATH="/app"
railway variables set PORT="5000"

echo ""
echo "✅ Core variables configured"
echo ""
echo "⚠️  IMPORTANT: You need to set these variables manually via Railway dashboard:"
echo "   1. GEMINI_API_KEY (your Google Gemini API key)"
echo "   2. GOOGLE_SHEET_ID (1isZ5XwcafEkDBG-kkQkZIWXVyqiEEHS_b4TO-XwTjQ8)"
echo "   3. GOOGLE_SHEET_NAME (职位数据)"
echo "   4. GOOGLE_CREDENTIALS_JSON (your Google service account JSON)"
echo "   5. SECRET_KEY (generate one with: openssl rand -hex 32)"
echo "   6. DEBUG=False"
echo ""
echo "Open Railway dashboard to set these:"
echo "  open https://railway.com/project/088aa7d6-9a06-4c0a-8b4b-ab0da0f26087/variables"
echo ""

echo "=========================================="
echo "🚀 Deploying to Railway..."
echo "=========================================="
echo ""

# Deploy
railway up

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set the remaining environment variables in Railway dashboard"
echo "2. Wait for deployment to complete"
echo "3. Check logs: railway logs"
echo "4. Get your domain: railway domain"
echo ""
