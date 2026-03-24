---
title: 'Odoo Testing Workflow'
read_only: false
type: 'command'
description: 'Odoo testing toolkit - generate, mock data, run, coverage, and E2E tests'
argument-hint: '[generate|data|run|coverage|e2e] <model|module> [args...]'
---

# /odoo-test [sub-command] [args...]

Parse the first token of `$ARGUMENTS` and route:

| Token | Action |
|-------|--------|
| *(empty)* | Show help + offer full workflow (generate > run > coverage) |
| `generate` | Generate TransactionCase/HttpCase test skeleton |
| `data` | Generate mock data factory for setUp |
| `run` | Run test suite with colored output |
| `coverage` | Scan for untested methods + coverage % |
| `e2e` | Generate/run Playwright E2E tests |
| *(other)* | Treat as module name, run full workflow |

```
/odoo-test                              Show help + offer full workflow
/odoo-test generate <model> [module]    Generate test skeleton
/odoo-test data <model> [--count N]     Generate mock data factory
/odoo-test run <module> [--tags X]      Run test suite
/odoo-test coverage <module>            Coverage analysis
/odoo-test e2e <module> [--url X]       Playwright E2E tests
```

## Execution

Use the odoo-test skill for:
- Test generation patterns (TransactionCase, HttpCase, SavepointCase)
- Mock data factory patterns (field-type-aware generation)
- Test execution with config/database auto-detection
- Coverage analysis methodology (static method comparison)
- E2E test scaffolding (Playwright + page objects)
- Azure DevOps CI integration patterns

Scripts at `${CLAUDE_PLUGIN_ROOT}/odoo-test/scripts/`:
- `test_generator.py` - Generate test skeletons from models
- `mock_data_factory.py` - Generate realistic test data
- `test_runner.py` - Execute test suites with colored output
- `coverage_reporter.py` - Test coverage analysis
