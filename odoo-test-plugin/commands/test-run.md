---
title: 'Run Odoo Tests'
read_only: false
type: 'command'
description: 'Run Odoo test suite for a module with colored output, tag filtering, and optional JUnit XML report'
---

# /test-run <module> [options]

Execute the Odoo test suite for a module with colored PASS/FAIL output, support for test tag filtering, class/method selection, and JUnit XML output for CI/CD pipelines (Azure DevOps, Jenkins).

## Usage

```
/test-run my_module --config conf/project17.conf --database project17
/test-run my_module --config conf/project17.conf --database project17 --tags post_install
/test-run my_module --config conf/project17.conf --database project17 --test-class TestMyModel
/test-run my_module --config conf/project17.conf --database project17 --show-logs
/test-run my_module --config conf/project17.conf --database project17 --output results.xml
```

## Natural Language Triggers

```
"Run tests for my_module"
"Run post_install tests"
"Run the TestSaleOrder test class"
"Run test_create_order method"
"Show all logs while running tests"
"Generate JUnit XML test results"
```

## Implementation

```python
import sys
import subprocess
from pathlib import Path

args_str = "${ARGS}".strip()
args_parts = args_str.split()

if not args_parts:
    print("Usage: /test-run <module> --config <conf> --database <db> [options]")
    print()
    print("Examples:")
    print("  /test-run my_module --config conf/project17.conf --database project17")
    print("  /test-run my_module --config conf/project17.conf --database project17 --tags post_install")
    print("  /test-run my_module --config conf/project17.conf --database project17 --show-logs")
    sys.exit(1)

module_name = args_parts[0]
extra_args = args_parts[1:]

script = Path(r"${PLUGIN_DIR}/odoo-test/scripts/test_runner.py")
cmd = [sys.executable, str(script), "--module", module_name] + extra_args

print(f"Starting test run for module: {module_name}")
print(f"Command: {' '.join(cmd)}")
print()

result = subprocess.run(cmd, capture_output=False, text=True)
sys.exit(result.returncode)
```

## Test Tag Reference

```bash
# Run all post_install tests (most common)
/test-run my_module --config conf/p17.conf --database db17 --tags post_install

# Run only tests tagged 'standard'
/test-run my_module --config conf/p17.conf --database db17 --tags standard

# Run all tests except slow ones
/test-run my_module --config conf/p17.conf --database db17 --tags standard,-slow

# Run a specific test class
/test-run my_module --config conf/p17.conf --database db17 --test-class TestMyModel

# Run a specific test method
/test-run my_module --config conf/p17.conf --database db17 --test-class TestMyModel --test-method test_create_order
```

## Output Formats

### Terminal (Default)

```
────────────────────────────────────────────────────────────────
Odoo Test Runner — my_module
────────────────────────────────────────────────────────────────
[INFO] Config:   conf/project17.conf
[INFO] Database: project17
[INFO] Tags:     post_install

PASS  my_module.tests.test_sale.TestSaleOrder.test_create_order
PASS  my_module.tests.test_sale.TestSaleOrder.test_confirm_order
FAIL  my_module.tests.test_sale.TestSaleOrder.test_invoice_flow

────────────────────────────────────────────────────────────────
Test Results Summary
────────────────────────────────────────────────────────────────
  TESTS FAILED

  Total Tests:         3
  Passed:              2      ← green
  Failed:              1      ← red
  Errors:              0
  Skipped:             0
  Duration:            5.12s

Failed Tests:
  ✗ my_module.tests.test_sale.TestSaleOrder.test_invoice_flow
    AssertionError: 'draft' != 'posted'
```

### JUnit XML (for Azure DevOps)

```bash
/test-run my_module --config conf/p17.conf --database db17 \
    --output test_results.xml --output-format junit
```

Produces standard JUnit XML suitable for `PublishTestResults@2` Azure DevOps task.

### JSON Report

```bash
/test-run my_module --config conf/p17.conf --database db17 \
    --output report.json --output-format json
```

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--config` | Odoo config file path | Required |
| `--database` | Database name | Required |
| `--tags` | Test tags (comma-separated, use `-tag` to exclude) | `post_install` |
| `--test-class` | Run only this test class | All classes |
| `--test-method` | Run only this method (requires --test-class) | All methods |
| `--install` | Use `-i` flag (install) instead of `-u` (update) | False |
| `--show-logs` | Show full Odoo log output | False |
| `--output` | Report output file | stdout |
| `--output-format` | `junit` or `json` | `junit` |

## Common Odoo Test Commands Reference

```bash
# Quick module test (update + test)
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module --stop-after-init

# Install fresh + test
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -i my_module --stop-after-init

# Specific test class
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=/my_module:TestMyModel --stop-after-init

# With debug logging
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module \
    --log-level=debug --log-handler=odoo.tests:DEBUG \
    --stop-after-init
```

---

*Part of odoo-test-plugin v1.0*
