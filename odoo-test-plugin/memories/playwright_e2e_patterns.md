# Playwright E2E Testing Patterns for Odoo

> **Purpose**: End-to-End testing of Odoo web UI using Playwright.
> Covers setup, authentication, page objects, selectors, and CI integration.

---

## Applicability Overview

| Target | Playwright Applicable? | How |
|--------|----------------------|-----|
| Self-hosted Odoo (any version) | ✅ Yes | Start Odoo locally or on CI, test against `http://localhost:8069` |
| Odoo.sh staging environment | ✅ Yes | Run Playwright from GitHub Actions against the public staging URL |
| Odoo.sh production | ⚠️ With care | Use read-only test user, never mutate production data |
| Odoo native `browser_js()` migration | ✅ Yes | Direct replacement — Playwright is the modern equivalent |

---

## Setup

### Installation

```bash
# In your module or project root
npm init playwright@latest

# Or add to existing project
npm install --save-dev @playwright/test
npx playwright install chromium  # Install Chromium browser
```

### `playwright.config.ts` for Odoo

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,       // Odoo tests share state — run sequentially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60000,             // Odoo pages can be slow to load

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'playwright-results.xml' }],  // For CI
  ],

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:8069',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Wait for Odoo's dynamic loading to settle
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Optional: mobile testing
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },
  ],
});
```

---

## Authentication Helper

Odoo requires session-based auth. Use `storageState` to reuse sessions:

```typescript
// tests/e2e/helpers/auth.ts

import { Page, BrowserContext } from '@playwright/test';

export interface OdooCredentials {
  url?: string;
  user: string;
  password: string;
  database?: string;
}

export async function loginToOdoo(
  page: Page,
  credentials: OdooCredentials
): Promise<void> {
  const base = credentials.url || process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:8069';

  await page.goto(`${base}/web/login`);

  // Wait for login form to be ready
  await page.waitForSelector('#login', { state: 'visible' });

  // Fill credentials
  await page.fill('#login', credentials.user);
  await page.fill('#password', credentials.password);

  // Optional: select database if multi-db
  if (credentials.database) {
    const dbSelect = page.locator('select[name="db"]');
    if (await dbSelect.isVisible()) {
      await dbSelect.selectOption(credentials.database);
    }
  }

  await page.click('button[type="submit"]');

  // Wait for Odoo backend to load
  await page.waitForSelector('.o_home_menu, .o_action_manager', { timeout: 30000 });
}

// Save session state to reuse across tests (much faster)
export async function saveOdooSession(
  context: BrowserContext,
  stateFile: string
): Promise<void> {
  await context.storageState({ path: stateFile });
}
```

**Use saved sessions in tests (recommended — avoids login on every test)**:

```typescript
// playwright.config.ts — add global setup
export default defineConfig({
  globalSetup: './tests/e2e/helpers/global-setup.ts',
  use: {
    storageState: 'tests/e2e/.auth/user.json',  // Reuse session
  },
});

// tests/e2e/helpers/global-setup.ts
import { chromium } from '@playwright/test';
import { loginToOdoo } from './auth';
import * as fs from 'fs';

export default async function globalSetup() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await loginToOdoo(page, {
    user: process.env.ODOO_USER || 'admin',
    password: process.env.ODOO_PASSWORD || 'admin',
  });

  // Save session
  fs.mkdirSync('tests/e2e/.auth', { recursive: true });
  await context.storageState({ path: 'tests/e2e/.auth/user.json' });
  await browser.close();
}
```

---

## Odoo-Specific Selectors Reference

### Core Layout

```typescript
// Main app areas
'.o_home_menu'              // Home menu (app switcher)
'.o_action_manager'         // Main content area
'.o_loading'                // Loading spinner (wait for it to disappear!)
'.o_navbar'                 // Top navigation bar
'.o_breadcrumb'             // Breadcrumb navigation

// Notifications
'.o_notification'           // Toast notifications
'.o_dialog'                 // Modal dialogs
'.o_error_dialog'           // Error dialogs
```

### Form View

```typescript
// Form container
'.o_form_view'                         // Form view root
'.o_form_editable'                     // Form in edit mode
'.o_form_readonly'                     // Form in read mode

// Fields (by name attribute)
'.o_field_widget[name="partner_id"]'   // Any field by name
'.o_field_char[name="name"]'           // Char field
'.o_field_many2one[name="partner_id"]' // Many2one field
'.o_field_text[name="description"]'    // Text area field
'.o_field_boolean[name="active"]'      // Boolean toggle

