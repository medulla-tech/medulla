import { expect, test } from '@playwright/test';
import { expectLoggedIn, login, pageUrl } from '../helpers/medulla';

// These tests manage their own session: logging out destroys it on the server,
// so they must not reuse the shared one from auth.setup.ts.
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('Login', () => {
  test('shows the login form', async ({ page }) => {
    await page.goto('index.php');
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#connect_button')).toBeVisible();
  });

  test('logs in with valid credentials', async ({ page }) => {
    await login(page);
    await expectLoggedIn(page);
  });

  test('rejects a wrong password', async ({ page }) => {
    await login(page, undefined, 'definitely-not-the-password');
    await expect(page.locator('#alert')).toBeVisible();
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#navbar-logout')).toHaveCount(0);
  });

  test('rejects an unknown user', async ({ page }) => {
    await login(page, 'no-such-user-playwright', 'whatever');
    await expect(page.locator('#alert')).toBeVisible();
    await expect(page.locator('#navbar-logout')).toHaveCount(0);
  });

  test('redirects to the login page without a session', async ({ page }) => {
    await page.goto(pageUrl('base', 'main', 'default'));
    await expect(page).toHaveURL(/index\.php\?sessionexpired=1/);
    await expect(page.locator('#loginForm')).toBeVisible();
  });
});

test.describe('Logout', () => {
  test('logs out and invalidates the session', async ({ page }) => {
    await login(page);
    await expectLoggedIn(page);

    await page.locator('#navbar-logout').click();
    await page.locator('input[name="delog"]').click();
    await expect(page.locator('#loginForm')).toBeVisible();

    // The old session must no longer grant access
    await page.goto(pageUrl('base', 'main', 'default'));
    await expect(page.locator('#loginForm')).toBeVisible();
  });
});
