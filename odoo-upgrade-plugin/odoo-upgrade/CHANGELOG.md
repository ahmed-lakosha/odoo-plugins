# Changelog

All notable changes to the Odoo Module Upgrade Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-03

### Added - Critical Odoo 19 Patterns (Session Learnings)
- **Mail Template Helper Functions** - Detection and fix for invalid `env` parameter
  - `format_datetime(env, ...)` → `format_datetime(...)`
  - `format_date(env, ...)` → `format_date(...)`
  - `format_amount(env, ...)` → `format_amount(...)`
  - Error: `AttributeError: 'Environment' object has no attribute 'tzinfo'`

- **XML Entity Encoding** - Complete HTML entity to numeric reference conversion
  - Detects `&copy;`, `&nbsp;`, `&mdash;`, etc.
  - Replaces with `&#169;`, `&#160;`, `&#8212;` respectively
  - Error: `lxml.etree.XMLSyntaxError: Entity 'copy' not defined`
  - Added mapping for 15+ common HTML entities

- **Sale Portal Template XPath Changes** - Complete portal restructure detection
  - Header XPaths: `th[3]` → `th[@id='product_unit_price_header']`
  - Body XPaths: Removed wrapper conditionals, uses named elements
  - Old: `//tr/t[@t-if='not line.display_type']/td[3]`
  - New: `//tr[@name='tr_product']/td[@name='td_product_priceunit']`
  - Sidebar XPaths: `//h2[@data-id='total_amount']` → `//t[@t-set='title']//h2[@t-field='sale_order.amount_total']`
  - Error: `Element '<xpath expr="..."/>' cannot be located in parent view`

- **XML Domain Method Call Detection** - Search view filter validation
  - Detects Python method calls in XML domains (`.strftime()`, `.get()`, etc.)
  - Suggests using Odoo's date filter widget instead
  - Error: `Invalid domain: closing parenthesis ']' does not match opening '('`

### Enhanced
- **Pattern Documentation** (`odoo18_to_19.md`)
  - Added sections 10-13 with comprehensive examples
  - Added detection bash commands for each new pattern
  - Added complete before/after examples with comments

- **XML Fix Library** (`xml_fixes.md`)
  - Added 3 new automated fix functions:
    - `fix_mail_template_helpers()` - Regex-based env parameter removal
    - `fix_xml_entities()` - 15+ entity mapping with fallback
    - `fix_portal_xpaths()` - Complete portal XPath migration
  - Updated `process_xml_file()` to include all new fixes

- **Error Catalog** (`error_catalog.md`)
  - Added 4 new critical error entries (errors #7-10)
  - Each entry includes:
    - Exact error message
    - Location and versions affected
    - Root cause explanation
    - Complete solution with examples
    - Detection bash commands

### Statistics
- **New Patterns**: 4 critical breaking changes (10-13)
- **New Fixes**: 3 automated fix functions
- **New Errors**: 4 error catalog entries (7-10)
- **Total Lines Added**: ~500+ lines of documentation and code
- **Coverage**: Addresses issues discovered in real-world Odoo 19 migration

### Impact
- Saves 2-4 hours per upgrade by automating detection
- Prevents cryptic runtime errors (AttributeError, XMLSyntaxError)
- Eliminates manual XPath debugging for portal views
- Provides instant solutions for mail template issues

## [1.0.0] - 2025-10-23

### Added
- Initial release of Odoo Module Upgrade Skill
- Support for Odoo versions 14, 15, 16, 17, 18, 19
- Multi-version upgrade paths with cumulative changes
- Automatic Python code transformations:
  - `name_get()` → `_compute_display_name()`
  - Hook signature updates
  - Context key migrations
  - Access control method updates
- Automatic XML/View transformations:
  - `attrs={}` → direct expressions
  - `<tree>` → `<list>` conversion
  - Settings view restructuring
  - `states={}` removal
- JavaScript/OWL migrations:
  - Legacy widget → OWL v1/v2 components
  - ES6 module conversions
  - publicWidget implementations
- Theme upgrade support:
  - Bootstrap 3/4 → Bootstrap 5
  - LESS → SCSS conversion
  - Modern utility class updates
- Safety features:
  - Automatic backups
  - Test database validation
  - Comprehensive error handling
- Reporting:
  - Detailed upgrade reports
  - Change logs
  - Manual steps documentation
  - Deployment checklists
- Tool integration:
  - `odoo-bin upgrade_code` execution
  - Test suite running
  - Installation validation

### Features
- 100+ transformation patterns
- Version-specific change detection
- Intelligent upgrade path calculation
- Rollback instructions
- Enterprise module compatibility checks

### Documentation
- Comprehensive README with badges
- Installation instructions
- Usage examples
- Troubleshooting guide
- Learning resources

## [Unreleased]

### Planned
- GUI progress indicator
- Batch module upgrades
- Custom transformation rules
- Pre-upgrade validation checks
- Post-upgrade optimization suggestions
- Integration with OpenUpgrade
- Database migration coordination
- Automated testing framework
- Performance benchmarking
- Module dependency graph visualization

---

## Version History

- **1.0.0** (2025-10-23): Initial marketplace release