// Buttons
'.o_form_buttons_view .o_btn_save'    // Save button
'.o_form_buttons_view .o_btn_discard' // Discard button
'button[name="action_confirm"]'        // Action button by name
'.o_status_bar .o_statusbar_status'   // Status bar buttons
```

### List View

```typescript
'.o_list_view'                         // List view root
'.o_list_view thead th'               // Column headers
'.o_list_view tbody tr.o_data_row'    // Data rows
'.o_pager'                             // Pagination
'.o_pager .o_pager_next'              // Next page
'.o_searchview'                        // Search bar
'.o_searchview_input'                  // Search input
```

### Kanban View

```typescript
'.o_kanban_view'                       // Kanban root
'.o_kanban_group'                      // Column/group
'.o_kanban_record'                     // Individual card
'.o_kanban_quick_create'              // Quick create form
```

---

## Waiting Strategies for Odoo

Odoo uses heavy async rendering. Always wait properly:

```typescript
// Wait for loading spinner to disappear (critical!)
await page.waitForSelector('.o_loading', { state: 'hidden', timeout: 30000 });

// Wait for network to be idle after navigation
await page.waitForLoadState('networkidle');

// Wait for specific field to be visible
await page.waitForSelector('.o_field_widget[name="state"]', { state: 'visible' });

// Wait for action to complete (e.g., save, confirm)
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle' }),
  page.click('button[name="action_confirm"]'),
]);

// Wait for dialog to appear
await page.waitForSelector('.o_dialog', { state: 'visible' });

// Wait for notification
await page.waitForSelector('.o_notification', { state: 'visible' });
const notificationText = await page.locator('.o_notification').textContent();
```

---

## Page Object Model for Odoo

### Base Odoo Page

```typescript
// tests/e2e/pages/base-odoo-page.ts
import { Page } from '@playwright/test';

export class BaseOdooPage {
  constructor(protected page: Page) {}

  async waitForLoad(): Promise<void> {
    await this.page.waitForSelector('.o_loading', { state: 'hidden', timeout: 30000 });
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToApp(appName: string): Promise<void> {
    await this.page.click('.o_home_menu_icon, .o_main_navbar .o_menu_brand');
    await this.page.click(`.o_app[data-menu-xmlid*="${appName}"], .o_app[title="${appName}"]`);
    await this.waitForLoad();
  }

  async getNotificationText(): Promise<string | null> {
    try {
      await this.page.waitForSelector('.o_notification', { timeout: 5000 });
      return await this.page.locator('.o_notification .o_notification_content').textContent();
    } catch {
      return null;
    }
  }

  async getCurrentBreadcrumb(): Promise<string> {
    return await this.page.locator('.o_breadcrumb .o_last_breadcrumb_item').textContent() || '';
  }
}
```

### OdooFormPage

```typescript
// tests/e2e/pages/odoo-form-page.ts
import { Page } from '@playwright/test';
import { BaseOdooPage } from './base-odoo-page';

export class OdooFormPage extends BaseOdooPage {
  constructor(page: Page) {
    super(page);
  }

  async fillField(fieldName: string, value: string): Promise<void> {
    const field = this.page.locator(`.o_field_widget[name="${fieldName}"] input`);
    await field.clear();
    await field.fill(value);
  }

  async selectMany2One(fieldName: string, searchValue: string): Promise<void> {
    const field = this.page.locator(`.o_field_many2one[name="${fieldName}"] input`);
    await field.fill(searchValue);
    await this.page.waitForSelector('.o_dropdown_menu .o_dropdown_option', { state: 'visible' });
    await this.page.click(`.o_dropdown_menu .o_dropdown_option:first-child`);
  }

  async setStatus(statusLabel: string): Promise<void> {
    await this.page.click(`.o_statusbar_status button:has-text("${statusLabel}")`);
    await this.waitForLoad();
  }

  async save(): Promise<void> {
    await this.page.click('.o_form_buttons_view .o_btn_save');
    await this.waitForLoad();
  }

  async clickButton(buttonName: string): Promise<void> {
    await this.page.click(`button[name="${buttonName}"]`);
    await this.waitForLoad();
  }

