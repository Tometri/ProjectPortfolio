# Maintenance Guide

<!--
  MAINTENANCE.md — Complete guide to maintaining the ProjectPortfolio repository.
  Documents all automation, scripts, and workflows available for keeping the
  repo consistent, up-to-date, and well-organized.
-->

## Quick Start

```bash
# Run everything at once (recommended after any structural changes)
make maintenance

# Individual tasks
make lint            # Check repository consistency
make fix             # Auto-fix formatting issues (line endings, newlines)
make update-pages    # Regenerate GitHub Pages navigation content
make backup          # Back up the labs/certs database
```

## Verified Goals

| Goal                                   | Status |
|----------------------------------------|--------|
| Repository consistency audit           | ✅ Complete — `scripts/check_consistency.py` |
| EditorConfig for uniform formatting    | ✅ Complete — `.editorconfig` |
| Contributing guidelines                | ✅ Complete — `CONTRIBUTING.md` |
| Style guide documentation              | ✅ Complete — `STYLE_GUIDE.md` |
| GitHub Pages site sync                 | ✅ Complete — `scripts/update_pages.py` |
| Automation scripts                     | ✅ Complete — `scripts/` directory |
| Makefile with targets                  | ✅ Complete — `Makefile` |
| GitHub Actions workflow                | ✅ Complete — `.github/workflows/maintenance.yml` |
| SQLite database for labs & certs       | ✅ Complete — `data/labs-certs.db` |
| Database CLI with full CRUD            | ✅ Complete — `scripts/database.py` |
| Database exports (Markdown & JSON)     | ✅ Complete — `export-md` / `export-json` commands |
| Pages integration with database        | ✅ Complete — `update_pages.py` pulls from DB |
| Environment config template            | ✅ Complete — `.env.example` |
| Repository health status document      | ✅ Complete — `REPO_STATUS.md` |

## Scripts Reference

### `scripts/check_consistency.py`
Audits the entire repository for formatting standard compliance:
- README presence in major directories
- Line endings (LF, not CRLF)
- Final newlines in all text files
- Trailing whitespace detection
- Python indentation (spaces, not tabs)

```bash
python scripts/check_consistency.py          # Check only
python scripts/check_consistency.py --fix    # Auto-fix where possible
```

### `scripts/database.py`
Full-featured CLI for managing labs and certifications:

```bash
# Initialize (safe to run multiple times)
python scripts/database.py init

# Add entries
python scripts/database.py add-lab --name "Lab Name" --description "Description" \
    --repo-path "labs/path" --status "in-progress" --difficulty "intermediate"
python scripts/database.py add-cert --name "Cert Name" --issuer "Org" \
    --issue-date "2026-01-15"

# Update existing entries
python scripts/database.py update-lab --id 1 --status "completed" \
    --completion-date "2026-04-01"

# View and export
python scripts/database.py list-labs
python scripts/database.py list-certs
python scripts/database.py export-md    # Markdown table format
python scripts/database.py export-json  # JSON format

# Backup
python scripts/database.py backup
```

### `scripts/update_pages.py`
Regenerates `docs/index.md` by scanning the repository and pulling from the database:

```bash
python scripts/update_pages.py            # Write updates
python scripts/update_pages.py --dry-run  # Preview only
```

### `scripts/run_all_maintenance.py`
Orchestrates all maintenance tasks in the correct order:
1. Database backup (safety net)
2. Database initialization (idempotent)
3. Consistency audit
4. Pages content regeneration

```bash
python scripts/run_all_maintenance.py        # Check mode
python scripts/run_all_maintenance.py --fix  # Auto-fix mode
```

## GitHub Actions Workflow

The `.github/workflows/maintenance.yml` workflow automatically:
- Runs on every push to `main`
- Runs weekly (Sundays at midnight UTC)
- Can be triggered manually from the Actions tab
- Commits any auto-generated changes back to the repo

## Adding New Content

### New Lab
1. Create the lab directory: `labs/my-new-lab/`
2. Add a `README.md` with objective, tools, steps, evidence, takeaways
3. Register in the database:
   ```bash
   python scripts/database.py add-lab --name "My New Lab" \
       --description "What this lab covers" --repo-path "labs/my-new-lab" \
       --status "in-progress" --difficulty "beginner"
   ```
4. Regenerate pages: `make update-pages`

### New Certification
1. Add any certificate PDF to `docs/Certificates/`
2. Register in the database:
   ```bash
   python scripts/database.py add-cert --name "CompTIA Security+" \
       --issuer "CompTIA" --issue-date "2026-06-01" \
       --credential-id "ABC123" --verification-link "https://..."
   ```
3. Regenerate pages: `make update-pages`

### New Course Module
1. Follow the pattern: `school/SEMESTER/COURSE-Name/module-XX/`
2. Add a `README.md` in each module
3. Run `make update-pages` to update the navigation index

## QoL Improvements

The following quality-of-life features are included beyond the base requirements:

- **Database auto-backup**: Every maintenance run backs up the DB first
- **WAL mode**: Database uses Write-Ahead Logging for better performance
- **Dry-run mode**: Pages updater supports `--dry-run` for safe previewing
- **Input validation**: Database CLI validates status/difficulty enum values
- **Logging**: All scripts use Python's logging module with configurable levels
- **Formatted CLI output**: Tables with aligned columns for list commands
- **Makefile help**: `make help` shows all available targets with descriptions
- **Concurrency guard**: GitHub Actions workflow prevents parallel runs
- **Timestamp tracking**: Pages index shows when it was last generated
