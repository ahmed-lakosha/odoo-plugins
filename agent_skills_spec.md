# Agent Skills Specification

This document explains how skills are structured in this marketplace, following the Claude Code Agent Skills Spec.

## What is a Skill?

A skill is a folder containing instructions, scripts, and resources that Claude Code can discover and load dynamically to perform specific tasks better. To be recognized as a skill, a folder **must** contain a `SKILL.md` file.

## Minimal Skill Structure

```
my-skill/
├── SKILL.md          # REQUIRED: The skill definition
└── README.md         # OPTIONAL: User documentation
```

More complex skills can include additional directories and files:

```
advanced-skill/
├── SKILL.md          # REQUIRED
├── README.md         # Documentation
├── CHANGELOG.md      # Version history
├── examples/         # Usage examples
│   └── example.md
├── scripts/          # Helper scripts
│   └── helper.py
└── resources/        # Additional resources
    └── data.json
```

## The SKILL.md File

The skill's "entrypoint" is the `SKILL.md` file. It must start with **YAML frontmatter** followed by Markdown content.

### YAML Frontmatter

#### Required Properties

- **`name`**
  - The skill name in hyphen-case
  - Must match the directory name
  - Restricted to lowercase alphanumeric + hyphen
  - Example: `odoo-upgrade`, `module-testing`

- **`description`**
  - Clear description of what the skill does
  - When Claude should use it
  - What problems it solves
  - 1-3 sentences recommended

#### Optional Properties

- **`license`**
  - License applied to the skill
  - Keep it short (e.g., "MIT", "Apache-2.0")
  - Or reference a license file (e.g., "See LICENSE.txt")

- **`allowed-tools`** *(Claude Code specific)*
  - List of tools pre-approved to run
  - Improves skill execution speed
  - Example: `["Read", "Write", "Bash", "Grep"]`

- **`metadata`**
  - Map of custom key-value pairs
  - Store additional properties
  - Use unique key names to avoid conflicts
  - Example: `version`, `category`, `author`

### Example SKILL.md

```markdown
---
name: odoo-upgrade
description: "Automatically upgrade custom Odoo modules across versions with code transformations, testing, and reporting. Use when user requests to upgrade or migrate Odoo modules."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  category: "code-migration"
  framework: "Odoo ERP"
---

# Odoo Module Upgrade Skill

## Skill Overview
This skill upgrades custom Odoo modules...

## Execution Steps

### Step 1: Gather Requirements
Ask the user for...

### Step 2: Validate Inputs
...
```

### Markdown Body

The Markdown body has no restrictions. Include:

- **Overview**: What the skill does
- **Prerequisites**: Requirements to use the skill
- **Instructions**: Step-by-step procedures
- **Examples**: Usage examples
- **Error Handling**: How to handle failures
- **Best Practices**: Domain-specific guidance
- **Troubleshooting**: Common issues and solutions

## Marketplace Structure

A marketplace groups skills into plugins:

```
marketplace-name/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace metadata
├── plugin-group-1/
│   ├── skill-a/
│   │   ├── SKILL.md
│   │   └── README.md
│   └── skill-b/
│       ├── SKILL.md
│       └── README.md
├── plugin-group-2/
│   └── skill-c/
│       ├── SKILL.md
│       └── README.md
├── README.md                  # Marketplace documentation
└── LICENSE                    # License file
```

## marketplace.json Format

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "metadata": {
    "description": "Marketplace description",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "Plugin description",
      "source": "./",
      "strict": false,
      "skills": [
        "./plugin-group/skill-name"
      ]
    }
  ]
}
```

### Fields Explained

- **`name`**: Unique marketplace identifier
- **`owner`**: Marketplace maintainer information
- **`metadata`**: Marketplace-level metadata
- **`plugins`**: Array of plugin definitions
  - **`name`**: Plugin identifier
  - **`description`**: What the plugin does
  - **`source`**: Base path for skills (usually `./`)
  - **`strict`**: Strict mode flag
  - **`skills`**: Array of skill paths relative to repo root

## Installation Methods

### As Marketplace (Recommended)

```bash
cd ~/.claude/plugins/marketplaces
git clone https://github.com/user/marketplace.git marketplace-name
```

Claude Code automatically discovers all skills in the marketplace.

### As Individual Skill

```bash
mkdir -p ~/.claude/skills
cp marketplace-name/plugin/skill/SKILL.md ~/.claude/skills/skill-name.md
```

Useful when you only want specific skills.

## Creating a New Skill

### Step 1: Create Directory Structure

```bash
cd your-marketplace
mkdir -p plugin-name/skill-name
cd plugin-name/skill-name
```

### Step 2: Create SKILL.md

```bash
cat > SKILL.md << 'EOF'
---
name: skill-name
description: "What this skill does and when to use it"
license: MIT
---

