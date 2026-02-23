# Claude Code Plugin Development - Complete Knowledge Base

## Table of Contents
1. [Overview](#overview)
2. [Plugin Architecture](#plugin-architecture)
3. [Plugin Types](#plugin-types)
4. [Required Components](#required-components)
5. [Commands - Custom Slash Commands](#commands---custom-slash-commands)
6. [Agents - Specialized AI Subagents](#agents---specialized-ai-subagents)
7. [Skills - Agent Capabilities](#skills---agent-capabilities)
8. [Hooks - Event-Driven Automation](#hooks---event-driven-automation)
9. [MCP Servers - Model Context Protocol](#mcp-servers---model-context-protocol)
10. [Practical Templates](#practical-templates)
11. [Validation Requirements](#validation-requirements)
12. [Development Workflow](#development-workflow)
13. [Best Practices](#best-practices)
14. [Publishing to Marketplace](#publishing-to-marketplace)
15. [Real-World Case Study: odoo-report-plugin](#real-world-case-study-odoo-report-plugin)
16. [SKILL.md Best Practices](#skillmd-best-practices)
17. [Version Management](#version-management)
18. [Plugin Development Workflow (Enhanced)](#plugin-development-workflow-enhanced)

## Overview

Claude Code plugins extend the functionality of Claude Code CLI through a modular marketplace system. Plugins can provide custom commands, specialized AI agents, automation hooks, and integrate with external tools via MCP (Model Context Protocol).

### Key Concepts
- **Marketplace**: Central repository containing multiple plugins
- **Plugin**: Self-contained unit providing specific functionality
- **Discovery**: Plugins are discovered via `.claude-plugin/plugin.json` manifests
- **Installation**: Users install plugins individually based on needs
- **Granular Control**: No bloat - install only what you need

## Plugin Architecture

### Hierarchy
```
claude-code-marketplace/
├── README.md                    # Marketplace documentation
├── PLUGIN_SCHEMA.md            # Plugin requirements
├── plugins/                    # All plugins directory
│   └── [plugin-name]/         # Individual plugin
│       ├── .claude-plugin/    # Required metadata
│       │   └── plugin.json    # Plugin manifest
│       ├── commands/          # Optional slash commands
│       ├── agents/            # Optional AI agents
│       ├── skills/            # Optional agent skills
│       ├── hooks/             # Optional automation
│       ├── scripts/           # Optional utilities
│       ├── .mcp.json          # Optional MCP config
│       └── README.md          # Plugin docs
└── scripts/                    # Validation scripts
```

### Plugin Naming Conventions
- Use **kebab-case** for plugin names (e.g., `code-review`, `api-tester`)
- Be descriptive but concise
- Avoid generic names - be specific about functionality
- Examples: `accessibility-expert`, `ultrathink`, `lyra`

## Plugin Types

Claude Code supports five main plugin types:

### 1. Commands
Custom slash commands for quick actions and workflows
- Example: `/lyra` for prompt optimization
- Example: `/ultrathink` for complex task orchestration

### 2. Agents
Specialized AI subagents with domain expertise
- Example: `accessibility-expert` for WCAG compliance
- Example: `frontend-developer` for UI development

### 3. Skills
Agent capabilities that extend functionality
- Loaded with specific agent contexts
- Can include scripts and resources

### 4. Hooks
Event-driven automation triggered by tool usage
- Example: Auto-update CLAUDE.md after major changes
- Example: Run tests after code modifications

### 5. MCP Servers
External tool integrations via Model Context Protocol
- Database connections
- API integrations
- Custom tool providers

## Required Components

### Manifest File: `.claude-plugin/plugin.json`

Every plugin MUST have this file with valid JSON:

#### Required Fields
```json
{
  "name": "plugin-name",           // Unique identifier (kebab-case)
  "version": "1.0.0",              // Semantic version
  "description": "Brief description of plugin functionality"
}
```

#### Complete Example with Optional Fields
```json
{
  "name": "enterprise-plugin",
  "version": "1.2.0",
  "description": "Enterprise-grade development plugin",
  "author": {
    "name": "Jane Developer",     // Required in author object
    "email": "jane@example.com",  // Optional
    "url": "https://github.com/janedev"  // Optional
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/janedev/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "security", "compliance"],
  "commands": "./commands/",       // Or ["./cmd1.md", "./cmd2.md"]
  "agents": "./agents/",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

## Commands - Custom Slash Commands

Commands add custom slash commands to Claude Code for quick actions and workflows.

### Command Structure
Location: `commands/[command-name].md`

### Command Definition Format
```markdown
---
description: Brief description of the command
author: Your Name
author-url: https://github.com/yourname
version: 1.0.0
---

# Command Instructions

You are implementing the /command-name command. Your role is...

## Functionality
- What the command does
- Expected inputs
- Expected outputs

## Usage Examples
- Example 1: Simple usage
- Example 2: Complex usage

## Implementation Details
[Detailed instructions for Claude Code to execute the command]
```

### Real Example: Lyra Command
```markdown
---
description: Lyra - a master-level AI prompt optimization specialist.
author: Anand Tyagi
author-url: https://github.com/ananddtyagi
version: 1.0.0
---

You are Lyra, a master-level AI prompt optimization specialist...

## THE 4-D METHODOLOGY
### 1. DECONSTRUCT
- Extract core intent, key entities, and context
...
```

### Command Best Practices
1. **Clear Welcome Message**: Display instructions when activated
2. **Input Validation**: Check parameters before execution
3. **Progressive Disclosure**: Offer BASIC and DETAIL modes
4. **Memory Management**: Note if data should not be saved
5. **Error Handling**: Graceful failures with helpful messages

## Agents - Specialized AI Subagents

Agents are specialized AI personalities with domain expertise and specific tool access.

### Agent Structure
Location: `agents/[agent-name].md`

### Agent Definition Format
```markdown
---
name: agent-name
description: Agent capabilities and use cases
Examples:

<example>
Context: Specific scenario
user: "User request"
assistant: "Agent response demonstrating expertise"
<commentary>
Why this approach matters
</commentary>
</example>

color: purple              # Visual identifier in UI
tools: Read, Write, Bash   # Allowed tools for this agent
---

# Agent Instructions

You are a [Role] specializing in [Domain]. Your expertise spans...

## Primary Responsibilities
1. **Responsibility 1** - Detailed description
2. **Responsibility 2** - Detailed description

## Domain Expertise
- **Area 1**: Deep knowledge description
- **Area 2**: Implementation strategies

## Implementation Approach
- How you prioritize tasks
- How you handle complex scenarios
- Performance considerations

## Success Metrics
- Measurable outcomes
- Quality indicators
```

### Real Example: Accessibility Expert
```markdown
---
name: accessibility-expert
description: WCAG compliance and accessibility implementation
Examples:
<example>
Context: B2B SaaS platform needs WCAG 2.1 AA compliance
user: "Our dashboard fails accessibility audits"
assistant: "I'll conduct a comprehensive accessibility audit..."
</example>
color: purple
tools: Read, Write, MultiEdit, Bash, Grep, Glob
---

You are an Accessibility Expert specializing in enterprise B2B applications...
```

### Agent Tool Permissions
Agents can be granted specific tools:
- **Read**: Read files
- **Write**: Create/overwrite files
- **Edit/MultiEdit**: Modify existing files
- **Bash**: Execute shell commands
- **Grep/Glob**: Search operations
- **WebSearch/WebFetch**: Internet access
- **TodoWrite**: Task management

## Skills - Agent Capabilities

Skills extend agent functionality with additional capabilities.

### Skill Structure
```
skills/
└── skill-name/
    ├── SKILL.md           # Skill definition
    └── scripts/           # Optional utilities
        └── helper.py
```

### SKILL.md Format
```markdown
---
name: skill-name
description: What this skill enables
version: 1.0.0
allowed-tools:
  - Read
  - Write
  - Bash
---

# Skill Implementation

This skill enables...

## Capabilities
1. Feature 1
2. Feature 2

## Workflows
### Workflow 1: Name
1. Step 1
2. Step 2

## Helper Scripts
- `scripts/helper.py`: Description of utility
```

## Hooks - Event-Driven Automation

Hooks enable automated actions triggered by Claude Code events.

### Hook Configuration
Location: `hooks/hooks.json`

### Hook Structure
```json
{
  "PostToolUse": [
    {
      "name": "Hook name",
      "matcher": "regex pattern",
      "description": "What this hook does",
      "hooks": [
        {
          "type": "command",
          "command": "/command-to-run"
        }
      ]
    }
  ]
}
```

### Real Example: Auto-Update CLAUDE.md
```json
{
  "PostToolUse": [
    {
      "name": "Update CLAUDE.md after major changes",
      "matcher": "(Write|Edit|Delete|Refactor).*[5-9]\\d+|[1-9]\\d{2,}",
      "description": "Automatically prompts to update CLAUDE.md when significant code changes are detected",
      "hooks": [
        {
          "type": "command",
          "command": "/update-claude"
        }
      ]
    }
  ]
}
```

### Hook Event Types
- **PostToolUse**: After any tool execution
- **PreCommit**: Before git commits
- **PostCommit**: After git commits
- **OnError**: When errors occur

## MCP Servers - Model Context Protocol

MCP servers enable integration with external tools and services.

### MCP Configuration
Location: `.mcp.json`

### MCP Structure
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### MCP Use Cases
- Database connections
- API integrations
- File system operations
- Browser automation
- Custom tool providers

## Practical Templates

### Minimal Plugin Template
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "A simple plugin for Claude Code"
}
```

### Command Plugin Template
```
my-command/
├── .claude-plugin/
│   └── plugin.json
└── commands/
    └── my-command.md
```

**plugin.json:**
```json
{
  "name": "my-command",
  "version": "1.0.0",
  "description": "Custom command for X",
  "commands": "./commands/"
}
```

**commands/my-command.md:**
```markdown
---
description: What this command does
author: Your Name
version: 1.0.0
---

You are implementing /my-command...
```

### Agent Plugin Template
```
my-agent/
├── .claude-plugin/
│   └── plugin.json
└── agents/
    └── my-agent.md
```

**plugin.json:**
```json
{
  "name": "my-agent",
  "version": "1.0.0",
  "description": "Specialized agent for Y",
  "agents": "./agents/"
}
```

**agents/my-agent.md:**
```markdown
---
name: my-agent
description: Agent capabilities
color: blue
tools: Read, Write, Bash
---

You are a specialized agent...
```

### Full-Featured Plugin Template
```
enterprise-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── command1.md
│   └── command2.md
├── agents/
│   └── specialist.md
├── skills/
│   └── advanced-skill/
│       └── SKILL.md
├── hooks/
│   └── hooks.json
├── scripts/
│   └── utility.py
├── .mcp.json
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## Validation Requirements

### Required Validation Checks
1. **Manifest exists**: `.claude-plugin/plugin.json` must exist
2. **Valid JSON**: All JSON files must parse correctly
3. **Required fields**: name, version, description in manifest
4. **Semantic version**: Version must follow X.Y.Z format
5. **Author format**: If present, must have "name" field

### Validation Script
Run validation locally:
```bash
python scripts/validate-plugin-schema.py
```

### Common Validation Errors

#### Missing Manifest
```
Error: Missing required file: .claude-plugin/plugin.json
Solution: Create the directory and manifest file
```

#### Invalid JSON
```
Error: Invalid JSON in plugin.json: Expecting ',' delimiter
Solution: Fix JSON syntax (remove trailing commas, add quotes)
```

#### Missing Required Fields
```
Error: plugin.json missing required fields: name, version
Solution: Add all required fields to manifest
```

## Development Workflow

### 1. Planning Phase
- Identify the problem your plugin solves
- Determine plugin type (command, agent, etc.)
- Design user interaction flow

### 2. Scaffolding
```bash
# Create plugin directory
mkdir -p plugins/my-plugin/.claude-plugin

# Create manifest
cat > plugins/my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Description here"
}
EOF

# Add components as needed
mkdir plugins/my-plugin/commands
mkdir plugins/my-plugin/agents
```

### 3. Implementation
- Write command/agent definitions
- Add any helper scripts
- Configure hooks if needed

### 4. Testing
```bash
# Validate schema
python scripts/validate-plugin-schema.py

# Test in Claude Code
/plugin install my-plugin@local

# Use your command/agent
/my-command
```

### 5. Documentation
- Create README.md with usage examples
- Add CHANGELOG.md for version history
- Include LICENSE file

### 6. Publishing
- Push to GitHub repository
- Submit to marketplace
- Tag releases with semantic versions

## Best Practices

### General Guidelines
1. **Single Responsibility**: Each plugin should do one thing well
2. **Clear Naming**: Use descriptive, specific names
3. **Comprehensive Docs**: Include examples and edge cases
4. **Error Handling**: Graceful failures with helpful messages
5. **Performance**: Consider impact on Claude Code performance

### Command Best Practices
- **Welcome Messages**: Clear instructions on first use
- **Parameter Validation**: Check inputs before processing
- **Progressive Enhancement**: Basic and advanced modes
- **Memory Management**: Be explicit about data persistence

### Agent Best Practices
- **Clear Role Definition**: Specific expertise areas
- **Tool Restrictions**: Only request needed tools
- **Examples in Frontmatter**: Show real use cases
- **Success Metrics**: Define measurable outcomes
- **Domain Language**: Use industry-specific terminology

### Marketplace Best Practices
- **Unique Value**: Differentiate from existing plugins
- **Active Maintenance**: Regular updates and bug fixes
- **Community Engagement**: Respond to issues and feedback
- **Semantic Versioning**: Follow major.minor.patch convention
- **Backwards Compatibility**: Avoid breaking changes

### Security Considerations
- **Minimal Permissions**: Request only necessary tools
- **Input Sanitization**: Validate and clean user inputs
- **No Secrets**: Never hardcode API keys or passwords
- **Secure Scripts**: Review all executable code
- **User Consent**: Be transparent about actions

## Publishing to Marketplace

### Prerequisites
1. Valid plugin following schema
2. GitHub repository
3. Comprehensive documentation
4. Tested functionality

### Submission Process
1. **Prepare Repository**
   - Ensure all files follow schema
   - Add comprehensive README
   - Include LICENSE file
   - Tag stable release

2. **Submit to Directory**
   - Visit claudecodecommands.directory/submit
   - Provide plugin information
   - Link GitHub repository
   - Describe functionality

3. **Marketplace Sync**
   - Automated sync from database
   - Updates every few hours
   - Maintains version history

### Post-Publication
1. **Monitor Issues**: Watch for user feedback
2. **Regular Updates**: Fix bugs, add features
3. **Version Management**: Use semantic versioning
4. **Community Support**: Help users with questions

## Advanced Patterns

### Multi-Mode Commands
Commands can offer different interaction modes:
```markdown
## OPERATING MODES

**DETAIL MODE:**
- Comprehensive analysis
- Multiple interactions
- Step-by-step guidance

**BASIC MODE:**
- Quick execution
- Minimal interaction
- Direct results
```

### Agent Orchestration
Complex plugins can coordinate multiple agents:
```markdown
You coordinate with:
1. **Architect Agent**: Design decisions
2. **Research Agent**: Information gathering
3. **Coder Agent**: Implementation
4. **Tester Agent**: Validation
```

### Conditional Hooks
Hooks can use regex patterns for selective triggering:
```json
{
  "matcher": "(Write|Edit).*\\.(py|js|ts)$",
  "description": "Trigger only for code file modifications"
}
```

### Skill Composition
Skills can build on each other:
```markdown
dependencies:
  - base-skill
  - advanced-skill
```

## Troubleshooting

### Plugin Not Found
- Check manifest exists at `.claude-plugin/plugin.json`
- Validate JSON syntax
- Ensure plugin name matches directory

### Command Not Working
- Verify command file in correct location
- Check frontmatter format
- Validate markdown syntax

### Agent Not Responding
- Check tools permissions
- Verify agent file location
- Review examples in frontmatter

### Hook Not Triggering
- Test regex pattern
- Check hook event type
- Verify command exists

## Resources

### Official Documentation
- Marketplace: https://claudecodecommands.directory
- Submit Plugin: https://claudecodecommands.directory/submit
- GitHub: https://github.com/ananddtyagi/claude-code-marketplace

### Validation Tools
- Schema Validator: `scripts/validate-plugin-schema.py`
- Marketplace Sync: `scripts/validate-marketplace-sync.py`

### Example Plugins to Study
- **lyra**: Simple command with complex logic
- **ultrathink**: Multi-agent orchestration
- **accessibility-expert**: Domain-specific agent
- **experienced-engineer**: Full-featured with hooks
- **code-review**: Practical utility command
- **odoo-report**: Domain-specific skill with issue prevention patterns
- **odoo-frontend**: Comprehensive skill with version tracking

---

## Real-World Case Study: odoo-report-plugin

This section documents lessons learned from developing the odoo-report-plugin, demonstrating best practices for skill-based plugins.

### The Problem

Initial v1.0.0 of the plugin had comprehensive email/QWeb patterns but users encountered recurring issues:

| Issue | Time Lost | Root Cause |
|-------|-----------|------------|
| Arabic text corruption | 2+ hours | Missing UTF-8 wrapper documentation |
| wkhtmltopdf not found | 30 min | No setup guide |
| Google Fonts failing | 1 hour | Offline mode not explained |
| CSS not parsing | 1 hour | SCSS pitfall undocumented |

**Total preventable debugging time: 5+ hours per user**

### The Solution: Issue-Driven Enhancement

v2.0.0 was developed by:

1. **Analyzing real failures** from sadad_invoice_report development
2. **Documenting the working solution** (not just theory)
3. **Adding validation checklists** to prevent issues
4. **Including complete working examples** based on proven code

### Key Lessons Learned

#### 1. Document Infrastructure Requirements

Don't assume users know prerequisites:

```markdown
## wkhtmltopdf Setup (MANDATORY)

### Installation
\`\`\`bash
# Windows
winget install wkhtmltopdf.wkhtmltox

# Linux
sudo apt-get install wkhtmltopdf
\`\`\`

### Odoo Configuration
Add to `odoo.conf`:
\`\`\`ini
bin_path = C:\Program Files\wkhtmltopdf\bin
\`\`\`
```

#### 2. Show Wrong Patterns, Not Just Right Ones

Users learn from seeing what NOT to do:

```markdown
### ❌ WRONG (Will Cause Encoding Issues)
\`\`\`xml
<template id="report">
    <html>
        <body>فاتورة</body>  <!-- Displays as ÙØ§ØªÙˆØ±Ø© -->
    </html>
</template>
\`\`\`

### ✅ CORRECT
\`\`\`xml
<template id="report">
    <t t-call="web.html_container">  <!-- UTF-8 meta tag -->
        <t t-call="web.external_layout">  <!-- Fonts -->
            <div class="page">فاتورة</div>
        </t>
    </t>
</template>
\`\`\`
```

#### 3. Include Validation Checklists

Pre-flight checks prevent issues:

```markdown
## Validation Checklist

### Infrastructure
□ wkhtmltopdf installed
□ bin_path configured
□ Server restarted

### Template Structure
□ web.html_container wrapper
□ web.external_layout
□ Content in div.page
```

#### 4. Provide Complete Working Examples

Don't just show snippets - include full, tested templates:

```markdown
## Bilingual Invoice Template (Complete Example)

Based on proven sadad_invoice implementation:

\`\`\`xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Paper Format -->
    <record id="paperformat_invoice" model="report.paperformat">
        ...
    </record>

    <!-- Report Action -->
    <record id="action_report" model="ir.actions.report">
        ...
    </record>

    <!-- Template with proven UTF-8 support -->
    <template id="report_document">
        ...
    </template>
</odoo>
\`\`\`
```

#### 5. Track Issues Prevented

Quantify the value of documentation:

```markdown
## Changelog

### v2.0.0

**ISSUES PREVENTED:**

| Issue | Time Saved |
|-------|------------|
| Arabic encoding | 2+ hours |
| wkhtmltopdf setup | 30 min |
| Font loading | 1 hour |
```

### Plugin Evolution Pattern

```
v1.0.0 (Initial)
├── Core patterns documented
├── Basic examples
└── Commands defined

v2.0.0 (Issue-Driven)
├── Infrastructure setup guides
├── Wrong vs Right patterns
├── Complete working examples
├── Validation checklists
├── Debug workflows
└── Changelog with issues prevented
```

---

## SKILL.md Best Practices

### Frontmatter Structure

```yaml
---
name: skill-name
description: "Comprehensive description with key features"
version: "2.0.0"
author: "Your Name/Company"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  mode: "codebase"
  supported-versions: ["14", "15", "16", "17", "18", "19"]
  primary-version: "17"
  categories:
    - category1
    - category2
---
```

### Section Organization

Recommended order for comprehensive skills:

1. **Quick Reference** - Architecture diagrams, key concepts
2. **Configuration** - Setup requirements, prerequisites
3. **Core Patterns** - Main functionality patterns
4. **Version Differences** - Version-specific syntax
5. **Commands Reference** - Available slash commands
6. **Validation Rules** - Pre-flight checks
7. **Error Recovery** - Common errors and solutions
8. **Debug Workflow** - Systematic diagnosis steps
9. **Complete Examples** - Full working code
10. **Changelog** - Version history with issues prevented

### Visual Documentation

Use ASCII diagrams for architecture:

```
┌─────────────────────────────────────────┐
│           ARCHITECTURE DIAGRAM           │
├─────────────────────────────────────────┤
│  Component A                             │
│  ├── Sub-component 1                     │
│  └── Sub-component 2                     │
└─────────────────────────────────────────┘
```

Use tables for decision matrices:

```markdown
| Feature | v14 | v15 | v16 | v17 | v18 |
|---------|:---:|:---:|:---:|:---:|:---:|
| Feature A | ❌ | ✅ | ✅ | ✅ | ✅ |
| Feature B | ✅ | ✅ | ❌ | ❌ | ✅ |
```

### Emoji Usage Guidelines

Use sparingly for critical warnings:
- ⚠️ CRITICAL warnings
- ❌ Wrong patterns
- ✅ Correct patterns
- 📚 Documentation references

Avoid overuse - keep professional tone.

---

## Version Management

### Semantic Versioning for Plugins

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes or major new sections
MINOR: New features, backward compatible
PATCH: Bug fixes, typo corrections
```

### When to Bump Versions

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| New major section | MAJOR | v1.0 → v2.0 |
| New command/pattern | MINOR | v2.0 → v2.1 |
| Fix typo/error | PATCH | v2.1 → v2.1.1 |
| Add example | MINOR | v2.1 → v2.2 |
| Restructure existing | MINOR | v2.2 → v2.3 |

### Changelog Best Practices

```markdown
## Changelog

### v2.0.0 - Major Enhancement (Date)

**NEW SECTIONS:**
- Section 1: Description
- Section 2: Description

**ISSUES PREVENTED:**
| Issue | Time Saved |
|-------|------------|
| Issue 1 | X hours |

### v1.0.0 - Initial Release

- Feature 1
- Feature 2
```

---

## Plugin Development Workflow (Enhanced)

### Phase 1: Research & Planning

1. **Identify User Pain Points**
   - What issues do users encounter?
   - How much time is wasted?
   - What's the root cause?

2. **Study Existing Solutions**
   - Analyze working implementations
   - Document what works vs what fails
   - Note version-specific differences

3. **Plan Documentation Structure**
   - List all sections needed
   - Prioritize by user impact
   - Include validation checklists

### Phase 2: Implementation

1. **Create Plugin Scaffold**
   ```bash
   mkdir -p plugin-name/.claude-plugin
   mkdir -p plugin-name/skill-name
   mkdir -p plugin-name/commands
   ```

2. **Write SKILL.md**
   - Start with working examples
   - Add wrong patterns to avoid
   - Include infrastructure setup
   - Add validation checklists

3. **Create Commands**
   - One file per command
   - Clear usage instructions
   - Error handling guidance

### Phase 3: Validation & Testing

1. **Test with Real Projects**
   - Use actual user scenarios
   - Document any issues found
   - Update skill based on findings

2. **Validate Plugin Schema**
   ```bash
   python scripts/validate-plugin-schema.py
   ```

3. **Review Documentation**
   - Check all code examples work
   - Verify links are valid
   - Ensure version consistency

### Phase 4: Release & Iterate

1. **Tag Release**
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

2. **Monitor User Feedback**
   - Track issues reported
   - Note common questions
   - Plan next iteration

3. **Iterate Based on Usage**
   - Add sections for new issues
   - Update examples as needed
   - Maintain changelog

## Summary

Creating Claude Code plugins involves:
1. Understanding the plugin architecture and types
2. Creating proper manifest and structure
3. Implementing commands, agents, or hooks
4. Following validation requirements
5. Testing thoroughly
6. Publishing to marketplace

Key success factors:
- Clear value proposition
- Excellent documentation
- Active maintenance
- Community engagement
- Following best practices

This guide provides everything needed to create powerful, useful plugins that extend Claude Code's capabilities and help developers be more productive.