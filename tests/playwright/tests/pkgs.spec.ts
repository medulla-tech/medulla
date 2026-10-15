import { expect, test } from '@playwright/test';
import { expectNoPhpErrors, pageUrl } from '../helpers/medulla';

test.describe('Packages', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(pageUrl('pkgs', 'pkgs', 'index'));
    const landed = new URL(page.url()).searchParams.get('module');
    test.skip(landed !== 'pkgs', 'pkgs module is not enabled for this user');
  });

  test('lists packages', async ({ page }) => {
    await expect(page.locator('h2').first()).toBeVisible();
    await expectNoPhpErrors(page);
  });

  test('opens the add package form', async ({ page }) => {
    await page.goto(pageUrl('pkgs', 'pkgs', 'add'));
    await expect(page.locator('h2').first()).toBeVisible();

    const name = page.locator('input[name="label"]');
    await expect(name).toBeVisible();
    await expect(name).toHaveAttribute('required', /.*/);
    await expect(page.locator('input[name="version"]')).toBeVisible();
    await expectNoPhpErrors(page);
  });
});
