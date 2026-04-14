# Repository Health Status

<!--
  REPO_STATUS.md — One-page health check of the ProjectPortfolio repository.
  Last updated: 2026-04-14
-->

## Overall Status: ✅ Healthy

| Area                    | Status | Details                                    |
|-------------------------|--------|--------------------------------------------|
| **Consistency**         | ✅     | Standards defined and enforced via scripts  |
| **Pages Sync**          | ✅     | `docs/index.md` auto-generated from repo   |
| **Database**            | ✅     | `data/labs-certs.db` initialized with data  |
| **Automation**          | ✅     | `Makefile` + GitHub Actions workflow ready  |
| **Documentation**       | ✅     | Style guide, contributing, maintenance docs |

## Configuration Files

| File                | Purpose                              | Present |
|---------------------|--------------------------------------|---------|
| `.editorconfig`     | Editor formatting rules              | ✅      |
| `.gitignore`        | Version control exclusions           | ✅      |
| `.gitattributes`    | Git line-ending normalization        | ✅      |
| `.env.example`      | Environment variable template        | ✅      |
| `Makefile`          | Build/maintenance command targets    | ✅      |

## Documentation

| File                | Purpose                              | Present |
|---------------------|--------------------------------------|---------|
| `README.md`         | Repository overview                  | ✅      |
| `CONTRIBUTING.md`   | Contribution guidelines              | ✅      |
| `STYLE_GUIDE.md`    | Coding and formatting standards      | ✅      |
| `MAINTENANCE.md`    | Maintenance procedures and commands  | ✅      |
| `REPO_STATUS.md`    | This health check document           | ✅      |

## Automation

| Component                              | Location                               | Status |
|----------------------------------------|----------------------------------------|--------|
| Consistency checker                    | `scripts/check_consistency.py`         | ✅     |
| Database CLI                           | `scripts/database.py`                  | ✅     |
| Pages generator                        | `scripts/update_pages.py`              | ✅     |
| Maintenance orchestrator               | `scripts/run_all_maintenance.py`       | ✅     |
| Link validator                         | `scripts/validate-links.ps1`           | ✅     |
| GitHub Actions workflow                | `.github/workflows/maintenance.yml`    | ✅     |

## Database

- **Path**: `data/labs-certs.db`
- **Engine**: SQLite with WAL mode
- **Tables**: `labs` (10 columns), `certifications` (8 columns)
- **Backup**: Automatic on every maintenance run → `data/backups/`
- **CLI**: `python scripts/database.py --help`

## Known Informational Notes

- Some pre-existing files (`index.html`, `styles.css`) contain minor trailing whitespace.
  These are flagged by the consistency checker but don't affect functionality.
- Legacy uppercase directories (`Labs/`, `School/`, `SelfStudy/`) coexist with
  lowercase equivalents — the consistency checker works with the active lowercase versions.

## Commands to Verify

```bash
make maintenance      # Full pass: backup → lint → pages update
make lint             # Consistency check only
make update-pages     # Regenerate navigation index
make help             # See all available targets
```
