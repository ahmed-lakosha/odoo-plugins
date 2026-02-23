# Testing Strategies for Odoo Frontend

## Jest Testing

### Configuration

```javascript
// jest.config.js
module.exports = {
    testEnvironment: 'jsdom',
    roots: ['<rootDir>/static/src'],
    moduleNameMapper: {
        '^@web/(.*)$': '<rootDir>/addons/web/static/src/$1',
        '^@owl/(.*)$': '<rootDir>/addons/web/static/lib/owl/$1',
        '\\.(css|scss)$': 'identity-obj-proxy',
        '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/tests/__mocks__/fileMock.js'
    },
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    transform: {
        '^.+\\.(js|jsx)$': 'babel-jest',
        '^.+\\.xml$': 'jest-transform-stub'
    },
    collectCoverageFrom: [
        'static/src/**/*.{js,jsx}',
        '!static/src/**/*.test.js',
        '!static/src/**/index.js'
    ],
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    }
};
```

### Testing Owl Components

```javascript
// tests/components/ProductCard.test.js
import { mount, makeTestEnv } from '@odoo/owl/test_utils';
import { ProductCard } from '../static/src/components/ProductCard';

describe('ProductCard Component', () => {
    let env;

    beforeEach(() => {
        env = makeTestEnv();
    });

    test('renders product information correctly', async () => {
        const props = {
            id: 1,
            name: 'Test Product',
            price: 99.99,
            image: '/web/image/product/1'
        };

        const comp = await mount(ProductCard, { env, props });

        expect(comp.el.querySelector('.product-name').textContent).toBe('Test Product');
        expect(comp.el.querySelector('.product-price').textContent).toBe('$99.99');
        expect(comp.el.querySelector('.product-image').src).toContain('/web/image/product/1');

        comp.destroy();
    });

    test('handles click event', async () => {
        const onClickMock = jest.fn();
        const props = {
            id: 1,
            name: 'Test Product',
            price: 99.99,
            onClick: onClickMock
        };

        const comp = await mount(ProductCard, { env, props });

        await comp.el.querySelector('.product-card').click();

        expect(onClickMock).toHaveBeenCalledWith(1);

        comp.destroy();
    });
});
```

### Testing Public Widgets

```javascript
// tests/widgets/CartWidget.test.js
import PublicWidget from '@web/legacy/js/public/public_widget';
import { CartWidget } from '../static/src/js/widgets/cart_widget';

describe('CartWidget', () => {
    let widget;
    let container;

    beforeEach(() => {
        container = document.createElement('div');
        container.className = 'shopping-cart';
        document.body.appendChild(container);

        widget = new CartWidget();
        widget.setElement(container);
    });

    afterEach(() => {
        widget.destroy();
        document.body.removeChild(container);
    });

    test('initializes with empty cart', async () => {
        await widget.willStart();
        await widget.start();

        expect(widget.cartItems).toEqual([]);
        expect(widget.$el.find('.cart-count').text()).toBe('0');
    });

    test('adds item to cart', async () => {
        await widget.willStart();
        await widget.start();

        widget.addItem({ id: 1, name: 'Product', quantity: 1 });

        expect(widget.cartItems.length).toBe(1);
        expect(widget.$el.find('.cart-count').text()).toBe('1');
    });
});
```

## Cypress E2E Testing

