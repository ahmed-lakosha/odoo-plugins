# odoo-test-plugin

Comprehensive Odoo testing toolkit for Claude Code. Generates test skeletons, runs test suites with colored output, creates realistic mock data, analyzes test coverage, and integrates with Azure DevOps for CI/CD test reporting. Supports Odoo versions 14 through 19.

## Features

- **Test Generation** - Auto-generates complete test class skeletons by reading model source files
- **Test Runner** - Colored PASS/FAIL output with JUnit XML and JSON report generation
- **Mock Data Factory** - Realistic field-type-aware fixture generation for test setUp methods
- **Coverage Reporter** - Identifies untested methods with per-model and overall coverage percentages
- **E2E Testing** - Playwright-based end-to-end test generation for Odoo web interfaces
- **Smart Hooks** - PostToolUse hooks that suggest tests when models, constraints, or routes are added
- **Azure DevOps Integration** - JUnit XML output compatible with `PublishTestResults@2` task

## Requirements

- Odoo 14, 15, 16, 17, 18, or 19 installation
- Python 3.10+
- PostgreSQL database with an Odoo database
- Optional: `colorama` for Windows color support (`pip install colorama`)
- Optional: `coverage` for Python coverage measurement (`pip install coverage`)

## Installation

Place this plugin directory at:
```
C:\TQ-WorkSpace\odoo\tmp\plugins\odoo-test-plugin\
```

The plugin is auto-loaded by Claude Code when the `.claude-plugin/plugin.json` is detected.

## Quick Start

### 1. Full Testing Workflow (recommended)

```
/odoo-test my_module --config conf/project17.conf --database project17
```

Runs coverage analysis, generates missing test skeletons, executes the test suite, and reports results.

### 2. Sub-commands

```bash
# Generate test skeleton for a model
/odoo-test generate sale.order --module /c/odoo/odoo17/projects/myproject/my_module

# Run tests for a module
/odoo-test run my_module --config conf/project17.conf --database project17

# Check test coverage
/odoo-test coverage /c/odoo/odoo17/projects/myproject/my_module

# Generate mock data fixtures
/odoo-test data --model res.partner --count 5

# Generate Playwright E2E tests
/odoo-test e2e my_module --base-url http://localhost:8069
```

### 3. Sample Output

```
PASS  my_module.tests.test_my_model.TestMyModel.test_create_minimal
PASS  my_module.tests.test_my_model.TestMyModel.test_write_name
FAIL  my_module.tests.test_my_model.TestMyModel.test_constraint_amount

Total Tests: 3 | Passed: 2 | Failed: 1 | Duration: 4.23s
```

---

## Natural Language

You do not need to memorize sub-command syntax. The skill responds to plain English:

| What you say | What happens |
|---|---|
| "Generate test cases for my sale.order extension" | Analyzes model and generates TransactionCase skeletons |
| "Create realistic mock data for testing my inventory module" | Produces a mock data factory with realistic records |
| "Run tests for my custom module with post_install tag" | Executes the suite with `--test-enable` and `--test-tags=post_install` |
| "Show me which parts of my module have no test coverage" | Scans for untested models/methods and produces a coverage report |
| "Generate Playwright E2E tests for my Odoo module" | Creates Playwright test files for login, navigation, and form flows |
| "What tests are missing for my_module?" | Runs coverage analysis and lists gaps |
| "Test the sale order customization" | Detects the module and runs its test suite |

---

## Command Reference

### `/odoo-test <module> [options]`

The single entry point. Without a sub-command, runs the full workflow (coverage + generate + run + report).

| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | Odoo config file | Auto-detected |
| `--database NAME` | Database name | Auto-detected |
| `--tags TAGS` | Test tag filter | `post_install` |
| `--generate-missing` | Auto-generate tests for models without them | False |
| `--coverage-only` | Only run coverage analysis | False |
| `--threshold N` | Fail if coverage below N% | 0 |
| `--output FILE` | Save report to file | stdout |

### Sub-commands

#### `generate <model> [options]`

Generate a complete `TransactionCase` test skeleton for an Odoo model.

```bash
/odoo-test generate my.model
/odoo-test generate my.model --module /path/to/module
/odoo-test generate my.model --module /path/to/module --dry-run
/odoo-test generate my.model --module /path/to/module --force
/odoo-test generate my.model --module /path/to/module --output /custom/path/test_my.py
```