  async getFieldValue(fieldName: string): Promise<string> {
    return await this.page.locator(`.o_field_widget[name="${fieldName}"]`).textContent() || '';
  }
}
```

---

## Example: Complete E2E Test for Sales Order

```typescript
// tests/e2e/sales-order.spec.ts
import { test, expect } from '@playwright/test';
import { OdooFormPage } from './pages/odoo-form-page';

test.describe('Sales Order Workflow', () => {

  test('create and confirm a sales order', async ({ page }) => {
    // Session is already loaded via globalSetup (storageState)
    const formPage = new OdooFormPage(page);

    // Navigate to Sales app
    await formPage.navigateToApp('sale');

    // Click New button
    await page.click('.o_list_buttons button.o_btn_new, a.o_btn_new');
    await formPage.waitForLoad();

    // Fill order details
    await formPage.selectMany2One('partner_id', 'Azure Interior');

    // Add a product line
    await page.click('.o_field_one2many[name="order_line"] .o_field_x2many_list_row_add a');
    await formPage.selectMany2One('product_id', '[CONS_CPU_I5]');

    // Verify amount populated
    await formPage.waitForLoad();
    const amount = await formPage.getFieldValue('amount_total');
    expect(parseFloat(amount.replace(/[^0-9.]/g, ''))).toBeGreaterThan(0);

    // Confirm order
    await formPage.clickButton('action_confirm');

    // Verify state changed to Sales Order
    const state = await page.locator('.o_statusbar_status .o_arrow_button_current').textContent();
    expect(state?.trim()).toBe('Sales Order');

    // Check breadcrumb has order reference
    const breadcrumb = await formPage.getCurrentBreadcrumb();
    expect(breadcrumb).toMatch(/S\d{5}/);
  });

});
```

---

## Odoo.sh: Running Playwright Against Staging URL

Odoo.sh creates a staging URL for each branch automatically.

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e-tests.yml
name: "E2E Tests (Playwright)"

on:
  # Run after Odoo.sh staging deployment completes
  push:
    branches-ignore: [main]  # Staging branches only
  workflow_dispatch:
    inputs:
      base_url:
        description: "Odoo staging URL"
        required: true
        type: string

jobs:
  e2e:
    name: Playwright E2E Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests against Odoo.sh staging
        run: npx playwright test
        env:
          PLAYWRIGHT_BASE_URL: ${{ github.event.inputs.base_url || secrets.ODOO_STAGING_URL }}
          ODOO_USER: ${{ secrets.ODOO_TEST_USER }}
          ODOO_PASSWORD: ${{ secrets.ODOO_TEST_PASSWORD }}

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

### Configuration for Odoo.sh Target

```typescript
// playwright.config.ts — Odoo.sh variant
export default defineConfig({
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'https://your-project.odoo.com',
    // Odoo.sh may need longer timeouts (shared infrastructure)
    actionTimeout: 60000,
    navigationTimeout: 90000,
  },
});
```

**Required GitHub Secrets**:
- `ODOO_STAGING_URL` — your Odoo.sh staging URL (e.g., `https://your-project-staging.odoo.com`)
- `ODOO_TEST_USER` — dedicated test user email (NOT admin)
- `ODOO_TEST_PASSWORD` — test user password

---

## Odoo 17-19 Specifics (OWL 2.0)

Odoo 17+ uses OWL 2.0 with more async rendering:

```typescript
// OWL 2.0 renders components asynchronously — need extra waits
async function waitForOWLRender(page: Page): Promise<void> {
  // Wait for all pending microtasks to flush
  await page.waitForFunction(() => {
    // Check no pending OWL renders
    return !document.querySelector('.o_loading');
  });
  await page.waitForLoadState('networkidle');
}

// Odoo 17+: Use waitForResponse for JSON-RPC calls
await page.waitForResponse(
  response => response.url().includes('/web/dataset/call_kw') && response.status() === 200
);
```

---

## Self-Hosted: Start Odoo in CI for E2E

```yaml
# In GitHub Actions — start Odoo as background service
- name: Start Odoo Server
  run: |
    python -m odoo \
      --db_host=localhost --db_user=odoo --db_password=odoo \
      -d test_e2e \
      --addons-path=odoo/addons,projects \
      --without-demo=False \
      --http-port=8069 &

    # Wait for server to be ready
    echo "Waiting for Odoo to start..."
    for i in $(seq 1 30); do
      if curl -sf http://localhost:8069/web/health > /dev/null 2>&1; then
        echo "✓ Odoo is ready"
        break
      fi
      echo "Attempt $i/30..."
      sleep 5
    done

- name: Run Playwright Tests
  run: npx playwright test
  env:
    PLAYWRIGHT_BASE_URL: http://localhost:8069
    ODOO_USER: admin
    ODOO_PASSWORD: admin
```

---

## Migration: `browser_js()` → Playwright

For teams upgrading from Odoo 14-16 where `browser_js()` was used:

| Old (`browser_js`) | New (Playwright) |
|--------------------|-----------------|
| `self.browser_js('/web', 'web.tour.startTour("tour_name")', login=True)` | `await page.goto('/web'); await runOdooTour(page, 'tour_name')` |
| `self.start_tour('/odoo/sales', 'tour_name')` | `await page.goto('/odoo/sales'); await page.evaluate("odoo.startTour('tour_name')")` |
| `phantom_js('/web', 'odoo.testing.run()')` | Full Playwright test (no equivalent shortcut) |

**Note**: Odoo's JavaScript tour definitions still work in Odoo 17+ — only the Python `browser_js()` method was removed. You can still trigger tours via `page.evaluate()`.

---

## Related

- `testing_patterns.md` — Python unit/integration test patterns
- `devops-plugin/memories/cicd_patterns.md` — GitHub Actions E2E workflow (Stage 2.5)
- `odoo-service-plugin/memories/deployment_patterns.md` — Starting Odoo for CI testing
- `/e2e-test` command — Generate E2E test scaffolds for a module
