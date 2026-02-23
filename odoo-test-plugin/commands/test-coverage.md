---
title: 'Analyze Test Coverage'
read_only: false
type: 'command'
description: 'Scan an Odoo module to identify untested public methods and compute a coverage percentage'
---

# /test-coverage <module_path> [options]

Analyse an Odoo module's Python source files to identify which public methods lack test coverage. Reports coverage percentage per model, lists untested methods (prioritizing action_, constraint, and compute methods), and generates actionable recommendations.

## Usage

```
/test-coverage /c/odoo/odoo17/projects/myproject/my_module
/test-coverage . --threshold 80
/test-coverage /path/to/module --output report.json --format json
/test-coverage /path/to/module --output coverage.html --format html
```

## Natural Language Triggers

```
"Check test coverage for my module"
"What methods don't have tests?"
"Show me coverage report for my_module"
"Which methods need tests in the sale module?"
"Generate HTML coverage report"
"Is my test coverage above 80%?"
```

## Implementation

```python
import sys
import subprocess
from pathlib import Path

args_str = "${ARGS}".strip()
args_parts = args_str.split()

if not args_parts:
    print("Usage: /test-coverage <module_path> [--threshold N] [--format terminal|json|html] [--output FILE]")
    print()
    print("Examples:")
    print("  /test-coverage /c/odoo/odoo17/projects/myproject/my_module")
    print("  /test-coverage . --threshold 80")
    print("  /test-coverage /path/to/module --format html --output coverage.html")
    sys.exit(1)

module_path = args_parts[0]
extra_args = args_parts[1:]

script = Path(r"${PLUGIN_DIR}/odoo-test/scripts/coverage_reporter.py")
cmd = [sys.executable, str(script), "--module", module_path] + extra_args

print(f"Analysing test coverage for: {module_path}")
print()

result = subprocess.run(cmd, capture_output=False, text=True)
sys.exit(result.returncode)
```

## Coverage Report Sections

### Terminal Output Example

```
════════════════════════════════════════════════════════════════════════
  ODOO TEST COVERAGE REPORT — my_module
════════════════════════════════════════════════════════════════════════
  Module path: /c/odoo/odoo17/projects/myproject/my_module
  Models analysed: 4
  Test methods found: 12

  Model                               File                       Methods  Tested  Coverage
  ────────────────────────────────────────────────────────────────────────────────────────
  my.model                            models/my_model.py              8       4     50.0%
  my.model (inherited)                models/sale_ext.py              3       3    100.0%
  my.wizard                           wizard/my_wizard.py             2       0      0.0%
  sale.order (inherited)              models/sale_order.py            5       3     60.0%
  ────────────────────────────────────────────────────────────────────────────────────────
  TOTAL                                                              18      10     55.6%

  Overall Coverage: [██████████░░░░░░░░░░] 55.6%

  Untested Methods (8 total):
    my.model.action_confirm [ACTION]  (line 45)
    my.model.action_cancel [ACTION]  (line 52)
    my.model._compute_amount [COMPUTE]  (line 78)
    my.wizard.action_apply [ACTION]  (line 23)
    ...

  Recommendations:
    • Coverage is below 80% target. Focus on untested action_ methods.
    • 2 constraint method(s) untested! These are high-priority.
    • Use /test-generate to create test skeletons for untested models.
```

### Coverage Thresholds

| Coverage % | Status | CI Gate |
|-----------|--------|---------|
| 90-100% | Excellent | Pass |
| 80-89% | Good | Pass (recommended minimum) |
| 50-79% | Needs improvement | Warn |
| 0-49% | Critical | Fail |

### Priority Order for Adding Tests

1. **Constraints** (`@constrains`) - Data integrity, must be 100%
2. **Action methods** (`action_*`) - User workflow critical paths
3. **Compute fields** (`@depends`) - Business logic correctness
4. **Onchange methods** (`@onchange`) - UI behavior
5. **Helper methods** - Internal logic

## Output Formats

### JSON Format

```bash
/test-coverage . --format json --output coverage.json
```

Output structure:
```json
{
  "module_name": "my_module",
  "overall_coverage": 55.6,
  "total_methods": 18,
  "tested_methods": 10,
  "models": [
    {
      "model_name": "my.model",
      "coverage_pct": 50.0,
      "untested_methods": [
        {"name": "action_confirm", "line": 45, "is_action": true, ...}
      ]
    }
  ]
}
```

### HTML Format

```bash
/test-coverage . --format html --output coverage.html
```

Produces a self-contained HTML file with a styled table and coverage bars — suitable for sharing with team or attaching to pull requests.

## Using with CI/CD

```bash
# Fail build if coverage drops below 80%
python coverage_reporter.py --module . --threshold 80
# Returns exit code 1 if coverage < 80%, 0 if passing

# In Azure DevOps pipeline:
# - script: python "${PLUGIN_DIR}/odoo-test/scripts/coverage_reporter.py"
#           --module projects/my_project/my_module
#           --threshold 80
#           --format json
#           --output coverage.json
```

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--threshold N` | Exit code 1 if coverage below N% | 0 (disabled) |
| `--format` | `terminal`, `json`, or `html` | `terminal` |
| `--output FILE` | Save report to file | stdout |

---

*Part of odoo-test-plugin v1.0*