Generated files include:
- `setUpClass()` with mail tracking disabled
- `setUp()` with per-test record creation
- CRUD tests (create, search, write, unlink)
- Compute field tests (for all `@depends` methods detected)
- Selection field tests (for all `Selection` fields)
- Constraint tests (templates)
- Action method stubs (for all `action_*` methods)
- Multi-record batch creation test

#### `run <module> [options]`

Execute Odoo module tests with colored terminal output.

```bash
/odoo-test run my_module --config conf/project17.conf --database project17
/odoo-test run my_module --tags post_install
/odoo-test run my_module --test-class TestMyModel
/odoo-test run my_module --test-class TestMyModel --test-method test_create_order
/odoo-test run my_module --show-logs
/odoo-test run my_module --output test_results.xml --output-format junit
/odoo-test run my_module --output report.json --output-format json
```

#### `coverage <module_path> [options]`

Analyze test coverage for an Odoo module.

```bash
/odoo-test coverage /path/to/module
/odoo-test coverage /path/to/module --threshold 80
/odoo-test coverage /path/to/module --format json --output coverage.json
/odoo-test coverage /path/to/module --format html --output coverage.html
```

#### `data --model <model> [options]`

Generate realistic mock data Python code for test fixtures.

```bash
/odoo-test data --model res.partner --count 5
/odoo-test data --model sale.order --count 3
/odoo-test data --model my.model --count 10 --module /path/to/module
/odoo-test data --model my.model --count 5 --format individual
/odoo-test data --model my.model --count 5 --format create_list
/odoo-test data --model my.model --count 50 --format loop
/odoo-test data --model my.model --count 5 --format setup_method
/odoo-test data --model hr.employee --count 10 --output setup_fixtures.py
```

#### `e2e <module> [options]`

Generate Playwright end-to-end tests for an Odoo module's web interface.

```bash
/odoo-test e2e my_module --base-url http://localhost:8069
/odoo-test e2e my_module --base-url http://localhost:8069 --output tests/e2e/
```

---

## Scripts Reference

Scripts can be run standalone without Claude Code.

### `test_generator.py`

```bash
python test_generator.py --model sale.order --module /path/to/module
python test_generator.py --model my.model --module /path/to/module --dry-run
python test_generator.py --model my.model --module /path/to/module --force
python test_generator.py --model my.model --module /path/to/module --output /path/test_my.py
```

### `test_runner.py`

```bash
python test_runner.py --module my_module --config conf/project17.conf --database project17
python test_runner.py --module my_module --config conf/p17.conf --database db17 --tags post_install
python test_runner.py --module my_module --config conf/p17.conf --database db17 \
    --test-class TestMyModel --test-method test_create
python test_runner.py --module my_module --config conf/p17.conf --database db17 \
    --output test_results.xml --output-format junit
python test_runner.py --module my_module --config conf/p17.conf --database db17 --show-logs
```

### `mock_data_factory.py`

```bash
python mock_data_factory.py --model res.partner --count 5
python mock_data_factory.py --model my.model --count 10 --module /path/to/module
python mock_data_factory.py --model my.model --count 5 --format create_list
python mock_data_factory.py --model my.model --count 50 --format loop
python mock_data_factory.py --model my.model --count 5 --format setup_method
python mock_data_factory.py --model hr.employee --count 5 --output fixtures.py
```

### `coverage_reporter.py`

```bash
python coverage_reporter.py --module /path/to/my_module
python coverage_reporter.py --module /path/to/my_module --format json --output coverage.json
python coverage_reporter.py --module /path/to/my_module --format html --output coverage.html
python coverage_reporter.py --module /path/to/my_module --threshold 80
```

---

## Azure DevOps Integration

### Pipeline YAML

```yaml
# azure-pipelines.yml
stages:
  - stage: OdooTests
    displayName: 'Odoo Module Tests'
    jobs:
      - job: UnitTests
        pool: { vmImage: 'ubuntu-22.04' }
        steps:
          - script: pip install -r requirements.txt
            displayName: 'Install Python dependencies'

          - script: |
              python odoo-test/scripts/test_runner.py \
                --module my_module \
                --config conf/project17.conf \
                --database project17 \
                --tags post_install \
                --output $(Build.ArtifactStagingDirectory)/test_results.xml \
                --output-format junit
            displayName: 'Run Odoo Tests'

          - task: PublishTestResults@2
            condition: always()
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '$(Build.ArtifactStagingDirectory)/test_results.xml'
              testRunTitle: 'Odoo Module Tests - $(Build.BuildId)'
              failTaskOnFailedTests: true

          - script: |
              python odoo-test/scripts/coverage_reporter.py \
                --module projects/my_project/my_module \
                --threshold 70 \
                --format json \
                --output $(Build.ArtifactStagingDirectory)/coverage.json
            displayName: 'Check Test Coverage'
```

