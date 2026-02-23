# Odoo Security Plugin

A comprehensive security auditing plugin for Odoo modules (versions 14-19). Performs static analysis across all security layers: model access rules, HTTP route authentication, sudo() usage patterns, SQL injection risks, and record rule completeness.

## Features

- **Multi-layer analysis**: Checks Odoo's 3-layer security model simultaneously
- **Severity grading**: Issues classified as CRITICAL / HIGH / MEDIUM / LOW
- **Version support**: Works with Odoo 14, 15, 16, 17, 18, and 19
- **Actionable output**: Every issue includes a specific remediation code snippet
- **CI/CD integration**: Exit codes and JSON output for pipeline integration
- **File system hooks**: Automatic suggestions when creating models or controllers
- **Standalone scripts**: Each auditor can run independently

---

## Installation

### Option 1: Claude Code Plugin (Recommended)

Place the plugin directory in your Claude plugins folder:

```bash
# Clone or copy the plugin
cp -r odoo-security-plugin ~/.claude/plugins/odoo-security-plugin

# Or on Windows:
xcopy /E /I odoo-security-plugin "%USERPROFILE%\.claude\plugins\odoo-security-plugin"
```

The plugin will be automatically available in Claude Code sessions. The AI will:
- Suggest `/check-access` when you create a new Python file in `models/`
- Suggest `/check-routes` when you create a new controller file
- Suggest `/check-access` when you create or edit `ir.model.access.csv`

### Option 2: Standalone Python Scripts

No installation needed. Run directly from the scripts directory:

```bash
# Clone the repository
git clone https://github.com/taqat-techno/plugins
cd plugins/odoo-security-plugin

# Run directly (Python 3.8+ required, no additional packages)
python odoo-security/scripts/security_auditor.py /path/to/your/module
```

---

## Quick Start

### Run a Full Audit

```bash
# Full security audit on a module
python odoo-security/scripts/security_auditor.py /path/to/odoo17/projects/my_project/my_module

# Example with a real Odoo installation on Windows
python "C:\odoo\tmp\plugins\odoo-security-plugin\odoo-security\scripts\security_auditor.py" \
    "C:\odoo\odoo17\projects\my_project\my_module"
```

### Run Individual Auditors

```bash
# Check model access rules only
python odoo-security/scripts/access_checker.py /path/to/module

# Check HTTP route security only
python odoo-security/scripts/route_auditor.py /path/to/module

# Find sudo() usage and classify risk
python odoo-security/scripts/sudo_finder.py /path/to/module
```

---

## Usage Reference

### security_auditor.py (Orchestrator)

```
Usage: python security_auditor.py <module_path> [options]

Options:
  --min-severity {CRITICAL,HIGH,MEDIUM,LOW}
                        Minimum severity to report (default: LOW)
  --exit-on-issues      Exit with code 1 if issues found (CI integration)
  --json                Output as machine-readable JSON
  --output <file>       Write report to file
  --skip-auditor {access,routes,sudo}
                        Skip specific sub-auditor (repeatable)

Exit codes:
  0 = No issues found at min-severity or above
  1 = Issues found at min-severity or above
  2 = Usage error (invalid path, etc.)

Examples:
  # Default: all issues
  python security_auditor.py /path/to/module

  # CI: fail on CRITICAL/HIGH only
  python security_auditor.py /path/to/module --min-severity HIGH --exit-on-issues

  # JSON report for tooling
  python security_auditor.py /path/to/module --json --output report.json

  # Skip route auditor for data-only modules
  python security_auditor.py /path/to/module --skip-auditor routes
```

### access_checker.py

```
Usage: python access_checker.py <module_path> [options]

Options:
  --json      Output as JSON
  --verbose   Detailed output

What it checks:
  - Models in models/*.py without ir.model.access.csv entries → CRITICAL
  - TransientModel (wizards) without access rules → HIGH
  - Empty group_id in CSV (grants access to ALL users) → HIGH
  - Overly permissive permissions for non-manager groups → MEDIUM
  - Unknown group references → LOW
  - Models with company_id but no record rules → HIGH
```

### route_auditor.py

```
Usage: python route_auditor.py <module_path> [options]

Options:
  --json      Output as JSON
  --verbose   Detailed output

What it checks:
  - auth='none' routes without API key validation → CRITICAL
  - Missing auth= parameter → HIGH
  - auth='public' accessing sensitive models with sudo() → HIGH
  - csrf=False on user-authenticated POST routes → HIGH
  - sudo() in public/portal controller → HIGH/MEDIUM
  - GET+POST mixed methods → MEDIUM
  - API routes without CORS configuration → LOW
  - SQL injection in controllers → HIGH
```

