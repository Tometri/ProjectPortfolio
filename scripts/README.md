# Scripts

<!--
  scripts/README.md — Index of all repository utility scripts.
  Updated to include the full maintenance automation suite.
-->

Repository utility scripts for maintenance and automation tasks.

## Included

| Script                      | Language   | Purpose                                         |
|-----------------------------|------------|--------------------------------------------------|
| [`database.py`](database.py) | Python 3 | Labs & certifications tracking database CLI      |
| [`check_consistency.py`](check_consistency.py) | Python 3 | Repository consistency audit |
| [`update_pages.py`](update_pages.py) | Python 3 | GitHub Pages content generator |
| [`run_all_maintenance.py`](run_all_maintenance.py) | Python 3 | Full maintenance orchestrator |
| [`validate-links.ps1`](validate-links.ps1) | PowerShell | Markdown link validation |

## Quick Usage

```bash
# Use Make targets (recommended)
make maintenance      # Full pass
make lint             # Consistency check
make update-pages     # Regenerate pages

# Or call scripts directly
python scripts/database.py --help
python scripts/check_consistency.py
python scripts/update_pages.py
python scripts/run_all_maintenance.py
```