### Posting to Azure DevOps Test Plans API

Use the integration pattern from `SKILL.md` to post results programmatically using the Azure DevOps REST API with a Personal Access Token.

---

## Integration with devops-plugin

This plugin works alongside the `devops-plugin` for full CI/CD workflows:

```
# 1. Run tests and generate JUnit XML
/odoo-test run my_module --config conf/project17.conf --database project17 \
    --output test_results.xml --output-format junit

# 2. Post to Azure DevOps (using devops-plugin)
/devops post-test-results --file test_results.xml --run-name "My Module Tests"
```

---

## Memory Files

The plugin includes three memory files for quick reference:

| File | Contents |
|------|----------|
| `memories/testing_patterns.md` | TransactionCase, HttpCase, SavepointCase patterns; `@tagged` reference table; assertion methods; setUp/tearDown patterns; compute/constraint/onchange testing |
| `memories/mock_data.md` | Realistic values by field type; common model fixtures (res.partner, sale.order, hr.employee, account.move); `env.ref()` patterns |
| `memories/common_test_cases.md` | Ready-to-adapt complete test suites for Sales, HR, Website/Portal, Accounting, and Inventory modules |

---

## Hook Triggers

The plugin's PostToolUse hooks automatically suggest testing actions when:

| Trigger | Suggestion |
|---------|-----------|
| New `.py` file in `models/` | `/odoo-test generate <model.name>` |
| `__manifest__.py` created/modified | Install and run tests command |
| `ir.model.access.csv` created | Security access control tests |
| `@api.constrains` added | Constraint test pattern |
| `@api.depends` added | Compute field test pattern |
| `action_*` method added | Workflow test pattern |
| `@http.route` added | HttpCase test pattern |
| Test file written | Remind to import in `__init__.py` |
| `SavepointCase` used | Warn about removal in Odoo 16+ |

---

## Version Support Matrix

| Feature | Odoo 14 | 15 | 16 | 17 | 18 | 19 |
|---------|---------|-----|-----|-----|-----|-----|
| TransactionCase | Yes | Yes | Yes | Yes | Yes | Yes |
| HttpCase | Yes | Yes | Yes | Yes | Yes | Yes |
| SavepointCase | Yes | Yes | Removed | - | - | - |
| @tagged decorator | Yes | Yes | Yes | Yes | Yes | Yes |
| --test-tags path syntax | No | No | Yes | Yes | Yes | Yes |
| invalidate_recordset() | No | No | Yes | Yes | Yes | Yes |
| browser_js() | Yes | Yes | Yes | Dep | - | - |

---

## Migrating from v1.x

In v1.x the plugin exposed five separate slash commands (`/test-generate`, `/test-run`, `/test-coverage`, `/test-data`, `/e2e-test`). In v2.0 these are consolidated under a single `/odoo-test` command with sub-commands:

| v1.x command | v2.0 equivalent |
|---|---|
| `/test-generate my.model` | `/odoo-test generate my.model` |
| `/test-run my_module` | `/odoo-test run my_module` |
| `/test-coverage /path` | `/odoo-test coverage /path` |
| `/test-data --model m` | `/odoo-test data --model m` |
| `/e2e-test my_module` | `/odoo-test e2e my_module` |

The standalone `/odoo-test my_module` (no sub-command) still runs the full workflow as before. All options remain the same within each sub-command.

Natural language continues to work unchanged -- describe what you need and the skill routes to the correct sub-command automatically.

---

## Common Issues

### Tests Not Discovered

Ensure `tests/__init__.py` imports your test file:
```python
# tests/__init__.py
from . import test_my_model
```

### Tests Running Slowly

Disable mail operations in `setUpClass`:
```python
cls.env = cls.env(context={
    **cls.env.context,
    'mail_notrack': True,
    'tracking_disable': True,
})
```

### AccessError in Tests

Use `sudo()` or add user to required group:
```python
self.env['my.model'].sudo().create({...})
# or
self.env.user.groups_id |= self.env.ref('my_module.group_manager')
```

### Computed Fields Not Updating

Invalidate cache after dependency changes:
```python
record.write({'dependency': new_value})
record.invalidate_recordset(['computed_field'])  # Odoo 16+
```

---

## License

MIT -- See plugin.json for full license information.

## Author

TaqaTechno -- support@example.com

https://github.com/taqat-techno/plugins/tree/main/odoo-test-plugin
