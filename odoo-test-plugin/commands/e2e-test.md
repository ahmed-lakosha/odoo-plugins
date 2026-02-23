---
title: 'E2E Test'
read_only: false
type: 'command'
description: 'Generate and run Playwright E2E tests for an Odoo module (supports self-hosted and Odoo.sh)'
---

# E2E Test

Generate Playwright E2E test scaffolds for an Odoo module and set up the test infrastructure.

## Instructions

Ask the user for the following if not provided:

1. **Module name** — the Odoo module to test (e.g., `sale_order`, `my_module`)
2. **Deployment target**: `self-hosted` (localhost) OR `Odoo.sh` (public URL)
3. **Base URL** — defaults: `http://localhost:8069` (self-hosted) or ask for Odoo.sh URL
4. **Test scenarios** — what workflows to test (CRUD, status changes, specific forms)

Then generate the appropriate files.

---

## Setup (First Time Only)

### Install Playwright

```bash
# In your project or module root
npm init playwright@latest

# Or if package.json already exists
npm install --save-dev @playwright/test
npx playwright install chromium
```

### Project Structure Created

```
your-project/
├── playwright.config.ts       ← Main config (generated)
├── tests/
│   └── e2e/
│       ├── helpers/
│       │   ├── auth.ts        ← Login helper (generated)
│       │   └── global-setup.ts ← Session setup (generated)
│       ├── pages/
│       │   └── odoo-form-page.ts ← Page object (generated)
│       └── [module]-e2e.spec.ts  ← Test file (generated)
└── .gitignore (append: playwright-report/, tests/e2e/.auth/)
```

---

## Generated Files

### `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60000,

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'playwright-results.xml' }],
  ],

  globalSetup: './tests/e2e/helpers/global-setup.ts',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:8069',
    storageState: 'tests/e2e/.auth/user.json',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

### `tests/e2e/helpers/global-setup.ts`

```typescript
import { chromium } from '@playwright/test';
import * as fs from 'fs';

export default async function globalSetup() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:8069';
  const user = process.env.ODOO_USER || 'admin';
  const password = process.env.ODOO_PASSWORD || 'admin';

  await page.goto(`${baseUrl}/web/login`);
  await page.waitForSelector('#login', { state: 'visible' });
  await page.fill('#login', user);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await page.waitForSelector('.o_home_menu, .o_action_manager', { timeout: 30000 });

  fs.mkdirSync('tests/e2e/.auth', { recursive: true });
  await context.storageState({ path: 'tests/e2e/.auth/user.json' });
  await browser.close();

  console.log(`✓ Odoo session saved for ${user} @ ${baseUrl}`);
}
```

### `tests/e2e/[module]-e2e.spec.ts` (Example for `my_module`)

```typescript
import { test, expect } from '@playwright/test';

// Session is pre-loaded via globalSetup

test.describe('[my_module] E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the module's main view
    await page.goto('/odoo/my-module');
    await page.waitForSelector('.o_loading', { state: 'hidden' });
  });

  test('should display list view', async ({ page }) => {
    await expect(page.locator('.o_list_view')).toBeVisible();
  });

  test('should create a new record', async ({ page }) => {
    // Click New
    await page.click('button.o_btn_new, a.o_btn_new');
    await page.waitForSelector('.o_form_editable', { state: 'visible' });

    // Fill required fields
    await page.fill('.o_field_char[name="name"] input', 'Test Record E2E');

    // Save
    await page.click('.o_form_buttons_view .o_btn_save');
    await page.waitForSelector('.o_loading', { state: 'hidden' });

    // Verify saved
    const name = await page.locator('.o_field_char[name="name"]').textContent();
    expect(name?.trim()).toBe('Test Record E2E');
  });

  test('should validate required fields', async ({ page }) => {
    await page.click('button.o_btn_new, a.o_btn_new');
    // Try to save without filling required fields
    await page.click('.o_form_buttons_view .o_btn_save');
    // Odoo shows red borders on required fields
    await expect(page.locator('.o_field_widget.o_required_modifier.o_field_invalid')).toBeVisible();
  });

});
```

---

## Running Tests

```bash
# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/my-module-e2e.spec.ts

# Run specific test by name
npx playwright test --grep "should create"

# Debug mode (step through)
npx playwright test --debug

# View HTML report
npx playwright show-report

# Against Odoo.sh (pass URL as env var)
PLAYWRIGHT_BASE_URL=https://your-project.odoo.com \
ODOO_USER=test@example.com \
ODOO_PASSWORD=testpassword \
npx playwright test
```

---

## GitHub Actions Integration

### For Odoo.sh (target staging URL)

```yaml
# Add to .github/workflows/e2e-tests.yml
name: "E2E Tests"
on:
  push:
    branches-ignore: [main]
  workflow_dispatch:

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - name: Run E2E tests
        run: npx playwright test
        env:
          PLAYWRIGHT_BASE_URL: ${{ secrets.ODOO_STAGING_URL }}
          ODOO_USER: ${{ secrets.ODOO_TEST_USER }}
          ODOO_PASSWORD: ${{ secrets.ODOO_TEST_PASSWORD }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

### Required GitHub Secrets

| Secret | Value |
|--------|-------|
| `ODOO_STAGING_URL` | `https://your-project-staging.odoo.com` |
| `ODOO_TEST_USER` | Dedicated test user email |
| `ODOO_TEST_PASSWORD` | Test user password |

---

## Output Summary

After running `/e2e-test`, confirm:
- `playwright.config.ts` created with correct `baseURL`
- `tests/e2e/` folder structure created
- Auth helper configured for the target (self-hosted or Odoo.sh)
- At least one `.spec.ts` test file generated for the module
- `package.json` updated with Playwright dependencies
- Instructions provided for first run and CI setup
