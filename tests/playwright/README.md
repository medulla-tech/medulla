# Medulla Playwright tests

End-to-end tests for the Medulla web interface (`web/`).

## Setup

```bash
cd tests/playwright
npm install
npx playwright install --with-deps chromium
cp .env.example .env   # then set MEDULLA_URL, MEDULLA_USER, MEDULLA_PASSWORD
```

`MEDULLA_URL` points to the web root, with a trailing slash (e.g. `https://server/mmc/`).
Use a test server: the suite logs in and out but creates no data.

## Run

```bash
npm test              # headless
npm run test:headed   # watch the browser
npm run report        # open the last HTML report
```

## Suites

| File | Covers |
|------|--------|
| `tests/auth.setup.ts` | Logs in once and saves the session to `.auth/user.json` |
| `tests/login.spec.ts` | Login form, valid / invalid credentials, redirect without session, logout |
| `tests/navigation.spec.ts` | Default page of every module loads without HTTP 5xx or PHP errors |
| `tests/pkgs.spec.ts` | Package list and add-package form |

Modules that are disabled or hidden by ACL are reported as **skipped**, not failed.

## CI

`.github/workflows/playwright.yml` runs on pull requests and pushes that touch `web/` or these tests:

- **check**: type-checks and lists the tests. Needs no server.
- **e2e**: runs the suite against the server set in the repository secrets
  `MEDULLA_URL`, `MEDULLA_USER` and `MEDULLA_PASSWORD`. Skipped when `MEDULLA_URL` is not set
  (for example on pull requests from forks). The HTML report is uploaded as the `playwright-report` artifact.

GitHub-hosted runners only reach public servers. If the test server is on a private network,
register a self-hosted runner that can reach it and set the repository variable
`PLAYWRIGHT_RUNNER` to its label.
