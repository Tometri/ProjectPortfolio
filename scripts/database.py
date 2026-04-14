#!/usr/bin/env python3
"""
database.py — Labs & Certifications Tracking Database
======================================================

A portable SQLite database for tracking labs and certifications in the
ProjectPortfolio repository. Provides a CLI for managing entries and
exporting data.

Database location: data/labs-certs.db

Tables:
    - labs: Hands-on lab exercises and projects
    - certifications: Professional certifications

Usage:
    python scripts/database.py init                          # Initialize DB
    python scripts/database.py add-lab --name "Lab Name" --description "..."
    python scripts/database.py add-cert --name "Cert Name" --issuer "Issuer"
    python scripts/database.py list-labs                     # List all labs
    python scripts/database.py list-certs                    # List all certs
    python scripts/database.py update-lab --id 1 --status completed
    python scripts/database.py export-md                     # Export to Markdown
    python scripts/database.py export-json                   # Export to JSON
    python scripts/database.py --help                        # Show help

Dependencies:
    - Python 3.10+ (uses sqlite3 from stdlib)
    - No external packages required
"""

import argparse
import json
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Root of the repository (parent of scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Database file path
DB_PATH = REPO_ROOT / "data" / "labs-certs.db"

# Export paths
EXPORT_MD = REPO_ROOT / "data" / "labs-certs.md"
EXPORT_JSON = REPO_ROOT / "data" / "labs-certs.json"


# ---------------------------------------------------------------------------
# Database schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- ==========================================================================
-- Labs table: tracks hands-on lab exercises and projects
-- ==========================================================================
CREATE TABLE IF NOT EXISTS labs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    repo_path       TEXT,          -- Relative path within the repository
    start_date      TEXT,          -- ISO 8601 date (YYYY-MM-DD)
    completion_date TEXT,          -- ISO 8601 date (YYYY-MM-DD)
    status          TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed
    difficulty      TEXT,          -- beginner, intermediate, advanced
    notes           TEXT,
    verification_link TEXT,        -- URL to verify completion
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ==========================================================================
-- Certifications table: tracks professional certifications
-- ==========================================================================
CREATE TABLE IF NOT EXISTS certifications (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    issuer            TEXT,
    issue_date        TEXT,        -- ISO 8601 date (YYYY-MM-DD)
    expiry_date       TEXT,        -- ISO 8601 date (YYYY-MM-DD), NULL if no expiry
    credential_id     TEXT,
    verification_link TEXT,        -- URL to verify the credential
    notes             TEXT,
    created_at        TEXT DEFAULT (datetime('now')),
    updated_at        TEXT DEFAULT (datetime('now'))
);

-- Trigger to auto-update the updated_at timestamp on labs
CREATE TRIGGER IF NOT EXISTS labs_updated_at
    AFTER UPDATE ON labs
    FOR EACH ROW
BEGIN
    UPDATE labs SET updated_at = datetime('now') WHERE id = OLD.id;
END;

-- Trigger to auto-update the updated_at timestamp on certifications
CREATE TRIGGER IF NOT EXISTS certs_updated_at
    AFTER UPDATE ON certifications
    FOR EACH ROW
BEGIN
    UPDATE certifications SET updated_at = datetime('now') WHERE id = OLD.id;
END;
"""

# Sample data to seed the database on first init
SAMPLE_LABS = [
    {
        "name": "Google ADK Coding Assistant Agent",
        "description": "Built an AI coding assistant agent using Google's Agent Development Kit",
        "repo_path": "labs/adk-workspace/my_first_agent/",
        "start_date": "2026-03-01",
        "completion_date": "2026-03-15",
        "status": "completed",
        "difficulty": "intermediate",
        "notes": "Uses Gemini 2.5 Flash model for code generation and review",
    },
    {
        "name": "Google ADK Philosopher Agent",
        "description": "YAML-configured AI agent for philosophy and ethics discussions",
        "repo_path": "Labs/adk-workspace/my_config_agent/",
        "start_date": "2026-03-15",
        "completion_date": "2026-03-20",
        "status": "completed",
        "difficulty": "beginner",
        "notes": "Demonstrates declarative agent configuration using YAML",
    },
    {
        "name": "Linux System Administration Labs",
        "description": "File system hierarchies, permissions, user management, backup/restore",
        "repo_path": "school/MGCCC-Spring2026/IST2263-AdvAdminLinux/",
        "start_date": "2026-01-15",
        "status": "in_progress",
        "difficulty": "intermediate",
        "notes": "Part of IST2263 coursework at MGCCC",
    },
    {
        "name": "Digital Forensics Hash Calculations",
        "description": "Hash calculation exercises for file integrity verification",
        "repo_path": "school/MGCCC-Spring2026/IST1613-CompForensics/",
        "start_date": "2026-01-20",
        "status": "in_progress",
        "difficulty": "intermediate",
        "notes": "Includes metadata analysis and OSINT practice",
    },
]

SAMPLE_CERTS = [
    {
        "name": "Microsoft Azure Fundamentals (AZ-900)",
        "issuer": "Microsoft",
        "issue_date": "2025-06-01",
        "credential_id": "AZ-900",
        "notes": "Core Azure services, identity, networking, security basics",
    },
    {
        "name": "CompTIA Security+",
        "issuer": "CompTIA",
        "notes": "In progress — cybersecurity fundamentals certification",
    },
    {
        "name": "ISC2 Certified in Cybersecurity (CC)",
        "issuer": "ISC2",
        "notes": "In progress — entry-level cybersecurity certification",
    },
]


# ---------------------------------------------------------------------------
# Database connection helper
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    Creates the data/ directory and database file if they don't exist.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# CRUD Functions
# ---------------------------------------------------------------------------

def init_database(seed: bool = True) -> None:
    """
    Initialize the database schema and optionally seed with sample data.

    Args:
        seed: If True and tables are empty, insert sample data.
    """
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)

    if seed:
        # Only seed if tables are empty
        lab_count = conn.execute("SELECT COUNT(*) FROM labs").fetchone()[0]
        cert_count = conn.execute("SELECT COUNT(*) FROM certifications").fetchone()[0]

        if lab_count == 0:
            for lab in SAMPLE_LABS:
                add_lab(conn=conn, **lab)
            print(f"  Seeded {len(SAMPLE_LABS)} sample labs")

        if cert_count == 0:
            for cert in SAMPLE_CERTS:
                add_cert(conn=conn, **cert)
            print(f"  Seeded {len(SAMPLE_CERTS)} sample certifications")

    conn.commit()
    conn.close()
    print(f"  ✓ Database initialized at {DB_PATH.relative_to(REPO_ROOT)}")


def add_lab(
    name: str,
    description: str = "",
    repo_path: str = "",
    start_date: str = "",
    completion_date: str = "",
    status: str = "not_started",
    difficulty: str = "",
    notes: str = "",
    verification_link: str = "",
    conn: sqlite3.Connection | None = None,
) -> int:
    """
    Add a new lab entry to the database.

    Returns:
        The ID of the newly inserted lab.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.execute(
        """INSERT INTO labs
           (name, description, repo_path, start_date, completion_date,
            status, difficulty, notes, verification_link)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, repo_path, start_date, completion_date,
         status, difficulty, notes, verification_link),
    )
    lab_id = cursor.lastrowid

    if close_conn:
        conn.commit()
        conn.close()

    return lab_id


def update_lab(lab_id: int, **kwargs: Any) -> None:
    """
    Update fields on an existing lab entry.

    Args:
        lab_id: The ID of the lab to update.
        **kwargs: Fields to update (e.g., status='completed').
    """
    if not kwargs:
        return

    valid_fields = {
        "name", "description", "repo_path", "start_date",
        "completion_date", "status", "difficulty", "notes",
        "verification_link",
    }
    fields = {k: v for k, v in kwargs.items() if k in valid_fields}
    if not fields:
        print(f"  No valid fields to update. Valid: {valid_fields}")
        return

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [lab_id]

    conn = get_connection()
    conn.execute(f"UPDATE labs SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    print(f"  ✓ Lab {lab_id} updated")


def list_labs() -> list[dict]:
    """List all labs from the database."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM labs ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_cert(
    name: str,
    issuer: str = "",
    issue_date: str = "",
    expiry_date: str = "",
    credential_id: str = "",
    verification_link: str = "",
    notes: str = "",
    conn: sqlite3.Connection | None = None,
) -> int:
    """
    Add a new certification entry to the database.

    Returns:
        The ID of the newly inserted certification.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.execute(
        """INSERT INTO certifications
           (name, issuer, issue_date, expiry_date, credential_id,
            verification_link, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, issuer, issue_date, expiry_date, credential_id,
         verification_link, notes),
    )
    cert_id = cursor.lastrowid

    if close_conn:
        conn.commit()
        conn.close()

    return cert_id


