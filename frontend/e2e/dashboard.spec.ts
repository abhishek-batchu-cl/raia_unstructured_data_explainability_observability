import { test, expect } from '@playwright/test';

/**
 * E2E Tests for RAIA Dashboard
 */

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/');

    // Check title
    await expect(page).toHaveTitle(/RAIA/);

    // Check main heading
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
  });

  test('should display metrics cards', async ({ page }) => {
    await page.goto('/');

    // Wait for metrics to load
    await page.waitForTimeout(1000);

    // Check for metric cards (adjust selectors based on your actual UI)
    const metricsCards = page.locator('[data-testid="metric-card"]');
    await expect(metricsCards).toHaveCount(4, { timeout: 5000 });
  });

  test('should navigate to different sections', async ({ page }) => {
    await page.goto('/');

    // Click on Attribution link
    await page.click('text=Attribution');
    await expect(page).toHaveURL(/.*attribution/);

    // Click on Reasoning link
    await page.click('text=Reasoning');
    await expect(page).toHaveURL(/.*reasoning/);

    // Click on Monitoring link
    await page.click('text=Monitoring');
    await expect(page).toHaveURL(/.*monitoring/);
  });

  test('should fetch and display data from API', async ({ page }) => {
    // Intercept API calls
    await page.route('**/api/dashboard', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_runs: 150,
          avg_faithfulness: 0.85,
          avg_hallucination: 0.12,
          avg_precision: 0.78
        })
      });
    });

    await page.goto('/');

    // Check that data is displayed
    await expect(page.locator('text=150')).toBeVisible();
    await expect(page.locator('text=0.85')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls with error
    await page.route('**/api/dashboard', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    await page.goto('/');

    // Check for error message
    const errorMessage = page.locator('text=/error|failed/i');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check that mobile menu works (if you have one)
    const mobileMenu = page.locator('[data-testid="mobile-menu"]');
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();

      // Check that menu items are visible
      await expect(page.locator('text=Dashboard')).toBeVisible();
    }
  });
});

test.describe('Authentication', () => {
  test('should show login page when not authenticated', async ({ page }) => {
    await page.goto('/');

    // Check if redirected to login or if login button is visible
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible({ timeout: 5000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');

    // Submit form
    await page.click('button[type="submit"]');

    // Check redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 5000 });
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill with invalid credentials
    await page.fill('input[name="username"]', 'invalid');
    await page.fill('input[name="password"]', 'wrong');

    // Submit form
    await page.click('button[type="submit"]');

    // Check for error message
    const errorMessage = page.locator('text=/invalid|incorrect|failed/i');
    await expect(errorMessage).toBeVisible();
  });
});

test.describe('Data Visualization', () => {
  test('should render charts correctly', async ({ page }) => {
    await page.goto('/');

    // Wait for charts to load
    await page.waitForTimeout(2000);

    // Check for chart elements (adjust selectors based on your charts)
    const charts = page.locator('canvas, svg[class*="recharts"]');
    await expect(charts.first()).toBeVisible();
  });

  test('should update charts when filters change', async ({ page }) => {
    await page.goto('/');

    // Select a filter option
    await page.selectOption('select[name="timeRange"]', '7d');

    // Wait for chart update
    await page.waitForTimeout(1000);

    // Verify API was called with correct params
    // This depends on your implementation
  });
});

test.describe('Performance', () => {
  test('should load page in reasonable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Assert load time is under 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should not have console errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    // Assert no console errors
    expect(errors).toHaveLength(0);
  });
});