### Configuration

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
    e2e: {
        baseUrl: 'http://localhost:8069',
        viewportWidth: 1920,
        viewportHeight: 1080,
        video: true,
        screenshotOnRunFailure: true,
        retries: {
            runMode: 2,
            openMode: 0
        },
        setupNodeEvents(on, config) {
            on('task', {
                'db:seed': async () => {
                    // Seed test data
                    return null;
                },
                'db:clean': async () => {
                    // Clean test data
                    return null;
                },
                log(message) {
                    console.log(message);
                    return null;
                }
            });
        }
    }
});
```

### E-commerce Flow Test

```javascript
// cypress/e2e/ecommerce.cy.js
describe('E-commerce User Journey', () => {
    beforeEach(() => {
        cy.task('db:seed');
        cy.visit('/shop');
    });

    afterEach(() => {
        cy.task('db:clean');
    });

    it('completes full purchase flow', () => {
        // Browse products
        cy.get('.oe_product').should('have.length.greaterThan', 0);

        // Search for specific product
        cy.get('input[name="search"]').type('Laptop{enter}');
        cy.url().should('include', 'search=Laptop');

        // Select product
        cy.get('.oe_product').first().click();
        cy.get('.product_detail').should('be.visible');

        // Add to cart with quantity
        cy.get('input[name="add_qty"]').clear().type('2');
        cy.get('#add_to_cart').click();

        // Verify cart updated
        cy.get('.my_cart_quantity').should('contain', '2');

        // Go to cart
        cy.get('a[href="/shop/cart"]').click();

        // Update quantity in cart
        cy.get('.js_quantity input').first().clear().type('3');
        cy.get('.js_quantity a.js_update_cart').click();

        // Apply coupon
        cy.get('input[name="promo"]').type('DISCOUNT10');
        cy.get('button:contains("Apply")').click();
        cy.get('.alert-success').should('contain', 'Coupon applied');

        // Proceed to checkout
        cy.get('a.btn-primary:contains("Checkout")').click();

        // Fill billing information
        cy.get('input[name="name"]').type('John Doe');
        cy.get('input[name="email"]').type('john@example.com');
        cy.get('input[name="phone"]').type('+1234567890');
        cy.get('input[name="street"]').type('123 Main St');
        cy.get('input[name="city"]').type('New York');
        cy.get('select[name="country_id"]').select('United States');
        cy.get('input[name="zip"]').type('10001');

        // Select shipping method
        cy.get('input[name="delivery_type"][value="standard"]').check();

        // Select payment method
        cy.get('input[name="payment_method"][value="credit_card"]').check();

        // Complete order
        cy.get('button[type="submit"]:contains("Confirm Order")').click();

        // Verify order confirmation
        cy.url().should('include', '/shop/confirmation');
        cy.get('.confirmation-message').should('be.visible');
        cy.get('.order-reference').should('match', /ORDER-\d+/);
    });

    it('handles product filtering and sorting', () => {
        // Filter by category
        cy.get('.o_wsale_products_categories_collapse').click();
        cy.get('a:contains("Electronics")').click();
        cy.get('.oe_product').each(($product) => {
            cy.wrap($product).should('have.attr', 'data-category', 'electronics');
        });

        // Filter by price range
        cy.get('input[name="min_price"]').type('100');
        cy.get('input[name="max_price"]').type('500');
        cy.get('button:contains("Filter")').click();

        // Sort products
        cy.get('select[name="order"]').select('Price: Low to High');
        cy.wait(1000);

        // Verify sorting
        let previousPrice = 0;
        cy.get('.product-price').each(($price) => {
            const price = parseFloat($price.text().replace('$', ''));
            expect(price).to.be.at.least(previousPrice);
            previousPrice = price;
        });
    });
});
```

### Custom Commands

```javascript
// cypress/support/commands.js

// Login command
Cypress.Commands.add('login', (email, password) => {
    cy.visit('/web/login');
    cy.get('input[name="login"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('not.include', '/web/login');
});

// Add product to cart
Cypress.Commands.add('addToCart', (productId, quantity = 1) => {
    cy.visit(`/shop/product/${productId}`);
    cy.get('input[name="add_qty"]').clear().type(quantity.toString());
    cy.get('#add_to_cart').click();
    cy.get('.my_cart_quantity').should('contain', quantity.toString());
});

// Clear cart
Cypress.Commands.add('clearCart', () => {
    cy.visit('/shop/cart');
    cy.get('.js_delete_product').each(($btn) => {
        cy.wrap($btn).click();
    });
});

// Wait for Odoo
Cypress.Commands.add('waitForOdoo', () => {
    cy.window().its('odoo').should('exist');
    cy.window().its('odoo.isReady').should('be.true');
});
```

## Visual Regression Testing

### BackstopJS Configuration

```javascript
// backstop.config.js
module.exports = {
    id: 'odoo_visual_regression',
    viewports: [
        { label: 'phone', width: 320, height: 480 },
        { label: 'tablet', width: 1024, height: 768 },
        { label: 'desktop', width: 1920, height: 1080 }
    ],
    onBeforeScript: 'onBefore.js',
    onReadyScript: 'onReady.js',
    scenarios: [
        {
            label: 'Homepage',
            url: 'http://localhost:8069',
            selectors: ['document'],
            hideSelectors: ['.dynamic-content', '.timestamp'],
            removeSelectors: ['.ads'],
            misMatchThreshold: 0.1,
            requireSameDimensions: false
        },
        {
            label: 'Product List',
            url: 'http://localhost:8069/shop',
            selectors: ['.products_pager', '.oe_product'],
            readySelector: '.oe_product',
            delay: 1000,
            misMatchThreshold: 0.1
        },
        {
            label: 'Product Detail',
            url: 'http://localhost:8069/shop/product/1',
            selectors: ['.product_detail'],
            hoverSelectors: ['#add_to_cart'],
            clickSelectors: ['.product-variant-selector'],
            postInteractionWait: 1000,
            misMatchThreshold: 0.1
        },
        {
            label: 'Shopping Cart',
            url: 'http://localhost:8069/shop/cart',
            selectors: ['.oe_cart'],
            misMatchThreshold: 0.1
        }
    ],
    paths: {
        bitmaps_reference: 'tests/visual/reference',
        bitmaps_test: 'tests/visual/test',
        engine_scripts: 'tests/visual/scripts',
        html_report: 'tests/visual/html_report',
        ci_report: 'tests/visual/ci_report'
    },
    report: ['browser', 'CI'],
    engine: 'puppeteer',
    engineOptions: {
        args: ['--no-sandbox'],
        headless: true
    },
    asyncCaptureLimit: 5,
    asyncCompareLimit: 50,
    debug: false,
    debugWindow: false
};
```

### Custom Scripts

```javascript
// tests/visual/scripts/onReady.js
module.exports = async (page, scenario) => {
    console.log('SCENARIO > ' + scenario.label);

    // Wait for animations to complete
    await page.waitForTimeout(500);

    // Remove dynamic elements
    await page.evaluate(() => {
        // Remove timestamps
        document.querySelectorAll('.timestamp, .date-display').forEach(el => {
            el.textContent = 'TIMESTAMP';
        });

        // Stabilize random content
        document.querySelectorAll('.random-product').forEach(el => {
            el.style.display = 'none';
        });
    });

    // Handle lazy loaded images
    if (scenario.label.includes('Product')) {
        await page.evaluate(() => {
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
            });
        });
        await page.waitForTimeout(1000);
    }
};
```

## Performance Testing

### Lighthouse CI

```javascript
// lighthouserc.js
module.exports = {
    ci: {
        collect: {
            url: [
                'http://localhost:8069/',
                'http://localhost:8069/shop',
                'http://localhost:8069/shop/product/1'
            ],
            numberOfRuns: 3,
            settings: {
                preset: 'desktop',
                throttling: {
                    cpuSlowdownMultiplier: 1
                }
            }
        },
        assert: {
            assertions: {
                'categories:performance': ['error', { minScore: 0.8 }],
                'categories:accessibility': ['warn', { minScore: 0.9 }],
                'categories:seo': ['warn', { minScore: 0.9 }],
                'categories:best-practices': ['warn', { minScore: 0.9 }],
                'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
                'largest-contentful-paint': ['error', { maxNumericValue: 4000 }],
                'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
                'total-blocking-time': ['error', { maxNumericValue: 300 }]
            }
        },
        upload: {
            target: 'temporary-public-storage'
        }
    }
};
```

## Test Data Management

### Fixtures

```javascript
// tests/fixtures/products.js
export const mockProducts = [
    {
        id: 1,
        name: 'Laptop',
        price: 999.99,
        category: 'Electronics',
        stock: 10,
        image: '/web/image/product.template/1/image_1920'
    },
    {
        id: 2,
        name: 'Office Chair',
        price: 299.99,
        category: 'Furniture',
        stock: 25,
        image: '/web/image/product.template/2/image_1920'
    }
];

