import { expect, test } from '@playwright/test';
import { expectNoPhpErrors, pageUrl } from '../helpers/medulla';

// Default page of each module (from modules/*/infoPackage.inc.php)
const pages: [module: string, submod: string, action: string][] = [
  ['base', 'main', 'default'],
  ['dashboard', 'main', 'default'],
  ['base', 'computers', 'machinesList'],
  ['base', 'groups', 'index'],
  ['base', 'users', 'index'],
  ['base', 'status', 'index'],
  ['base', 'audit', 'indexall'],
  ['base', 'logview', 'index'],
  ['inventory', 'inventory', 'incoming'],
  ['pkgs', 'pkgs', 'index'],
  ['msc', 'logs', 'consult'],
  ['xmppmaster', 'xmppmaster', 'index'],
  ['imaging', 'manage', 'index'],
  ['admin', 'admin', 'relaysList'],
  ['kiosk', 'kiosk', 'index'],
  ['updates', 'updates', 'index'],
  ['security', 'security', 'index'],
  ['report', 'report', 'index'],
  ['backuppc', 'backuppc', 'index'],
  ['urbackup', 'urbackup', 'index'],
  ['store', 'store', 'index'],
  ['support', 'support', 'index'],
  ['services', 'control', 'index'],
  ['mastering', 'mastering', 'index'],
  ['mobile', 'mobile', 'index'],
];

test.describe('Module navigation', () => {
  for (const [module, submod, action] of pages) {
    test(`${module}/${submod}/${action} loads`, async ({ page }) => {
      const response = await page.goto(pageUrl(module, submod, action));
      expect(response?.status(), 'HTTP status').toBeLessThan(500);

      // main.php redirects to the default page when a module is disabled or
      // the user lacks the ACL: that is a configuration choice, not a failure.
      const landed = new URL(page.url()).searchParams.get('module');
      test.skip(landed !== module, `module "${module}" is not enabled for this user`);

      await expect(page.locator('#navbar-logout')).toBeVisible();
      await expectNoPhpErrors(page);
    });
  }
});
