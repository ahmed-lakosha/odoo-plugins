# Odoo Upgrade Plugin Usage Guide

## Available Tools

### 1. Pre-Check Tool (NEW)
**Purpose**: Scan your project for Odoo 19 compatibility issues BEFORE upgrading

```bash
python C:\tmp\plugins\odoo-upgrade-plugin\odoo-upgrade\scripts\odoo19_precheck.py <project_path>
```

**Example**:
```bash
python odoo19_precheck.py C:\odoo\odoo17\projects\my_project
```

**Output**:
- Lists all compatibility issues by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Shows exact file locations and issue descriptions
- Provides recommendations for fixing

### 2. Quick Fix Tool (NEW)
**Purpose**: Apply targeted fixes for the most common Odoo 19 issues

```bash
python C:\tmp\plugins\odoo-upgrade-plugin\odoo-upgrade\scripts\quick_fix_odoo19.py <project_path>
```

**What it fixes**:
- ✅ Tree to List view conversion
- ✅ Search view group tag removal
- ✅ Act_window view_mode references
- ✅ js_class="crm_kanban" removal
- ✅ Cron numbercall field removal
- ✅ Kanban template name changes
- ✅ RPC service migration

### 3. Full Upgrade Script
**Purpose**: Complete upgrade with backup, all fixes, and report generation

```bash
python C:\tmp\plugins\odoo-upgrade-plugin\odoo-upgrade\scripts\upgrade_to_odoo19.py <project_path>
```

**Features**:
- Creates automatic backup
- Applies ALL compatibility fixes
- Updates manifest versions
- Generates detailed report

## Recommended Workflow

### Step 1: Pre-Check
Always start with a pre-check to understand what needs fixing:
```bash
python odoo19_precheck.py C:\odoo\odoo17\projects\my_project
```

### Step 2: Quick Fix or Full Upgrade

**Option A: Quick Fix (Faster)**
If you only have common issues:
```bash
python quick_fix_odoo19.py C:\odoo\odoo17\projects\my_project
```

**Option B: Full Upgrade (Comprehensive)**
For complete migration with backup:
```bash
python upgrade_to_odoo19.py C:\odoo\odoo17\projects\my_project
```

### Step 3: Test Installation
```bash
# Create test database
python -m odoo -d test_db_19 -i base --stop-after-init

# Install your module
python -m odoo -d test_db_19 -i your_module --stop-after-init
```

### Step 4: Verify
Run pre-check again to confirm all issues are resolved:
```bash
python odoo19_precheck.py C:\odoo\odoo19\projects\my_project
```

## Common Issues and Solutions

### Issue: "Invalid view type: 'tree'"
**Solution**: Run quick fix or use this command:
```bash
python quick_fix_odoo19.py <project>
# Automatically converts all <tree> to <list>
```

### Issue: "Cannot find key 'crm_kanban' in registry"
**Solution**: The quick fix removes this automatically, or manually:
- Remove `js_class="crm_kanban"` from kanban views

### Issue: "View types not defined tree found in act_window"
**Solution**: Fixed automatically by quick fix, changes:
- `view_mode="tree,form"` → `view_mode="list,form"`

### Issue: "Invalid view definition" (search views)
**Solution**: Quick fix removes group tags from search views

### Issue: "Service rpc is not available"
**Solution**: Quick fix adds _jsonRpc helper method automatically

## Batch Processing

### Process Multiple Projects
Create a batch script:
```bash
#!/bin/bash
projects=("project1" "project2" "project3")

for project in "${projects[@]}"; do
    echo "Upgrading $project..."
    python upgrade_to_odoo19.py "/path/to/$project"
done
```

### Windows Batch:
```batch
@echo off
for %%p in (project1 project2 project3) do (
    echo Upgrading %%p...
    python upgrade_to_odoo19.py "C:\odoo\odoo17\projects\%%p"
)
```

## Troubleshooting

### Unicode Errors in Windows Console
Set console to UTF-8:
```batch
chcp 65001
```

### Permission Errors
Run as administrator or ensure write permissions on project directories

### Module Not Found Errors
Ensure all Python dependencies are installed:
```bash
pip install lxml psycopg2 babel
```

## Advanced Options

### Custom Fix Patterns
Edit `scripts/upgrade_to_odoo19.py` to add custom patterns:
```python
# Add custom XML fix
content = re.sub(r'your_pattern', r'replacement', content)
```

### Exclude Files
Modify scripts to skip certain files:
```python
if 'skip_this' in str(file_path):
    continue
```

## Support

For issues or questions:
1. Run pre-check first to identify issues
2. Try quick fix for common problems
3. Use full upgrade for comprehensive migration
4. Check generated reports for detailed information

## Version Compatibility

| From Version | To Version | Support Status |
|--------------|------------|----------------|
| Odoo 17      | Odoo 19    | ✅ Full Support |
| Odoo 18      | Odoo 19    | ✅ Full Support |
| Odoo 16      | Odoo 19    | ⚠️ Partial (may need manual fixes) |
| Odoo 14-15   | Odoo 19    | ⚠️ Limited (significant changes) |