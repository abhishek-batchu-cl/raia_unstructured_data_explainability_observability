#!/bin/bash

# E2E Testing Setup for RAIA Frontend
# ====================================

echo "🔧 Setting up E2E testing environment..."

# Install Playwright
npm install -D @playwright/test@latest

# Install browsers
npx playwright install --with-deps chromium firefox webkit

echo "✅ E2E testing setup complete!"
echo ""
echo "Run tests with:"
echo "  npm run test:e2e         # Run all E2E tests"
echo "  npm run test:e2e:ui      # Run with UI mode"
echo "  npm run test:e2e:headed  # Run in headed mode"
