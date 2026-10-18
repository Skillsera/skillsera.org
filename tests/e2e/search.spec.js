const { test, expect } = require('@playwright/test');

test.describe('Search', () => {
  test('homepage renders search input', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[name="q"]').first()).toBeVisible();
    await expect(page.locator('h1.logo').first()).toContainText('Skillsera');
  });

  test('typing in search box triggers results', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.locator('#main-search');
    await searchInput.fill('what is');

    // Wait for htmx to fire and results to appear
    await page.waitForResponse(resp =>
      resp.url().includes('/questions/search') && resp.status() === 200
    );

    // Either results list or "no results" message should appear
    const resultsContainer = page.locator('#main-search-results');
    await expect(resultsContainer).not.toBeEmpty({ timeout: 3000 });
  });

  test('nav search bar is visible on learn page', async ({ page }) => {
    await page.goto('/learn');
    await expect(page.locator('nav input[name="q"]')).toBeVisible();
  });

  test('search from nav navigates to correct URL', async ({ page }) => {
    await page.goto('/');
    const navSearch = page.locator('nav input[name="q"]');
    await navSearch.fill('matter');
    await page.waitForResponse(resp =>
      resp.url().includes('/questions/search') && resp.status() === 200
    );
    // Results should appear below nav
    const navResults = page.locator('#search-results');
    await expect(navResults).not.toBeEmpty({ timeout: 3000 });
  });
});