### sudo_finder.py

```
Usage: python sudo_finder.py <module_path> [options]

Options:
  --json      Output as JSON
  --verbose   Show code context around each finding
  --all       Show ALL sudo() calls including safe ones

Severity classification:
  CRITICAL  sudo() in auth='none'/'public' route with sensitive model
  HIGH      sudo() in public route, or accessing sensitive models
  MEDIUM    sudo() in loop, unscoped sudo(), sudo() in wizard
  LOW       sudo() needing documentation review
  OK        Known-safe patterns (mail, audit logs, config reads)
```

---

## Sample Output

### Full Audit Report

```
Running security audit on: /path/to/my_module
  Running access_checker... 2 CRITICAL, 1 HIGH
  Running route_auditor...  1 HIGH
  Running sudo_finder...    1 MEDIUM

======================================================================
  ODOO SECURITY AUDIT REPORT
======================================================================
  Module:    my_module
  Path:      /path/to/my_module
  Date:      2026-02-23 14:30:00
  Risk Score: 72/100 — Significant vulnerabilities present

  SUMMARY
  ----------------------------------------
  CRITICAL      2 issues
  HIGH          2 issues
  MEDIUM        1 issue
  LOW           0 issues
  TOTAL         5 issues

  AUDITOR STATUS
  ----------------------------------------
  access_checker       3 issues
  route_auditor        1 issue
  sudo_finder          1 issue

  ISSUES (showing LOW+, 5 total)
  ======================================================================

  models/my_model.py
  [CRITICAL] models/my_model.py:15
    Model 'my.model' (class MyModel) has no access rules in ir.model.access.csv.
    Expected CSV entry with model_id:id = 'model_my_model'
    FIX: Add: access_my_model_user,my.model user,model_my_model,[group],1,1,1,0

  [CRITICAL] models/my_wizard.py:8
    Transient (wizard) 'my.wizard' has no access rules in ir.model.access.csv.
    FIX: Add: access_my_wizard_user,my.wizard user,model_my_wizard,[group],1,1,1,1

  [HIGH] models/my_model.py:52
    File 'my_model.py' defines a model with company_id field, but no record rules
    XML file (security/rules_*.xml) was found.
    FIX: Create security/rules_my_module.xml with multi-company domain rule.

  controllers/main.py
  [HIGH] controllers/main.py:34
    Route ['/orders'] uses auth='none' but no API key validation detected in
    method 'get_orders'. This route is completely unauthenticated.
    FIX: Add API key validation or change auth='user' for internal routes.

  models/my_model.py
  [MEDIUM] models/my_model.py:89
    sudo() inside a loop in method 'compute_totals'. Each iteration re-elevates
    privileges unnecessarily.
    FIX: Move sudo() before loop, use read_group() with all record IDs.

======================================================================
```

### JSON Output

```json
{
  "module": "my_module",
  "module_path": "/path/to/my_module",
  "audit_date": "2026-02-23T14:30:00",
  "risk_score": 72,
  "risk_label": "HIGH",
  "risk_description": "Significant vulnerabilities present",
  "summary": {
    "total": 5,
    "by_severity": {
      "CRITICAL": 2,
      "HIGH": 2,
      "MEDIUM": 1,
      "LOW": 0
    }
  },
  "issues": [
    {
      "severity": "CRITICAL",
      "type": "missing_access_rule",
      "file": "models/my_model.py",
      "line": 15,
      "message": "Model 'my.model' has no access rules...",
      "remediation": "Add entry to security/ir.model.access.csv..."
    }
  ]
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/security-audit.yml
name: Odoo Security Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-audit:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run Security Audit
        run: |
          python ./plugins/odoo-security-plugin/odoo-security/scripts/security_auditor.py \
            ./projects/my_project/my_module \
            --min-severity HIGH \
            --exit-on-issues \
            --json \
            --output security-report.json

      - name: Upload Security Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: security-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Install: cp this file .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

PLUGIN_DIR="$(git rev-parse --show-toplevel)/plugins/odoo-security-plugin"
AUDITOR="$PLUGIN_DIR/odoo-security/scripts/security_auditor.py"

# Find changed modules
CHANGED_FILES=$(git diff --cached --name-only)
CHANGED_MODULES=$(echo "$CHANGED_FILES" | grep -E '^(projects|odoo[0-9]+/projects)/' | \
    awk -F'/' '{print $1"/"$2"/"$3}' | sort -u)

EXIT_CODE=0

for MODULE in $CHANGED_MODULES; do
    if [ -f "$MODULE/__manifest__.py" ]; then
        echo "Auditing security for: $MODULE"
        python "$AUDITOR" "$MODULE" --min-severity CRITICAL --exit-on-issues
        if [ $? -ne 0 ]; then
            echo "CRITICAL security issues found in $MODULE. Fix before committing."
            EXIT_CODE=1
        fi
    fi
done

exit $EXIT_CODE
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Security Audit') {
            steps {
                script {
                    def result = sh(
                        script: """
                            python plugins/odoo-security-plugin/odoo-security/scripts/security_auditor.py \
                                ${WORKSPACE}/projects/my_project/my_module \
                                --min-severity HIGH \
                                --json \
                                --output security-report.json
                        """,
                        returnStatus: true
                    )
                    if (result != 0) {
                        archiveArtifacts 'security-report.json'
                        error("Security audit failed — HIGH or CRITICAL issues found")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security-report.json', allowEmptyArchive: true
                }
            }
        }
    }
}
```

