# Contributing to ProjectPortfolio

<!--
  CONTRIBUTING.md — Guidelines for contributing to the ProjectPortfolio repository.
  This file ensures all contributors follow the same standards for consistency.
-->

Thank you for your interest in contributing! This document explains conventions
and workflows used in this repository.

## Getting Started

1. **Fork** this repository and clone your fork locally.
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make your changes following the standards below.
4. Commit with clear messages: `git commit -m "Add module-05 notes for IST2263"`
5. Push and open a Pull Request against `main`.

## Repository Standards

All formatting rules are enforced by [`.editorconfig`](.editorconfig). Please
install an EditorConfig plugin for your editor.

| Area              | Convention                                            |
|-------------------|-------------------------------------------------------|
| Encoding          | UTF-8 everywhere                                      |
| Line endings      | LF (Unix-style)                                       |
| Python indent     | 4 spaces (PEP 8)                                      |
| Web files indent  | 2 spaces (HTML, CSS, JS, JSON, YAML)                  |
| Folder names      | `kebab-case` for new folders (see `docs/naming-conventions.md`) |
| File names        | Descriptive, lowercase with hyphens preferred          |
| Documentation     | Every major folder needs a `README.md`                 |

## Adding New Content

### New Course Module
```
school/MGCCC-Spring2026/COURSE-Name/
  README.md          # Objective, tools, steps, evidence, takeaways
  module-01/
  module-02/
```

### New Lab
```
labs/lab-name/
  README.md          # What, why, how, results
```

Also register the lab in the database:
```bash
python scripts/database.py add-lab --name "Lab Name" --description "Short desc" --repo-path "labs/lab-name"
```

### New Certification
```bash
python scripts/database.py add-cert --name "Cert Name" --issuer "Issuer" --issue-date "2026-01-15"
```

## Running Maintenance

```bash
make maintenance     # Full consistency check + pages update
make lint            # Consistency check only
make update-pages    # Regenerate GitHub Pages content
```

## Commit Messages

Use clear, descriptive commit messages:
- `Add module-03 notes for IST1613`
- `Update database with new certification`
- `Fix broken link in docs/index.md`

## Code of Conduct

Be respectful, constructive, and inclusive. This is a learning portfolio —
questions and suggestions are always welcome.