def list_certs() -> list[dict]:
    """List all certifications from the database."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM certifications ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def export_to_markdown() -> str:
    """
    Export all labs and certifications to a Markdown file.

    Returns:
        Path to the generated Markdown file.
    """
    labs = list_labs()
    certs = list_certs()

    lines = [
        "# Labs & Certifications",
        "",
        f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
    ]

    if certs:
        lines.extend(["## Certifications", ""])
        lines.append("| Name | Issuer | Issue Date | Status | Notes |")
        lines.append("|------|--------|-----------|--------|-------|")
        for cert in certs:
            name = cert["name"]
            issuer = cert["issuer"] or "—"
            issue_date = cert["issue_date"] or "—"
            status = "In Progress" if not cert["issue_date"] else "Active"
            notes = cert["notes"] or ""
            lines.append(f"| {name} | {issuer} | {issue_date} | {status} | {notes} |")
        lines.append("")

    if labs:
        lines.extend(["## Labs", ""])
        lines.append("| Name | Status | Difficulty | Path | Notes |")
        lines.append("|------|--------|-----------|------|-------|")
        for lab in labs:
            name = lab["name"]
            status = lab["status"] or "—"
            difficulty = lab["difficulty"] or "—"
            repo_path = lab["repo_path"] or "—"
            notes = lab["notes"] or ""
            lines.append(f"| {name} | {status} | {difficulty} | {repo_path} | {notes} |")
        lines.append("")

    EXPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return str(EXPORT_MD)


def export_to_json() -> str:
    """
    Export all labs and certifications to a JSON file.

    Returns:
        Path to the generated JSON file.
    """
    data = {
        "generated_at": datetime.now().isoformat(),
        "labs": list_labs(),
        "certifications": list_certs(),
    }

    EXPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_JSON.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )
    return str(EXPORT_JSON)


# ---------------------------------------------------------------------------
# CLI — Command-line interface
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="database.py",
        description="Labs & Certifications Tracking Database for ProjectPortfolio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/database.py init
  python scripts/database.py add-lab --name "My Lab" --description "A cool lab"
  python scripts/database.py add-cert --name "AWS CCP" --issuer "Amazon"
  python scripts/database.py list-labs
  python scripts/database.py list-certs
  python scripts/database.py update-lab --id 1 --status completed
  python scripts/database.py export-md
  python scripts/database.py export-json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- init ---
    subparsers.add_parser("init", help="Initialize the database (safe to run multiple times)")

    # --- add-lab ---
    add_lab_parser = subparsers.add_parser("add-lab", help="Add a new lab entry")
    add_lab_parser.add_argument("--name", required=True, help="Lab name")
    add_lab_parser.add_argument("--description", default="", help="Lab description")
    add_lab_parser.add_argument("--repo-path", default="", help="Relative path in repo")
    add_lab_parser.add_argument("--start-date", default="", help="Start date (YYYY-MM-DD)")
    add_lab_parser.add_argument("--completion-date", default="", help="Completion date")
    add_lab_parser.add_argument(
        "--status", default="not_started",
        choices=["not_started", "in_progress", "completed"],
        help="Current status"
    )
    add_lab_parser.add_argument(
        "--difficulty", default="",
        choices=["", "beginner", "intermediate", "advanced"],
        help="Difficulty level"
    )
    add_lab_parser.add_argument("--notes", default="", help="Additional notes")
    add_lab_parser.add_argument("--verification-link", default="", help="Verification URL")

    # --- update-lab ---
    update_lab_parser = subparsers.add_parser("update-lab", help="Update an existing lab")
    update_lab_parser.add_argument("--id", type=int, required=True, help="Lab ID")
    update_lab_parser.add_argument("--name", help="New name")
    update_lab_parser.add_argument("--description", help="New description")
    update_lab_parser.add_argument("--repo-path", help="New repo path")
    update_lab_parser.add_argument("--start-date", help="New start date")
    update_lab_parser.add_argument("--completion-date", help="New completion date")
    update_lab_parser.add_argument(
        "--status",
        choices=["not_started", "in_progress", "completed"],
        help="New status"
    )
    update_lab_parser.add_argument(
        "--difficulty",
        choices=["beginner", "intermediate", "advanced"],
        help="New difficulty"
    )
    update_lab_parser.add_argument("--notes", help="New notes")

    # --- add-cert ---
    add_cert_parser = subparsers.add_parser("add-cert", help="Add a new certification")
    add_cert_parser.add_argument("--name", required=True, help="Certification name")
    add_cert_parser.add_argument("--issuer", default="", help="Issuing organization")
    add_cert_parser.add_argument("--issue-date", default="", help="Issue date (YYYY-MM-DD)")
    add_cert_parser.add_argument("--expiry-date", default="", help="Expiry date (YYYY-MM-DD)")
    add_cert_parser.add_argument("--credential-id", default="", help="Credential ID")
    add_cert_parser.add_argument("--verification-link", default="", help="Verification URL")
    add_cert_parser.add_argument("--notes", default="", help="Additional notes")

    # --- list commands ---
    subparsers.add_parser("list-labs", help="List all labs")
    subparsers.add_parser("list-certs", help="List all certifications")

    # --- export commands ---
    subparsers.add_parser("export-md", help="Export to Markdown file")
    subparsers.add_parser("export-json", help="Export to JSON file")

    return parser


def cli_main() -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "init":
        print("Initializing database...")
        init_database(seed=True)
        return 0

    if args.command == "add-lab":
        lab_id = add_lab(
            name=args.name,
            description=args.description,
            repo_path=args.repo_path,
            start_date=args.start_date,
            completion_date=args.completion_date,
            status=args.status,
            difficulty=args.difficulty,
            notes=args.notes,
            verification_link=args.verification_link,
        )
        print(f"  ✓ Lab added with ID: {lab_id}")
        return 0

    if args.command == "update-lab":
        # Collect only the fields that were explicitly provided
        update_fields = {}
        for field in ["name", "description", "repo_path", "start_date",
                       "completion_date", "status", "difficulty", "notes"]:
            val = getattr(args, field.replace("-", "_"), None)
            if val is not None:
                update_fields[field] = val
        update_lab(args.id, **update_fields)
        return 0

    if args.command == "add-cert":
        cert_id = add_cert(
            name=args.name,
            issuer=args.issuer,
            issue_date=args.issue_date,
            expiry_date=args.expiry_date,
            credential_id=args.credential_id,
            verification_link=args.verification_link,
            notes=args.notes,
        )
        print(f"  ✓ Certification added with ID: {cert_id}")
        return 0

    if args.command == "list-labs":
        labs = list_labs()
        if not labs:
            print("  No labs found. Run 'init' to seed sample data.")
            return 0
        print(f"\n{'ID':<4} {'Name':<40} {'Status':<15} {'Difficulty':<15}")
        print("-" * 74)
        for lab in labs:
            print(f"{lab['id']:<4} {lab['name']:<40} {lab['status']:<15} {lab['difficulty'] or '—':<15}")
        print(f"\nTotal: {len(labs)} labs")
        return 0

    if args.command == "list-certs":
        certs = list_certs()
        if not certs:
            print("  No certifications found. Run 'init' to seed sample data.")
            return 0
        print(f"\n{'ID':<4} {'Name':<45} {'Issuer':<20} {'Issue Date':<12}")
        print("-" * 81)
        for cert in certs:
            print(f"{cert['id']:<4} {cert['name']:<45} {cert['issuer'] or '—':<20} {cert['issue_date'] or 'In Progress':<12}")
        print(f"\nTotal: {len(certs)} certifications")
        return 0

    if args.command == "export-md":
        path = export_to_markdown()
        print(f"  ✓ Exported to {path}")
        return 0

    if args.command == "export-json":
        path = export_to_json()
        print(f"  ✓ Exported to {path}")
        return 0

    parser.print_help()
    return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(cli_main())
