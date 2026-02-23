# odoo-test-plugin

Comprehensive Odoo testing toolkit for Claude Code. Generates test skeletons, runs test suites with colored output, creates realistic mock data, analyzes test coverage, and integrates with Azure DevOps for CI/CD test reporting. Supports Odoo versions 14 through 19.

## Features

- **Test Generation** - Auto-generates complete test class skeletons by reading model source files
- **Test Runner** - Colored PASS/FAIL output with JUnit XML and JSON report generation
- **Mock Data Factory** - Realistic field-type-aware fixture generation for test setUp methods
- **Coverage Reporter** - Identifies untested methods with per-model and overall coverage percentages
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
C:\odoo\tmp\plugins\odoo-test-plugin\
```

The plugin is auto-loaded by Claude Code when the `.claude-plugin/plugin.json` is detected.

## Quick Start

### 1. Generate a Test File for a Model

```
/test-generate sale.order --module /c/odoo/odoo17/projects/myproject/my_module
```

Reads the model's Python source, detects field types, and creates:
```
my_module/tests/test_sale_order.py
my_module/tests/__init__.py  (if missing)
```

### 2. Run Tests for a Module

```
/test-run my_module --config conf/project17.conf --database project17
```

Output:
```
PASS  my_module.tests.test_my_model.TestMyModel.test_create_minimal
PASS  my_module.tests.test_my_model.TestMyModel.test_write_name
FAIL  my_module.tests.test_my_model.TestMyModel.test_constraint_amount

Total Tests: 3 | Passed: 2 | Failed: 1 | Duration: 4.23s
```

### 3. Check Test Coverage

```
/test-coverage /c/odoo/odoo17/projects/myproject/my_module
```

Shows coverage percentage per model and lists untested methods.

### 4. Generate Mock Data Fixtures

```
/test-data --model res.partner --count 5
/test-data --model hr.employee --count 3 --format setup_method
```

Produces Python code ready to paste into `setUpClass()`.

### 5. Full Testing Workflow

```
/odoo-test my_module --config conf/project17.conf --database project17
```

Runs coverage analysis, generates missing test skeletons, executes the test suite, and reports results.

---

## Commands Reference

### `/odoo-test <module> [options]`

Full testing workflow: discover module, analyze coverage, optionally generate tests, run suite, report.

| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | Odoo config file | Auto-detected |
| `--database NAME` | Database name | Auto-detected |
| `--tags TAGS` | Test tag filter | `post_install` |
| `--generate-missing` | Auto-generate tests for models without them | False |
| `--coverage-only` | Only run coverage analysis | False |
| `--threshold N` | Fail if coverage below N% | 0 |
| `--output FILE` | Save report to file | stdout |

### `/test-generate <model> [options]`

Generate a complete `TransactionCase` test skeleton for an Odoo model.

```bash
# Basic usage (generic skeleton)
/test-generate my.model

# With module path (enables field type detection)
/test-generate my.model --module /c/odoo/odoo17/projects/myproject/my_module

# Preview without writing to disk
/test-generate my.model --module /path/to/module --dry-run

# Overwrite existing file
/test-generate my.model --module /path/to/module --force

# Custom output location
/test-generate my.model --module /path/to/module --output /custom/path/test_my.py
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

### `/test-run <module> [options]`

Execute Odoo module tests with colored terminal output.

```bash
# Run all tests
/test-run my_module --config conf/project17.conf --database project17

# Filter by tag
/test-run my_module --config conf/project17.conf --database project17 --tags post_install

# Specific test class
/test-run my_module --config conf/project17.conf --database project17 --test-class TestMyModel

# Specific method
/test-run my_module --config conf/project17.conf --database project17 \
    --test-class TestMyModel --test-method test_create_order

# Show full Odoo logs
/test-run my_module --config conf/project17.conf --database project17 --show-logs

# Generate JUnit XML
/test-run my_module --config conf/project17.conf --database project17 \
    --output test_results.xml --output-format junit

# Generate JSON report
/test-run my_module --config conf/project17.conf --database project17 \
    --output report.json --output-format json
```

### `/test-coverage <module_path> [options]`

Analyze test coverage for an Odoo module.

```bash
# Terminal report
/test-coverage /c/odoo/odoo17/projects/myproject/my_module

# With coverage threshold (exit code 1 if below)
/test-coverage /c/odoo/odoo17/projects/myproject/my_module --threshold 80

# JSON report for CI/CD
/test-coverage /path/to/module --format json --output coverage.json

# HTML report for team sharing
/test-coverage /path/to/module --format html --output coverage.html
```

### `/test-data --model <model> [options]`

Generate realistic mock data Python code for test fixtures.

```bash
# 5 partners with realistic names, emails, addresses
/test-data --model res.partner --count 5

# Sale orders with line items
/test-data --model sale.order --count 3

# Custom model with field detection
/test-data --model my.model --count 10 --module /path/to/module

# Formats
/test-data --model my.model --count 5 --format individual   # One create() per record
/test-data --model my.model --count 5 --format create_list  # Batch create([...])
/test-data --model my.model --count 50 --format loop        # for loop
/test-data --model my.model --count 5 --format setup_method # Full setUpClass() snippet

# Save to file
/test-data --model hr.employee --count 10 --output setup_fixtures.py
```

---

## Scripts Reference

Scripts can be run standalone without Claude Code.

### `test_generator.py`

```bash
# Generate test for known model
python test_generator.py --model sale.order --module /path/to/module

# Dry run (print to stdout)
python test_generator.py --model my.model --module /path/to/module --dry-run

# Force overwrite
python test_generator.py --model my.model --module /path/to/module --force

# Custom output path
python test_generator.py --model my.model --module /path/to/module --output /path/test_my.py
```

### `test_runner.py`

```bash
# Basic run
python test_runner.py --module my_module --config conf/project17.conf --database project17

# With tag filter
python test_runner.py --module my_module --config conf/p17.conf --database db17 --tags post_install

# Specific class and method
python test_runner.py --module my_module --config conf/p17.conf --database db17 \
    --test-class TestMyModel --test-method test_create

# JUnit XML for Azure DevOps
python test_runner.py --module my_module --config conf/p17.conf --database db17 \
    --output test_results.xml --output-format junit

# Show full Odoo output
python test_runner.py --module my_module --config conf/p17.conf --database db17 --show-logs
```

### `mock_data_factory.py`

```bash
# Known model (uses pre-built template)
python mock_data_factory.py --model res.partner --count 5

# Custom model with field detection
python mock_data_factory.py --model my.model --count 10 --module /path/to/module

# Different output formats
python mock_data_factory.py --model my.model --count 5 --format create_list
python mock_data_factory.py --model my.model --count 50 --format loop
python mock_data_factory.py --model my.model --count 5 --format setup_method

# Write to file
python mock_data_factory.py --model hr.employee --count 5 --output fixtures.py
```

### `coverage_reporter.py`

```bash
# Terminal report
python coverage_reporter.py --module /path/to/my_module

# JSON output
python coverage_reporter.py --module /path/to/my_module --format json --output coverage.json

# HTML output
python coverage_reporter.py --module /path/to/my_module --format html --output coverage.html

# CI gate (exit code 1 if below threshold)
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
/test-run my_module --config conf/project17.conf --database project17 \
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
| New `.py` file in `models/` | `/test-generate <model.name>` |
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

MIT — See plugin.json for full license information.

## Author

TaqaTechno — support@example.com

https://github.com/taqat-techno/plugins/tree/main/odoo-test-plugin
