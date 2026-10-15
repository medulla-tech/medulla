import { expect, Page } from '@playwright/test';

export const credentials = {
  user: process.env.MEDULLA_USER ?? '',
  password: process.env.MEDULLA_PASSWORD ?? '',
};

/** Fills the login form of index.php and submits it. */
export async function login(page: Page, user = credentials.user, password = credentials.password) {
  await page.goto('index.php');
  await page.locator('#username').fill(user);
  await page.locator('#password').fill(password);
  await page.locator('#connect_button').click();
}

/** Asserts the current page is an authenticated Medulla page. */
export async function expectLoggedIn(page: Page) {
  await expect(page).toHaveURL(/main\.php/);
  await expect(page.locator('#navbar-logout')).toBeVisible();
}

/** Builds the URL of a module page: main.php?module=X&submod=Y&action=Z */
export function pageUrl(module: string, submod: string, action: string) {
  return `main.php?module=${module}&submod=${submod}&action=${action}`;
}

const PHP_ERROR = /(Fatal error|Parse error|Uncaught (Error|Exception)|Warning:|Notice:|Deprecated:)/;

/** Fails if PHP printed an error or a warning into the page. */
export async function expectNoPhpErrors(page: Page) {
  const text = await page.locator('body').innerText();
  expect(text, 'PHP error found in page').not.toMatch(PHP_ERROR);
}
