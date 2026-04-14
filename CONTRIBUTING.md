# Contributing to ProjectPortfolio

Thank you for your interest in contributing! This document explains how to
maintain consistency when adding new content to this repository.

## Getting Started

1. **Fork** the repository and create a feature branch from `main`.
2. Follow the conventions described in [`STYLE_GUIDE.md`](STYLE_GUIDE.md).
3. Run the maintenance scripts before submitting a pull request:
   ```bash
   make maintenance
   ```
4. Open a pull request with a clear description of your changes.

## Repository Structure

```
ProjectPortfolio/
├── school/           # Academic coursework organized by term and course
├── SelfStudy/        # Self-directed learning projects
├── labs/             # Hands-on lab exercises (lowercase)
├── Labs/             # Google ADK agent workspace
├── resume/           # Resume documents and versions
├── StarshipConfig/   # Terminal prompt configuration
├── scripts/          # Repository maintenance and utility scripts
├── data/             # SQLite databases and exported data
├── docs/             # GitHub Pages supporting documents
├── .github/          # GitHub Actions workflows
├── index.html        # Portfolio website (GitHub Pages root)
├── styles.css        # Portfolio website styles
└── script.js         # Portfolio website JavaScript
```

## Adding New Content

### School Coursework
Place files under `school/<Institution>-<Term>/<CourseCode>-<Title>/`.
Add a `README.md` (or `.odt`) in each course folder.

### Labs
Create a folder under `labs/<lab-name>/` with a `README.md` that includes:
objective, environment, steps, results, and lessons learned.

### Self-Study Projects
Add projects under `SelfStudy/<topic>/` with descriptive filenames.

### Certifications & Labs Tracking
Use the database CLI to add entries:
```bash
python scripts/database.py add-cert --name "Cert Name" --issuer "Issuer"
python scripts/database.py add-lab --name "Lab Name" --description "Description"
```

## Code Style

- Follow the standards in [`.editorconfig`](.editorconfig).
- Python: PEP 8 with 4-space indentation.
- HTML/CSS/JS: 4-space indentation.
- Markdown: ATX-style headers (`#`), blank line before/after headers.
- See [`STYLE_GUIDE.md`](STYLE_GUIDE.md) for full details.

## Commit Messages

Use clear, descriptive commit messages:
- Start with a verb: `Add`, `Fix`, `Update`, `Remove`, `Refactor`
- Keep the first line under 72 characters
- Reference issue numbers when applicable

## Questions?

Open an issue or reach out via the contact links on the portfolio site.
