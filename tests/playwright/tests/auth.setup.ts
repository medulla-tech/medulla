import { test as setup } from '@playwright/test';
import { expectLoggedIn, login } from '../helpers/medulla';

// Logs in once and stores the session cookie for every other test.
setup('authenticate', async ({ page }) => {
  await login(page);
  await expectLoggedIn(page);
  await page.context().storageState({ path: '.auth/user.json' });
});
