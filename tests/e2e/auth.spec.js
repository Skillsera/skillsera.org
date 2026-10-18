const { test, expect } = require('@playwright/test');

test.describe('Auth API', () => {
  test('session endpoint returns logged:false when not logged in', async ({ request }) => {
    const response = await request.post('/auth/session');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.logged).toBe(false);
  });

  test('login with missing credentials returns 422', async ({ request }) => {
    const response = await request.post('/auth/login', {
      data: {},
    });
    expect(response.status()).toBe(422);
  });

  test('register with missing fields returns 422', async ({ request }) => {
    const response = await request.post('/auth/register', {
      data: {},
    });
    expect(response.status()).toBe(422);
  });
});
