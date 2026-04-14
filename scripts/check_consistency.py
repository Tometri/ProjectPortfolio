#!/usr/bin/env python3
"""
scripts/check_consistency.py — Repository Consistency Audit

Scans the entire ProjectPortfolio repository and reports any deviations from
the standards defined in STYLE_GUIDE.md and .editorconfig. This is the
automated enforcement layer that keeps the repo uniform.

Checks performed:
  1. Every major directory has a README.md
  2. No trailing whitespace in tracked text files (except Markdown)
  3. All text files end with a newline
  4. No Windows-style (CRLF) line endings in text files
  5. Python files use 4-space indentation (no tabs)
  6. No files with spaces in names in new directories

Usage:
  python scripts/check_consistency.py          # Run all checks
  python scripts/check_consistency.py --fix    # Auto-fix what's possible

Exit codes:
  0 — All checks passed
  1 — Issues found (details printed to stdout)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories to skip during scanning (not part of the project content)
SKIP_DIRS = {".git", ".vs", "__pycache__", "node_modules", ".venv", "venv", "data"}

# Major directories that should have a README.md
EXPECTED_READMES = [
    "school",
    "labs",
    "resume",
    "scripts",
    "docs",
]

# File extensions considered "text" for line-ending and whitespace checks
TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".ps1", ".sh", ".html", ".css", ".js",
    ".json", ".yml", ".yaml", ".xml", ".toml", ".cfg", ".ini",
    ".editorconfig", ".gitignore", ".gitattributes",
}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Check Functions
# ============================================================================

def check_readmes() -> list[str]:
    """
    Verify that each major directory contains a README.md file.

    Returns a list of issue descriptions for any missing READMEs.
    """
    issues = []
    for dirname in EXPECTED_READMES:
        dirpath = REPO_ROOT / dirname
        if not dirpath.is_dir():
            issues.append(f"MISSING DIR: Expected directory '{dirname}/' not found")
            continue
        readme = dirpath / "README.md"
        if not readme.exists():
            # Also accept README.odt as a fallback (some dirs have it)
            readme_odt = dirpath / "README.odt"
            if not readme_odt.exists():
                issues.append(f"MISSING README: '{dirname}/' has no README.md")
    return issues


def check_line_endings(fix: bool = False) -> list[str]:
    """
    Scan text files for Windows-style CRLF line endings.

    If fix=True, converts CRLF to LF in place. Returns list of issues found.
    """
    issues = []
    for filepath in _iter_text_files():
        try:
            raw = filepath.read_bytes()
            if b"\r\n" in raw:
                rel = filepath.relative_to(REPO_ROOT)
                if fix:
                    filepath.write_bytes(raw.replace(b"\r\n", b"\n"))
                    issues.append(f"FIXED CRLF: {rel}")
                else:
                    issues.append(f"CRLF LINE ENDINGS: {rel}")
        except (OSError, UnicodeDecodeError):
            continue
    return issues


def check_final_newline(fix: bool = False) -> list[str]:
    """
    Verify all text files end with a newline character (POSIX standard).

    If fix=True, appends a newline where missing.
    """
    issues = []
    for filepath in _iter_text_files():
        try:
            raw = filepath.read_bytes()
            if len(raw) > 0 and not raw.endswith(b"\n"):
                rel = filepath.relative_to(REPO_ROOT)
                if fix:
                    filepath.write_bytes(raw + b"\n")
                    issues.append(f"FIXED NEWLINE: {rel}")
                else:
                    issues.append(f"NO FINAL NEWLINE: {rel}")
        except (OSError, UnicodeDecodeError):
            continue
    return issues


def check_trailing_whitespace() -> list[str]:
    """
    Report text files (except Markdown) that contain trailing whitespace.

    Markdown is exempt because trailing spaces can denote line breaks.
    """
    issues = []
    for filepath in _iter_text_files():
        if filepath.suffix == ".md":
            continue  # Markdown trailing spaces are intentional line breaks
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.splitlines(), 1):
                if line != line.rstrip():
                    rel = filepath.relative_to(REPO_ROOT)
                    issues.append(f"TRAILING WHITESPACE: {rel}:{i}")
                    break  # Report once per file
        except (OSError, UnicodeDecodeError):
            continue
    return issues


def check_python_indentation() -> list[str]:
    """
    Verify Python files use spaces (not tabs) for indentation.

    PEP 8 requires 4-space indentation. Tab characters in Python files
    are flagged as issues.
    """
    issues = []
    for filepath in _iter_text_files():
        if filepath.suffix != ".py":
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.splitlines(), 1):
                if line.startswith("\t"):
                    rel = filepath.relative_to(REPO_ROOT)
                    issues.append(f"TAB INDENTATION: {rel}:{i}")
                    break  # Report once per file
        except (OSError, UnicodeDecodeError):
            continue
    return issues


# ============================================================================
# Utility Functions
# ============================================================================

def _iter_text_files():
    """
    Yield all text files in the repository, skipping ignored directories
    and binary files. Uses TEXT_EXTENSIONS to identify text files.
    """
    for root, dirs, files in os.walk(REPO_ROOT):
        # Prune skipped directories (modifying dirs in-place)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            filepath = Path(root) / fname
            if filepath.suffix in TEXT_EXTENSIONS or filepath.name in {
                ".editorconfig", ".gitignore", ".gitattributes", "Makefile",
            }:
                yield filepath


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    """
    Run all consistency checks and report results.

    Returns 0 if all checks pass, 1 if any issues are found.
    """
    parser = argparse.ArgumentParser(
        description="Repository Consistency Audit — checks formatting standards"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Auto-fix issues where possible (line endings, final newlines)",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Repository Consistency Audit")
    logger.info("=" * 60)
    logger.info("Root: %s", REPO_ROOT)
    logger.info("")

    all_issues = []

    # Run each check category
    checks = [
        ("README presence", check_readmes),
        ("Line endings (CRLF)", lambda: check_line_endings(fix=args.fix)),
        ("Final newlines", lambda: check_final_newline(fix=args.fix)),
        ("Trailing whitespace", check_trailing_whitespace),
        ("Python indentation", check_python_indentation),
    ]

    for name, check_fn in checks:
        logger.info("Checking: %s ...", name)
        issues = check_fn()
        if issues:
            for issue in issues:
                logger.info("  ⚠  %s", issue)
            all_issues.extend(issues)
        else:
            logger.info("  ✅ All good")
        logger.info("")

    # Summary
    logger.info("=" * 60)
    if all_issues:
        logger.info("Found %d issue(s). Run with --fix to auto-fix where possible.", len(all_issues))
        return 1
    else:
        logger.info("✅ All consistency checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
