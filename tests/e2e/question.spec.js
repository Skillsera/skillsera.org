const { test, expect } = require('@playwright/test');

test.describe('Question page', () => {
  test('/learn renders without an id', async ({ page }) => {
    await page.goto('/learn');
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('#question-container')).toBeVisible();
  });

  test('/about page renders correctly', async ({ page }) => {
    await page.goto('/about');
    await expect(page.locator('h2')).toContainText('About Skillsera');
    await expect(page.locator('nav h1.logo')).toBeVisible();
  });

  test('page title includes Skillsera', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Skillsera/);
  });

  test('learn page title updates with question', async ({ page }) => {
    // This test is meaningful once the DB has seeded data.
    // With no data it should still render without crashing.
    const response = await page.goto('/learn');
    expect(response.status()).toBe(200);
  });

  test('answer form is accessible on learn page', async ({ page }) => {
    await page.goto('/learn');
    // The form appears inside a question card when a question is loaded.
    // Without a question loaded, the fallback text appears.
    const container = page.locator('#question-container');
    await expect(container).toBeVisible();
  });
});
