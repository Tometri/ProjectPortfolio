#!/usr/bin/env python3
"""
check_consistency.py — Repository Consistency Audit Script
==========================================================
Scans the entire ProjectPortfolio repository for common inconsistencies
and reports them. Can optionally auto-fix safe issues.
What it checks:
    1. Trailing whitespace in text files
    2. Missing final newlines in text files
    3. Broken relative links in Markdown files
    4. Files with spaces in names (reports, does not auto-fix)
    5. Mixed line endings (CRLF vs LF)
    6. Missing README files in top-level directories
Usage:
    python scripts/check_consistency.py          # Report only
    python scripts/check_consistency.py --fix    # Auto-fix safe issues
Exit codes:
    0 — No issues found (or all issues auto-fixed)
    1 — Issues found that need manual attention
"""
import argparse
import os
import sys
from pathlib import Path
# ---------------------------------------------------------------------------
# Configuration: directories and extensions to check
# ---------------------------------------------------------------------------
# Root of the repository (parent of the scripts/ directory)
REPO_ROOT = Path(__file__).resolve().parent.parent
# Directories to skip during scanning
SKIP_DIRS = {".git", ".vs", "__pycache__", "node_modules", ".venv", "venv"}
# Text file extensions to check for whitespace/newline issues
TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".sh", ".ps1", ".js", ".css", ".html",
    ".yml", ".yaml", ".toml", ".json", ".xml", ".cfg", ".ini", ".env",
}
# Binary file extensions to skip entirely
BINARY_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx", ".odt", ".accdb", ".db",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
    ".zip", ".gz", ".tar", ".thmx", ".url",
}
def is_text_file(path: Path) -> bool:
    """Determine if a file is a text file based on extension."""
    return path.suffix.lower() in TEXT_EXTENSIONS
def should_skip(path: Path) -> bool:
    """Check if a path should be skipped during scanning."""
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return path.suffix.lower() in BINARY_EXTENSIONS
# ---------------------------------------------------------------------------
# Check functions — each returns a list of (file, message) tuples
# ---------------------------------------------------------------------------
def check_trailing_whitespace(fix: bool = False) -> list[tuple[str, str]]:
    """Check for trailing whitespace in text files (except Markdown)."""
    issues = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(REPO_ROOT)):
            continue
        if not is_text_file(path):
            continue
        # Skip Markdown files — trailing spaces can be intentional (line breaks)
        if path.suffix.lower() == ".md":
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        lines = content.splitlines(keepends=True)
        has_trailing = False
        fixed_lines = []
        for line in lines:
            stripped = line.rstrip(" \t")
            if stripped != line.rstrip("\n\r"):
                has_trailing = True
            # Preserve the line ending
            ending = line[len(line.rstrip("\n\r")):]
            fixed_lines.append(stripped + ending)
        if has_trailing:
            rel = path.relative_to(REPO_ROOT)
            if fix:
                path.write_text("".join(fixed_lines), encoding="utf-8")
                issues.append((str(rel), "FIXED: trailing whitespace removed"))
            else:
                issues.append((str(rel), "trailing whitespace found"))
    return issues
def check_final_newline(fix: bool = False) -> list[tuple[str, str]]:
    """Check that text files end with a newline character."""
    issues = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(REPO_ROOT)):
            continue
        if not is_text_file(path):
            continue
        try:
            content = path.read_bytes()
        except OSError:
            continue
        if len(content) == 0:
            continue
        if not content.endswith(b"\n"):
            rel = path.relative_to(REPO_ROOT)
            if fix:
                with open(path, "ab") as f:
                    f.write(b"\n")
                issues.append((str(rel), "FIXED: added final newline"))
            else:
                issues.append((str(rel), "missing final newline"))
    return issues
def check_broken_markdown_links() -> list[tuple[str, str]]:
    """Check for broken relative links in Markdown files."""
    import re
    issues = []
    link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    for path in REPO_ROOT.rglob("*.md"):
        if should_skip(path.relative_to(REPO_ROOT)):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        for match in link_pattern.finditer(content):
            link = match.group(2).strip()
            # Skip external URLs, anchors, and mailto links
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Remove anchor fragments from the link
            clean_link = link.split("#")[0]
            if not clean_link:
                continue
            target = path.parent / clean_link
            if not target.exists():
                rel = path.relative_to(REPO_ROOT)
                issues.append((str(rel), f"broken link: {link}"))
    return issues
def check_spaces_in_names() -> list[tuple[str, str]]:
    """Report files and directories with spaces in their names."""
    issues = []
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT)
        if should_skip(rel):
            continue
        if " " in path.name:
            kind = "directory" if path.is_dir() else "file"
            issues.append((str(rel), f"{kind} name contains spaces"))
    return issues
def check_mixed_line_endings(fix: bool = False) -> list[tuple[str, str]]:
    """Check for files with CRLF line endings (should be LF)."""
    issues = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(REPO_ROOT)):
            continue
        if not is_text_file(path):
            continue
        try:
            content = path.read_bytes()
        except OSError:
            continue
        if b"\r\n" in content:
            rel = path.relative_to(REPO_ROOT)
            if fix:
                fixed = content.replace(b"\r\n", b"\n")
                path.write_bytes(fixed)
                issues.append((str(rel), "FIXED: converted CRLF to LF"))
            else:
                issues.append((str(rel), "uses CRLF line endings (should be LF)"))
    return issues
def check_missing_readmes() -> list[tuple[str, str]]:
    """Check that top-level content directories have a README."""
    issues = []
    top_dirs = ["school", "SelfStudy", "labs", "Labs", "resume",
                "scripts", "StarshipConfig", "docs"]
    for dirname in top_dirs:
        dirpath = REPO_ROOT / dirname
        if dirpath.is_dir():
            has_readme = any(
                (dirpath / name).exists()
                for name in ["README.md", "README.txt", "README.odt"]
            )
            if not has_readme:
                issues.append((dirname, "missing README file"))
    return issues
# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main() -> int:
    """Run all consistency checks and report results."""
    parser = argparse.ArgumentParser(
        description="Repository consistency audit for ProjectPortfolio"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix safe issues (trailing whitespace, line endings, newlines)"
    )
    args = parser.parse_args()
    print("=" * 60)
    print("  ProjectPortfolio — Consistency Audit")
    print("=" * 60)
    print()
    all_issues: list[tuple[str, str]] = []
    checks = [
        ("Trailing Whitespace", lambda: check_trailing_whitespace(args.fix)),
        ("Final Newlines", lambda: check_final_newline(args.fix)),
        ("Broken Markdown Links", check_broken_markdown_links),
        ("Spaces in File/Dir Names", check_spaces_in_names),
        ("Mixed Line Endings (CRLF)", lambda: check_mixed_line_endings(args.fix)),
        ("Missing READMEs", check_missing_readmes),
    ]
    for name, check_fn in checks:
        print(f"Checking: {name}...")
        issues = check_fn()
        if issues:
            for file, msg in issues:
                print(f"  [{file}] {msg}")
            all_issues.extend(issues)
        else:
            print(f"  ✓ No issues")
        print()
    # Summary
    print("=" * 60)
    fixed = sum(1 for _, msg in all_issues if msg.startswith("FIXED:"))
    remaining = len(all_issues) - fixed
    print(f"Total issues: {len(all_issues)}")
    if args.fix:
        print(f"  Auto-fixed: {fixed}")
        print(f"  Remaining (manual): {remaining}")
    print("=" * 60)
    # Return 1 if there are unfixed issues, 0 otherwise
    return 1 if remaining > 0 else 0
if __name__ == "__main__":
    sys.exit(main())

