# Memories Directory

This directory contains decision-making knowledge files that help Claude make intelligent choices when working with Odoo email templates and QWeb reports.

## Files

### version_routing.md

Version-specific decision matrix for:
- Output tag selection (`t-esc` vs `t-out`)
- Report attachment field (`report_template` vs `report_template_ids`)
- Feature availability by version
- Migration transformation rules

### template_patterns.md

Pattern selection guide for:
- Choosing appropriate patterns by use case
- Model-specific template recommendations
- Common template patterns with code examples
- Layout selection guide

### qweb_best_practices.md

Best practices for QWeb template development:
- Safety rules (null checks, escaping)
- Performance guidelines (N+1 queries, caching)
- Common patterns (loops, conditionals, attributes)
- Email-specific guidelines (tables, inline styles)
- Report-specific guidelines (page breaks, Bootstrap)

## Usage

These memory files are automatically loaded by Claude when working with the Odoo Report Plugin. They provide context and guidance for:

1. **Creating Templates**: Pattern selection, syntax choice
2. **Analyzing Templates**: Issue detection, improvement suggestions
3. **Migrating Templates**: Version-specific transformations
4. **Debugging**: Error pattern recognition

## Adding New Memories

To add a new memory file:

1. Create a `.md` file in this directory
2. Start with a purpose statement in a blockquote
3. Structure content with clear headers
4. Include code examples where relevant
5. Reference from SKILL.md if needed
