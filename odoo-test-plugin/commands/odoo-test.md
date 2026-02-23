---
title: 'Odoo Testing Workflow'
read_only: false
type: 'command'
description: 'Full Odoo testing workflow: generate tests, run suite, analyze coverage for a module'
---

# /odoo-test <module> [options]

Run the complete Odoo testing workflow for a module: detect missing tests, generate skeletons, run the test suite, and report coverage.

## Usage

```
/odoo-test <module_name>
/odoo-test my_module --config conf/project17.conf --database project17
/odoo-test my_module --generate-missing
/odoo-test my_module --coverage-only
/odoo-test my_module --tags post_install
```

## Natural Language Triggers

```
"Run tests for my_module"
"Test the sale order customization"
"Check coverage for my hr module"
"Generate and run all tests for my module"
"What tests are missing for my_module?"
```

## Full Workflow

When invoked, this command executes the following steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                   ODOO TEST WORKFLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Step 1: DISCOVER  →  Find module path and config               │
│  Step 2: ANALYSE   →  Scan models and count public methods       │
│  Step 3: GENERATE  →  Create test files for untested models      │
│  Step 4: RUN       →  Execute test suite with Odoo runner        │
│  Step 5: REPORT    →  Show PASS/FAIL summary and coverage %      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Implementation

### Step 1: Discover Module

```python
import os
import glob
from pathlib import Path

module_name = "${ARGS}".split()[0]
odoo_root = Path(r"C:\odoo")

# Search for module across all Odoo versions
found_modules = list(odoo_root.glob(f"odoo*/projects/*/{module_name}"))
if not found_modules:
    found_modules = list(odoo_root.glob(f"odoo*/projects/*/*/{module_name}"))

if not found_modules:
    print(f"[ERROR] Module '{module_name}' not found under C:\\odoo\\odoo*\\projects\\")
    print("Hint: Check the module name and ensure it's in a projects\\ directory")
else:
    module_path = found_modules[0]
    print(f"[OK] Found module: {module_path}")
```

### Step 2: Run Coverage Analysis

```bash
# Find module path first, then run coverage reporter
python "${PLUGIN_DIR}/odoo-test/scripts/coverage_reporter.py" \
    --module "${MODULE_PATH}"
```

### Step 3: Generate Missing Tests

```bash
python "${PLUGIN_DIR}/odoo-test/scripts/test_generator.py" \
    --model "${MODEL}" \
    --module "${MODULE_PATH}"
```

### Step 4: Run Tests

```bash
python "${PLUGIN_DIR}/odoo-test/scripts/test_runner.py" \
    --module "${MODULE_NAME}" \
    --config "${CONFIG}" \
    --database "${DATABASE}" \
    --tags "post_install"
```

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--config` | Path to Odoo config file | Auto-detected |
| `--database` | Database name | Auto-detected |
| `--tags` | Test tags to run | `post_install` |
| `--generate-missing` | Auto-generate tests for untested models | False |
| `--coverage-only` | Only run coverage analysis, skip test execution | False |
| `--threshold` | Minimum coverage % (fail if below) | 0 (disabled) |
| `--output` | Save report to file | stdout |

## Output Example

```
────────────────────────────────────────────────────────────────
Odoo Test Runner — my_module
────────────────────────────────────────────────────────────────
[INFO] Config:   conf/project17.conf
[INFO] Database: project17
[INFO] Module:   my_module
[INFO] Tags:     post_install

PASS  my_module.tests.test_my_model.TestMyModel.test_create_minimal
PASS  my_module.tests.test_my_model.TestMyModel.test_write_name
FAIL  my_module.tests.test_my_model.TestMyModel.test_constraint_amount

────────────────────────────────────────────────────────────────
Test Results Summary
────────────────────────────────────────────────────────────────
  TESTS FAILED

  Total Tests:         3
  Passed:              2
  Failed:              1
  Errors:              0
  Skipped:             0
  Duration:            4.23s
```

## Integration with /devops Plugin

This command integrates with the devops-plugin for Azure DevOps reporting:

```
/odoo-test my_module --output test_results.xml --format junit
# Then use devops-plugin to post results to Azure DevOps
```

---

*Part of odoo-test-plugin v1.0*