# Skill Name

## Overview
...

## Execution Steps

### Step 1: ...
EOF
```

### Step 3: Create README.md (Optional)

```markdown
# Skill Name

User-facing documentation with:
- Installation instructions
- Usage examples
- Requirements
- Troubleshooting
```

### Step 4: Update marketplace.json

Add your skill to the `skills` array:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "skills": [
        "./plugin-name/existing-skill",
        "./plugin-name/skill-name"  // Add this
      ]
    }
  ]
}
```

### Step 5: Test Locally

```bash
# Clone to marketplaces directory
cd ~/.claude/plugins/marketplaces
git clone /path/to/your-marketplace test-marketplace

# Ask Claude: "Show available skills"
# Your skill should appear

# Test it: "Use skill-name to..."
```

### Step 6: Document and Commit

```bash
git add .
git commit -m "Add skill-name skill

- Feature 1
- Feature 2
"
git push
```

## Best Practices

### Skill Design

1. **Single Responsibility**: One skill, one task
2. **Clear Trigger**: Obvious when to use the skill
3. **Error Handling**: Graceful failure recovery
4. **User Feedback**: Keep user informed of progress
5. **Documentation**: Comprehensive usage instructions

### YAML Frontmatter

1. **Match Names**: Directory name = YAML `name` field
2. **Clear Description**: Include when/why to use
3. **List Tools**: Specify `allowed-tools` for performance
4. **Useful Metadata**: Add version, category, etc.

### Markdown Content

1. **Step-by-Step**: Clear execution steps
2. **Examples**: Include usage examples
3. **Prerequisites**: List requirements upfront
4. **Validation**: Explain input validation
5. **Output**: Describe what success looks like

### Testing

1. **Local First**: Test before pushing
2. **Edge Cases**: Handle unusual inputs
3. **Error Paths**: Test failure scenarios
4. **Documentation**: Verify examples work
5. **Cross-Platform**: Test on Windows/Linux/Mac if applicable

## Naming Conventions

### Directories

- Use `hyphen-case` for all directories
- Example: `odoo-upgrade`, `database-migration`

### Files

- `SKILL.md` - Always uppercase, exactly this name
- `README.md` - Uppercase README
- `CHANGELOG.md` - Uppercase CHANGELOG
- Other files: lowercase with hyphens

### YAML Fields

- `name`: hyphen-case
- `description`: sentence case with punctuation
- `metadata` keys: lowercase with hyphens

## Common Pitfalls

### ❌ Wrong

```
odoo_upgrade/           # Underscores not hyphens
  skill.md              # Lowercase 's'
  ---
  name: OdooUpgrade     # CamelCase
  description: upgrades # Missing capital
  ---
```

### ✅ Correct

```
odoo-upgrade/           # Hyphens
  SKILL.md              # Uppercase SKILL
  ---
  name: odoo-upgrade    # hyphen-case, matches directory
  description: "Upgrades Odoo modules..."  # Proper sentence
  license: MIT
  ---
```

## Versioning

### Skill Versions

Track skill versions in metadata:

```yaml
---
name: my-skill
metadata:
  version: "1.2.0"
---
```

Follow [Semantic Versioning](https://semver.org/):
- **Major** (1.x.x): Breaking changes
- **Minor** (x.2.x): New features, backwards compatible
- **Patch** (x.x.3): Bug fixes

### Marketplace Versions

Update marketplace version in `marketplace.json`:

```json
{
  "metadata": {
    "version": "1.0.0"
  }
}
```

## Additional Resources

- [Anthropic Agent Skills Spec](https://github.com/anthropics/anthropic-agent-skills)
- [Claude Code Documentation](https://claude.ai/code)
- [Semantic Versioning](https://semver.org/)
- [Markdown Guide](https://www.markdownguide.org/)
- [YAML Specification](https://yaml.org/spec/)

## Support

For questions or issues with skills in this marketplace:

1. Check the skill's README
2. Look at [examples](./examples/) if available
3. Review this specification
4. [Open an issue](https://github.com/taqat-techno/plugins/issues)

---

**Version**: 1.0.0 | **Last Updated**: 2025-10-23