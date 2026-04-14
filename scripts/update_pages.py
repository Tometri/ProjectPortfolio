#!/usr/bin/env python3
"""
scripts/update_pages.py — GitHub Pages Content Generator

Automatically regenerates the GitHub Pages site content to reflect the current
state of the repository. This script:

  1. Scans the repository for projects, labs, coursework, and certifications
  2. Pulls data from the SQLite database (data/labs-certs.db) for labs & certs
  3. Updates docs/index.md with an accurate navigation index
  4. Generates a labs-and-certs section for the portfolio

This ensures the GitHub Pages site is never out of sync with the actual
repository contents. Run after any structural changes.

Usage:
  python scripts/update_pages.py               # Regenerate all Pages content
  python scripts/update_pages.py --dry-run     # Preview without writing files

Requires: Python 3.8+ (stdlib only)
"""

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DB_PATH = REPO_ROOT / "data" / "labs-certs.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Repository Scanning Functions
# ============================================================================

def scan_school_courses() -> list[dict]:
    """
    Scan the school/ directory for course folders.

    Returns a list of dicts with 'code', 'name', and 'path' keys.
    Handles the MGCCC-Spring2026 semester structure.
    """
    courses = []
    school_dir = REPO_ROOT / "school"
    if not school_dir.is_dir():
        return courses

    for semester_dir in sorted(school_dir.iterdir()):
        if not semester_dir.is_dir() or semester_dir.name.startswith("."):
            continue
        for course_dir in sorted(semester_dir.iterdir()):
            if not course_dir.is_dir() or course_dir.name.startswith("."):
                continue
            # Parse course code from folder name (e.g., "IST2263-AdvAdminLinux")
            parts = course_dir.name.split("-", 1)
            code = parts[0]
            name = parts[1] if len(parts) > 1 else code
            rel_path = course_dir.relative_to(REPO_ROOT)
            courses.append({
                "code": code,
                "name": name,
                "path": str(rel_path),
                "semester": semester_dir.name,
            })

    return courses


def scan_labs() -> list[dict]:
    """
    Scan the labs/ directory for lab project folders.

    Returns a list of dicts with 'name' and 'path' keys.
    """
    labs = []
    labs_dir = REPO_ROOT / "labs"
    if not labs_dir.is_dir():
        return labs

    for item in sorted(labs_dir.iterdir()):
        if item.name.startswith(".") or item.name == "README.md" or item.name == "README.odt":
            continue
        if item.is_dir():
            labs.append({
                "name": item.name,
                "path": str(item.relative_to(REPO_ROOT)),
            })

    return labs


def scan_self_study() -> list[dict]:
    """
    Scan the SelfStudy/ directory for self-study projects.

    Returns a list of dicts with 'name' and 'path' keys.
    """
    projects = []
    # Check both SelfStudy (existing) and self-study (standard)
    for dirname in ["SelfStudy", "self-study"]:
        study_dir = REPO_ROOT / dirname
        if not study_dir.is_dir():
            continue
        for item in sorted(study_dir.iterdir()):
            if item.name.startswith(".") or item.name == "README.md":
                continue
            if item.is_dir() or item.suffix == ".py":
                projects.append({
                    "name": item.stem if item.is_file() else item.name,
                    "path": str(item.relative_to(REPO_ROOT)),
                })

    return projects


def get_database_content() -> str:
    """
    Pull labs and certifications data from the SQLite database and return
    it as formatted Markdown.

    If the database doesn't exist or has no data, returns a placeholder
    message. This function imports database.py dynamically to reuse its
    export function.
    """
    if not DB_PATH.exists():
        return (
            "## Labs & Certifications\n\n"
            "_Database not yet initialized. Run `python scripts/database.py init` "
            "to set up tracking._\n"
        )

    # Import the database module from scripts/
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import database
        conn = database.get_connection()
        database.init_db(conn)
        md = database.export_to_markdown(conn)
        conn.close()
        return md
    except Exception as e:
        logger.warning("Could not read database: %s", e)
        return "## Labs & Certifications\n\n_Error reading database._\n"
    finally:
        sys.path.pop(0)


# ============================================================================
# Content Generation
# ============================================================================

def generate_index_md() -> str:
    """
    Generate a complete docs/index.md navigation hub based on the current
    repository contents and database.

    This is the single source of truth for the GitHub Pages site navigation.
    Every time this runs, it produces a fresh, accurate index.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Repository Index",
        "",
        f"<!-- Auto-generated by scripts/update_pages.py on {timestamp} -->",
        "<!-- Do not edit manually — run 'make update-pages' to regenerate -->",
        "",
        "This file is the navigation hub for the portfolio.",
        "",
    ]

    # --- Top-Level Areas ---
    lines.append("## Top-Level Areas\n")
    top_dirs = [
        ("school", "Academic coursework"),
        ("labs", "Hands-on lab exercises"),
        ("SelfStudy", "Self-directed learning projects"),
        ("resume", "Resume and career documents"),
        ("scripts", "Repository utility scripts"),
        ("docs", "Documentation and guides"),
        ("StarshipConfig", "Terminal configuration"),
    ]
    for dirname, desc in top_dirs:
        dirpath = REPO_ROOT / dirname
        if dirpath.is_dir():
            readme = f"../{dirname}/README.md"
            lines.append(f"- [`{dirname}/`]({readme}) — {desc}")
    lines.append("")

    # --- School Courses ---
    courses = scan_school_courses()
    if courses:
        lines.append("## School Courses\n")
        current_semester = None
        for course in courses:
            if course["semester"] != current_semester:
                current_semester = course["semester"]
                lines.append(f"### {current_semester}\n")
            lines.append(f"- [`{course['code']}`](../{course['path']}/) — {course['name']}")
        lines.append("")

    # --- Labs ---
    scanned_labs = scan_labs()
    if scanned_labs:
        lines.append("## Lab Projects\n")
        for lab in scanned_labs:
            lines.append(f"- [`{lab['name']}`](../{lab['path']}/)")
        lines.append("")

    # --- Self-Study ---
    study_projects = scan_self_study()
    if study_projects:
        lines.append("## Self-Study Projects\n")
        for project in study_projects:
            lines.append(f"- [`{project['name']}`](../{project['path']}/)")
        lines.append("")

    # --- Database Content (Labs & Certifications) ---
    db_content = get_database_content()
    lines.append(db_content)

    # --- Standards ---
    lines.append("## Standards & Guides\n")
    lines.append("- [Naming Conventions](naming-conventions.md)")
    lines.append("- [Structure Roadmap](portfolio-roadmap.md)")
    lines.append("- [Style Guide](../STYLE_GUIDE.md)")
    lines.append("- [Contributing](../CONTRIBUTING.md)")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    """
    Regenerate all GitHub Pages content files.

    Returns 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Regenerate GitHub Pages site content from repository state"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview generated content without writing files",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("GitHub Pages Content Generator")
    logger.info("=" * 60)

    # Generate docs/index.md
    index_content = generate_index_md()

    if args.dry_run:
        logger.info("DRY RUN — would write docs/index.md:")
        print(index_content)
    else:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        index_path = DOCS_DIR / "index.md"
        index_path.write_text(index_content, encoding="utf-8")
        logger.info("Updated %s", index_path.relative_to(REPO_ROOT))

    logger.info("")
    logger.info("✅ Pages content generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
