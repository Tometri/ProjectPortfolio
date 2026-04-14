# Style Guide

This document defines the coding and documentation standards for the
ProjectPortfolio repository. All contributors should follow these conventions.

## General Principles

- **Consistency** over personal preference.
- **Readability** over cleverness.
- **Automation** over manual enforcement — use `.editorconfig` and scripts.

## File Naming

| Type | Convention | Example |
|------|-----------|---------|
| Markdown docs | `kebab-case.md` or `README.md` | `naming-conventions.md` |
| Python scripts | `snake_case.py` | `bill_split_calculator.py` |
| Shell scripts | `kebab-case.sh` | `install.sh` |
| HTML/CSS/JS | `kebab-case` | `styles.css`, `script.js` |
| Course folders | `CourseCode-Title` | `IST2263-AdvAdminLinux` |
| Module folders | `ModuleName` or `module-name` | `ModuleOne`, `module-01` |

## Folder Naming

- Top-level folders use `PascalCase` for category names: `SelfStudy/`, `StarshipConfig/`
- Course-related folders preserve their existing convention: `MGCCC-Spring2026/`
- New folders should prefer `kebab-case` when possible
- Avoid spaces in folder names (existing ones are grandfathered)

## Indentation & Formatting

| Language | Indent | Style |
|----------|--------|-------|
| Python | 4 spaces | PEP 8 |
| HTML | 4 spaces | Standard |
| CSS | 4 spaces | BEM-inspired class names |
| JavaScript | 4 spaces | ES6+, single quotes |
| YAML/TOML | 2 spaces | Standard |
| Makefile | Tabs | Required by Make |
| Markdown | N/A | ATX headers, blank lines around blocks |
| Shell | 4 spaces | POSIX-compatible |

## Markdown Standards

- Use ATX-style headers (`#`, `##`, `###`)
- One blank line before and after headers
- One blank line before and after code blocks
- Use fenced code blocks with language identifiers
- Wrap lines at 80 characters where practical (not enforced in tables)
- Use `- ` for unordered lists (not `*`)

## Python Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for function signatures
- Include docstrings for all public functions and classes
- Use `f-strings` for string formatting
- Maximum line length: 100 characters

## HTML/CSS Standards

- Use semantic HTML5 elements
- CSS custom properties (variables) in `:root`
- BEM-inspired class naming: `.block-name`, `.block-name__element`
- Mobile-first responsive design

## JavaScript Standards

- ES6+ syntax (arrow functions, `const`/`let`, template literals)
- No `var` declarations
- Single quotes for strings
- Semicolons required

## Comment Style

- Python: `# Comment` for inline, docstrings for functions
- HTML: `<!-- Comment -->`
- CSS: `/* Comment */`
- JavaScript: `// Comment` for inline, `/* */` for blocks
- Shell: `# Comment`
- All comments should explain *why*, not *what*

## Git Conventions

- Branch names: `feature/description`, `fix/description`, `docs/description`
- Commit messages: imperative mood, under 72 characters
- One logical change per commit
