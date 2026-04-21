# Scripts

Repository utility scripts for maintenance and automation tasks.

## Available Scripts

| Script | Purpose |
|--------|---------|
| [`check_consistency.py`](check_consistency.py) | Audit repo for style and consistency issues |
| [`update_pages.py`](update_pages.py) | Regenerate GitHub Pages files from repo state |
| [`run_all_maintenance.py`](run_all_maintenance.py) | One-command full maintenance runner |
| [`database.py`](database.py) | Labs & certifications tracking database CLI |
| [`validate-links.ps1`](validate-links.ps1) | PowerShell Markdown link validation |

## Quick Start

```bash
# Run everything at once
make maintenance

# Or run individual scripts
python scripts/check_consistency.py          # Report issues
python scripts/check_consistency.py --fix    # Auto-fix safe issues
python scripts/update_pages.py               # Update Pages files
python scripts/database.py --help            # Database CLI help
```

## Makefile Targets

```bash
make lint           # Consistency audit (report only)
make fix            # Consistency audit with auto-fix
make update-pages   # Regenerate Pages files
make db-init        # Initialize database
make maintenance    # Full maintenance suite
make help           # Show all targets
```