// tests/fixtures/users.js
export const testUsers = {
    admin: {
        email: 'admin@example.com',
        password: 'admin123',
        role: 'admin'
    },
    customer: {
        email: 'customer@example.com',
        password: 'customer123',
        role: 'portal'
    }
};
```

### Mock Services

```javascript
// tests/mocks/rpcService.js
export class MockRPCService {
    constructor() {
        this.responses = new Map();
    }

    mockResponse(route, response) {
        this.responses.set(route, response);
    }

    async call(route, params) {
        if (this.responses.has(route)) {
            return this.responses.get(route);
        }
        throw new Error(`No mock response for route: ${route}`);
    }
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/frontend-tests.yml
name: Frontend Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/coverage-final.json

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Odoo
        run: docker-compose up -d

      - name: Wait for Odoo
        run: npx wait-on http://localhost:8069

      - name: Run Cypress tests
        uses: cypress-io/github-action@v5
        with:
          browser: chrome
          record: true
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup
        run: npm ci

      - name: Run BackstopJS tests
        run: npm run test:visual

      - name: Upload visual diff report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: visual-diff-report
          path: tests/visual/html_report

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
```

## Test Scripts

```json
// package.json scripts section
{
  "scripts": {
    "test": "npm run test:unit && npm run test:e2e",
    "test:unit": "jest",
    "test:unit:watch": "jest --watch",
    "test:unit:coverage": "jest --coverage",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open",
    "test:visual": "backstop test",
    "test:visual:approve": "backstop approve",
    "test:visual:reference": "backstop reference",
    "test:performance": "lhci autorun",
    "test:accessibility": "pa11y-ci",
    "test:all": "npm run test:unit && npm run test:e2e && npm run test:visual && npm run test:performance"
  }
}
```

## Best Practices

1. **Test Pyramid**
   - Many unit tests (fast, isolated)
   - Some integration tests
   - Few E2E tests (slower, more brittle)

2. **Test Organization**
   - Group tests by feature
   - Use descriptive test names
   - Follow AAA pattern (Arrange, Act, Assert)

3. **Mock External Dependencies**
   - Mock RPC calls in unit tests
   - Use test database for E2E tests
   - Stub third-party services

4. **Performance**
   - Run tests in parallel when possible
   - Use test data factories
   - Clean up after tests

5. **Maintenance**
   - Keep tests simple and readable
   - Update tests when features change
   - Regular test refactoring