---
title: 'Odoo Security — Full Module Audit'
read_only: true
type: 'command'
description: 'Run a comprehensive security audit across all layers of an Odoo module: model access rules, HTTP route authentication, sudo() usage, SQL injection risks, and record rule coverage.'
---

# /odoo-security <module-path>

Run a full, multi-layer security audit on an Odoo module. This is the primary command that orchestrates all sub-auditors and produces a unified severity-graded report.

## What It Checks

- **Model Access Rules** — Every model defined in `models/*.py` cross-referenced with `security/ir.model.access.csv`
- **HTTP Route Authentication** — `auth=` parameters, CSRF protection, and public route data exposure
- **sudo() Usage** — Classification of all `.sudo()` calls by risk level and context
- **SQL Injection Risks** — `env.cr.execute()` calls with string formatting
- **Record Rule Coverage** — Multi-company isolation and user scoping completeness
- **Field-Level Security** — Sensitive fields without `groups=` restrictions

## Usage

```
/odoo-security <module-path>
/odoo-security <module-path> --min-severity HIGH
/odoo-security <module-path> --skip-auditor sudo
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `module-path` | Yes | Absolute or relative path to the Odoo module directory |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--min-severity` | LOW | Only report issues at this severity or above: CRITICAL, HIGH, MEDIUM, LOW |
| `--skip-auditor` | none | Skip specific auditor: `access`, `routes`, `sudo` |
| `--json` | false | Output report as machine-readable JSON |
| `--output <file>` | stdout | Write report to file |
| `--exit-on-issues` | false | Exit with code 1 if any issues found (useful in CI) |

## Severity Levels

| Severity | Meaning | Action Required |
|----------|---------|-----------------|
| CRITICAL | Immediate security vulnerability | Fix before deployment |
| HIGH | Significant risk, likely exploitable | Fix within sprint |
| MEDIUM | Security weakness | Fix in next release |
| LOW | Minor improvement | Fix when convenient |

## Examples

```bash
# Full audit on a specific module
python scripts/security_auditor.py /c/odoo/odoo17/projects/my_project/my_module

# Only show HIGH and CRITICAL issues
python scripts/security_auditor.py /path/to/module --min-severity HIGH

# Audit for CI — fails build if issues found
python scripts/security_auditor.py /path/to/module --exit-on-issues

# Save JSON report
python scripts/security_auditor.py /path/to/module --json --output security-report.json

# Skip route auditing (module has no controllers)
python scripts/security_auditor.py /path/to/module --skip-auditor routes
```

## Sample Output

```
Running security audit on: /path/to/my_module
  Running access_checker... 2 CRITICAL, 1 HIGH
  Running route_auditor...  CLEAN
  Running sudo_finder...    1 MEDIUM

======================================================================
  ODOO SECURITY AUDIT REPORT
======================================================================
  Module:    my_module
  Path:      /path/to/my_module
  Date:      2026-02-23 14:30:00
  Risk Score: 65/100 — Significant vulnerabilities present

  SUMMARY
  ----------------------------------------
  CRITICAL      2 issues
  HIGH          1 issue
  MEDIUM        1 issue
  LOW           0 issues
  TOTAL         4 issues

  AUDITOR STATUS
  ----------------------------------------
  access_checker       3 issues
  route_auditor        0 issues
  sudo_finder          1 issue

  ISSUES (showing LOW+, 4 total)
  ======================================================================

  models/my_model.py
  [CRITICAL] models/my_model.py:15
    Model 'my.model' has no access rules in ir.model.access.csv
    FIX: Add entry: access_my_model_user,my.model user,model_my_model,[group],1,1,1,0
```

## Risk Score

The risk score (0-100) is computed from issue severity weights:
- CRITICAL = 4 points each
- HIGH = 3 points each
- MEDIUM = 2 points each
- LOW = 1 point each

Score interpretation:
- 80-100: CRITICAL risk — deploy is blocked
- 50-79: HIGH risk — significant issues need immediate attention
- 25-49: MEDIUM risk — schedule fixes
- 1-24: LOW risk — minor improvements needed
- 0: Clean — no issues detected

## When to Run

- Before every pull request merge
- After creating a new module
- After adding controllers or models
- After modifying `ir.model.access.csv`
- As part of CI/CD pipeline

## Integration with AI

When you run `/odoo-security`, the AI assistant will:

1. Execute the security audit scripts on the specified module
2. Analyze the findings in context of the Odoo version being used
3. Prioritize issues by severity and exploitability
4. Generate specific, production-ready remediation code for each issue
5. Create a `security_fixes.md` file with all recommended changes
6. Optionally apply the fixes directly if confirmed

The AI uses the knowledge in `odoo-security/SKILL.md` and `memories/` to provide context-aware remediation that respects Odoo's version-specific patterns.