---

## Plugin Structure

```
odoo-security-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata and configuration
├── odoo-security/
│   ├── SKILL.md                 # 700+ line AI skill definition
│   └── scripts/
│       ├── security_auditor.py  # Master orchestrator — run this
│       ├── access_checker.py    # Model access rule checker
│       ├── route_auditor.py     # HTTP route security auditor
│       └── sudo_finder.py       # sudo() risk classifier
├── commands/
│   ├── odoo-security.md         # /odoo-security command
│   ├── security-audit.md        # /security-audit command
│   ├── check-access.md          # /check-access command
│   ├── find-sudo.md             # /find-sudo command
│   └── check-routes.md          # /check-routes command
├── memories/
│   ├── security_patterns.md     # Severity-graded patterns with fixes
│   ├── access_rules.md          # Complete ir.model.access.csv reference
│   └── odoo_vulnerabilities.md  # Top 8 Odoo vulnerabilities with examples
├── hooks/
│   └── hooks.json               # File system event triggers
└── README.md                    # This file
```

---

## What Gets Checked

### Access Control Layer

| Check | Severity | Description |
|-------|----------|-------------|
| Model without CSV entry | CRITICAL | Any model with `_name` but no access rule |
| Wizard without CSV entry | HIGH | TransientModel without access rule |
| Empty group_id in CSV | HIGH | Grants access to ALL authenticated users |
| Overly permissive perms | MEDIUM | DELETE for non-manager groups |
| No multi-company rule | HIGH | Model with company_id but no record rules |

### Route Security Layer

| Check | Severity | Description |
|-------|----------|-------------|
| auth='none' without auth code | CRITICAL | Completely unauthenticated route |
| Missing auth= parameter | HIGH | Implicit default, not explicit |
| sudo() + sensitive model in public | HIGH | IDOR risk |
| csrf=False on user route | HIGH | CSRF vulnerability |
| auth='public' + sensitive model | MEDIUM | Potential data exposure |
| SQL injection in controller | HIGH | String formatting in execute() |

### sudo() Usage Layer

| Check | Severity | Description |
|-------|----------|-------------|
| sudo() in public route + sensitive model | CRITICAL | Bypasses all access controls |
| sudo() in public route | HIGH | Potential privilege escalation |
| sudo() accessing sensitive model | HIGH | Unnecessary broad access |
| sudo() in loop | MEDIUM | Performance + security smell |
| Unscoped sudo() | MEDIUM | No domain filter applied |

---

## Supported Odoo Versions

| Version | Status | Notes |
|---------|--------|-------|
| Odoo 14 | Supported | Legacy auth patterns detected |
| Odoo 15 | Supported | website auth_signup_token handling |
| Odoo 16 | Supported | Bootstrap 5 / ir.http refactor aware |
| Odoo 17 | Supported (Primary) | _check_access() API aware |
| Odoo 18 | Supported | OAuth 2.0 patterns recognized |
| Odoo 19 | Supported | REST API framework patterns |

---

## Requirements

- Python 3.8 or higher
- No external packages required (uses Python standard library only)
- Compatible with Windows, macOS, and Linux

---

## Author & License

**Author**: TAQAT Techno
**Email**: support@example.com
**GitHub**: https://github.com/taqat-techno
**License**: MIT

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-check`
3. Add your security check to the appropriate script
4. Update SKILL.md with documentation for the new check
5. Test against an Odoo module with known issues
6. Submit a pull request

### Adding a New Check

1. Identify the check category: access, routes, or sudo
2. Add detection logic to the appropriate script
3. Return an issue dict with: `severity`, `type`, `file`, `line`, `message`
4. Add remediation to `generate_remediation()` in `security_auditor.py`
5. Document in `memories/security_patterns.md`
