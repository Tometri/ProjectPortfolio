# Style Guide

<!--
  STYLE_GUIDE.md — Documents the uniform coding and documentation standards
  applied across the ProjectPortfolio repository. All conventions are also
  enforced by .editorconfig and checked by scripts/check_consistency.py.
-->

## Formatting

| Rule                  | Standard                              | Rationale                    |
|-----------------------|---------------------------------------|------------------------------|
| Character encoding    | UTF-8                                 | Universal compatibility      |
| Line endings          | LF                                    | Cross-platform consistency   |
| Final newline         | Always                                | POSIX compliance             |
| Trailing whitespace   | Trimmed (except `.md`)                | Clean diffs                  |
| Python indentation    | 4 spaces                              | PEP 8                        |
| Web indentation       | 2 spaces (HTML/CSS/JS/JSON/YAML)      | Industry convention          |
| Makefile indentation  | Tabs                                  | Required by Make             |

## Naming

| Item             | Convention       | Example                         |
|------------------|------------------|---------------------------------|
| New folders      | `kebab-case`     | `module-04`, `hash-calculation` |
| Python files     | `snake_case`     | `check_consistency.py`          |
| Shell scripts    | `kebab-case`     | `run-maintenance.sh`            |
| Markdown docs    | Descriptive name | `README.md`, `naming-conventions.md` |
| Course folders   | `CODE-Name`      | `IST2263-AdvAdminLinux`         |

## Documentation

Every major directory should include a `README.md` containing:

1. **Objective** — What this folder/project is about.
2. **Tools Used** — Languages, frameworks, platforms.
3. **Steps Performed** — Key actions or workflow.
4. **Evidence** — Screenshots, output, or references.
5. **Key Takeaways** — What was learned.

## Python Code

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type hints for function signatures.
- Include docstrings for all public functions.
- Use `argparse` for CLI interfaces.
- Use `logging` module instead of bare `print()` for scripts.

## PowerShell Code

- Use `param()` blocks for script parameters.
- Set `$ErrorActionPreference = "Stop"` for safety.
- Use approved verbs (`Get-`, `Set-`, `New-`, etc.).

## Git Practices

- Write descriptive commit messages (imperative mood).
- One logical change per commit.
- Keep the `main` branch deployable at all times.

## Enforcement

Standards are checked by:
- `.editorconfig` — Editor-level formatting
- `scripts/check_consistency.py` — Automated consistency audit
- `make lint` — Quick consistency check command
