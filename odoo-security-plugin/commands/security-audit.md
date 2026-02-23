---
title: 'Security Audit'
read_only: true
type: 'command'
description: 'Run a targeted security audit on a named Odoo module, with severity filtering and actionable fix suggestions.'
---

# /security-audit <module-path-or-name>

Run a comprehensive security audit on a specific Odoo module. Unlike `/odoo-security` which accepts any path, this command is optimized for named modules within the current project's structure and provides richer contextual analysis.

## Usage

```
/security-audit my_module_name
/security-audit /absolute/path/to/my_module
/security-audit my_module --severity HIGH
/security-audit my_module --fix
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `module-path-or-name` | Yes | Module name (searched in current project) or absolute path |

## Options

| Option | Description |
|--------|-------------|
| `--severity <level>` | Filter to CRITICAL, HIGH, MEDIUM, or LOW (default: LOW) |
| `--fix` | Automatically apply safe remediations after review |
| `--report` | Generate a detailed markdown report file |
| `--compare <commit>` | Compare security posture against a git commit |

## What This Command Does

### Step 1: Module Discovery
Locates the module in the Odoo projects directory and validates it's a proper Odoo module (`__manifest__.py` present).

### Step 2: Static Analysis
Runs all three sub-auditors:
- `access_checker.py` — Model access rule completeness
- `route_auditor.py` — HTTP route authentication safety
- `sudo_finder.py` — sudo() usage risk classification

### Step 3: AI-Enhanced Analysis
The AI assistant performs additional analysis:
- Cross-references model relationships to find indirect access paths
- Checks for inherited models that may have missed access rules
- Reviews XML view `groups=` attributes for field-level security
- Analyzes record rule domains for logical completeness
- Identifies sensitive field names without `groups=` restriction

### Step 4: Remediation Generation
For each issue found, generates:
- Specific fix code (CSV entries, XML rules, Python changes)
- Explanation of why the change is needed
- Risk of leaving the issue unfixed

### Step 5: Report Output
Presents a prioritized list of issues with all remediations, ready to apply.

## Example Workflow

```bash
# Audit a module, see all issues
/security-audit my_module

# Focus on critical issues only
/security-audit my_module --severity CRITICAL

# Audit and apply safe fixes automatically
/security-audit my_module --fix

# Generate a full report for code review
/security-audit my_module --report
# → Creates: my_module_security_report_2026-02-23.md
```

## Automated Fix Capabilities

When `--fix` is used, the AI can automatically:

1. **Create missing `ir.model.access.csv`** — generates complete CSV with all model rules
2. **Fix empty group references** — adds appropriate groups to access rules
3. **Add groups= to sensitive fields** — adds field-level restrictions to salary, password, token, etc.
4. **Create multi-company record rules** — generates the standard domain filter XML
5. **Fix parameterized queries** — rewrites unsafe `env.cr.execute()` calls

Actions requiring manual review (never auto-applied):
- Changing `auth='public'` to `auth='user'` (may break functionality)
- Removing `sudo()` from controllers (requires understanding business logic)
- Adding CSRF back to routes (may break integrations)

## Security Audit Checklist Generated

After running this command, you'll receive a checklist like:

```markdown
## Security Audit: my_module — 2026-02-23

### CRITICAL Issues (Fix Immediately)
- [ ] `models/my_model.py:15` — Model 'my.model' has no access rules
  - Fix: Add to security/ir.model.access.csv
  - Code: `access_my_model_user,my.model user,model_my_model,my_module.group_user,1,1,1,0`

### HIGH Issues (Fix This Sprint)
- [ ] `controllers/main.py:45` — sudo() in public route without domain filter
  - Fix: Add domain filter or change auth='user'

### MEDIUM Issues (Fix Next Release)
- [ ] `models/partner_ext.py:23` — Field 'salary' has no groups= restriction
  - Fix: `salary = fields.Float(groups='my_module.group_manager')`
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Security Audit
  run: |
    # This is equivalent to running the scripts directly
    python plugins/odoo-security/scripts/security_auditor.py \
      ./projects/my_project/my_module \
      --min-severity HIGH \
      --exit-on-issues \
      --json \
      --output security-report.json
```
