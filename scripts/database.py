#!/usr/bin/env python3
"""
scripts/database.py — Labs & Certifications Tracking Database CLI

Manages a SQLite database (data/labs-certs.db) for tracking hands-on labs and
professional certifications. Provides full CRUD operations and export
capabilities for integration with the GitHub Pages portfolio site.

Tables:
  - labs: Tracks lab exercises with status, difficulty, and dates
  - certifications: Tracks professional certifications with expiry tracking

Usage:
  python scripts/database.py --help           # Show all commands
  python scripts/database.py add-lab ...      # Add a new lab
  python scripts/database.py list-labs        # List all labs
  python scripts/database.py add-cert ...     # Add a new certification
  python scripts/database.py list-certs       # List all certifications
  python scripts/database.py export-md        # Export to Markdown
  python scripts/database.py export-json      # Export to JSON
  python scripts/database.py backup           # Create database backup

Requires: Python 3.8+ (uses only stdlib modules)
"""

import argparse
import datetime
import json
import logging
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# ============================================================================
# Configuration
# ============================================================================

# Resolve paths relative to repository root (parent of scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "labs-certs.db"
BACKUP_DIR = REPO_ROOT / "data" / "backups"

# Logging setup — configurable via LOG_LEVEL environment variable
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Database Initialization
# ============================================================================

def get_connection() -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and return a connection.

    The data/ directory is created automatically if it doesn't exist.
    Row factory is set so queries return dict-like Row objects.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent read performance
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Create the labs and certifications tables if they don't already exist.

    Schema design notes:
      - id: Auto-incrementing primary key
      - status: One of 'not-started', 'in-progress', 'completed'
      - difficulty: One of 'beginner', 'intermediate', 'advanced'
      - Dates stored as ISO 8601 text (YYYY-MM-DD) for portability
      - verification_link: Optional URL to credential or lab proof
    """
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS labs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            description     TEXT    DEFAULT '',
            repo_path       TEXT    DEFAULT '',
            start_date      TEXT    DEFAULT '',
            completion_date TEXT    DEFAULT '',
            status          TEXT    DEFAULT 'not-started',
            difficulty      TEXT    DEFAULT 'beginner',
            notes           TEXT    DEFAULT '',
            verification_link TEXT  DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS certifications (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT    NOT NULL,
            issuer            TEXT    DEFAULT '',
            issue_date        TEXT    DEFAULT '',
            expiry_date       TEXT    DEFAULT '',
            credential_id     TEXT    DEFAULT '',
            verification_link TEXT    DEFAULT '',
            notes             TEXT    DEFAULT ''
        );
    """)
    conn.commit()
    logger.info("Database initialized at %s", DB_PATH)


# ============================================================================
# Lab CRUD Operations
# ============================================================================

def add_lab(
    conn: sqlite3.Connection,
    name: str,
    description: str = "",
    repo_path: str = "",
    start_date: str = "",
    completion_date: str = "",
    status: str = "not-started",
    difficulty: str = "beginner",
    notes: str = "",
    verification_link: str = "",
) -> int:
    """
    Insert a new lab record into the database.

    Returns the ID of the newly created lab.
    Validates status and difficulty against allowed values.
    """
    valid_statuses = ("not-started", "in-progress", "completed")
    valid_difficulties = ("beginner", "intermediate", "advanced")

    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
    if difficulty not in valid_difficulties:
        raise ValueError(f"Invalid difficulty '{difficulty}'. Must be one of: {valid_difficulties}")

    cursor = conn.execute(
        """INSERT INTO labs
           (name, description, repo_path, start_date, completion_date,
            status, difficulty, notes, verification_link)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, repo_path, start_date, completion_date,
         status, difficulty, notes, verification_link),
    )
    conn.commit()
    lab_id = cursor.lastrowid
    logger.info("Added lab #%d: %s", lab_id, name)
    return lab_id


def update_lab(conn: sqlite3.Connection, lab_id: int, **kwargs) -> bool:
    """
    Update one or more fields of an existing lab record.

    Accepts any column name as a keyword argument. Only provided fields
    are updated; others remain unchanged.

    Returns True if the record was found and updated.
    """
    allowed_fields = {
        "name", "description", "repo_path", "start_date", "completion_date",
        "status", "difficulty", "notes", "verification_link",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

    if not updates:
        logger.warning("No valid fields provided for update.")
        return False

    # Validate enum fields if they are being updated
    if "status" in updates:
        valid_statuses = ("not-started", "in-progress", "completed")
        if updates["status"] not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
    if "difficulty" in updates:
        valid_difficulties = ("beginner", "intermediate", "advanced")
        if updates["difficulty"] not in valid_difficulties:
            raise ValueError(f"Invalid difficulty. Must be one of: {valid_difficulties}")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [lab_id]
    cursor = conn.execute(f"UPDATE labs SET {set_clause} WHERE id = ?", values)
    conn.commit()

    if cursor.rowcount == 0:
        logger.warning("Lab #%d not found.", lab_id)
        return False

    logger.info("Updated lab #%d: %s", lab_id, ", ".join(updates.keys()))
    return True


def list_labs(conn: sqlite3.Connection, status: Optional[str] = None) -> list[dict]:
    """
    Retrieve all lab records, optionally filtered by status.

    Returns a list of dictionaries for easy serialization and display.
    """
    if status:
        rows = conn.execute(
            "SELECT * FROM labs WHERE status = ? ORDER BY id", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM labs ORDER BY id").fetchall()

    return [dict(row) for row in rows]


# ============================================================================
# Certification CRUD Operations
# ============================================================================

def add_cert(
    conn: sqlite3.Connection,
    name: str,
    issuer: str = "",
    issue_date: str = "",
    expiry_date: str = "",
    credential_id: str = "",
    verification_link: str = "",
    notes: str = "",
) -> int:
    """
    Insert a new certification record into the database.

    Returns the ID of the newly created certification.
    """
    cursor = conn.execute(
        """INSERT INTO certifications
           (name, issuer, issue_date, expiry_date, credential_id,
            verification_link, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, issuer, issue_date, expiry_date, credential_id,
         verification_link, notes),
    )
    conn.commit()
    cert_id = cursor.lastrowid
    logger.info("Added certification #%d: %s", cert_id, name)
    return cert_id


def list_certs(conn: sqlite3.Connection) -> list[dict]:
    """
    Retrieve all certification records.

    Returns a list of dictionaries ordered by issue date (newest first).
    """
    rows = conn.execute(
        "SELECT * FROM certifications ORDER BY issue_date DESC"
    ).fetchall()
    return [dict(row) for row in rows]


# ============================================================================
# Export Functions
# ============================================================================

def export_to_markdown(conn: sqlite3.Connection) -> str:
    """
    Export all labs and certifications as a Markdown-formatted string.

    This output is used by update_pages.py to generate the Labs &
    Certifications section on the GitHub Pages site.
    """
    lines = ["# Labs & Certifications\n"]

    # --- Labs Section ---
    labs = list_labs(conn)
    lines.append("## Labs\n")
    if not labs:
        lines.append("_No labs recorded yet._\n")
    else:
        lines.append("| # | Name | Status | Difficulty | Description |")
        lines.append("|---|------|--------|------------|-------------|")
        for lab in labs:
            link = f"[{lab['name']}]({lab['repo_path']})" if lab["repo_path"] else lab["name"]
            lines.append(
                f"| {lab['id']} | {link} | {lab['status']} | "
                f"{lab['difficulty']} | {lab['description']} |"
            )
    lines.append("")

    # --- Certifications Section ---
    certs = list_certs(conn)
    lines.append("## Certifications\n")
    if not certs:
        lines.append("_No certifications recorded yet._\n")
    else:
        lines.append("| # | Name | Issuer | Issue Date | Expiry | Credential ID |")
        lines.append("|---|------|--------|------------|--------|---------------|")
        for cert in certs:
            name_display = cert["name"]
            if cert["verification_link"]:
                name_display = f"[{cert['name']}]({cert['verification_link']})"
            lines.append(
                f"| {cert['id']} | {name_display} | {cert['issuer']} | "
                f"{cert['issue_date']} | {cert['expiry_date'] or 'N/A'} | "
                f"{cert['credential_id'] or 'N/A'} |"
            )
    lines.append("")

    return "\n".join(lines)


def export_to_json(conn: sqlite3.Connection) -> str:
    """
    Export all labs and certifications as a JSON string.

    Useful for programmatic consumption or API integration.
    """
    data = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "labs": list_labs(conn),
        "certifications": list_certs(conn),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ============================================================================
# Backup Function
# ============================================================================

def backup_database() -> Optional[str]:
    """
    Create a timestamped backup copy of the database file.

    Backups are stored in data/backups/ and gitignored to keep the
    repository clean. Returns the backup file path, or None if the
    source database doesn't exist.
    """
    if not DB_PATH.exists():
        logger.warning("No database found at %s — nothing to back up.", DB_PATH)
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"labs-certs-{timestamp}.db"
    shutil.copy2(str(DB_PATH), str(backup_path))
    logger.info("Database backed up to %s", backup_path)
    return str(backup_path)


# ============================================================================
# CLI Interface
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser with subcommands for all database operations.

    Each subcommand maps to a database function and includes help text.
    """
    parser = argparse.ArgumentParser(
        prog="database.py",
        description="Labs & Certifications Tracking Database CLI",
        epilog="Run 'database.py <command> --help' for command-specific options.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- add-lab ---
    p_add_lab = subparsers.add_parser("add-lab", help="Add a new lab")
    p_add_lab.add_argument("--name", required=True, help="Lab name")
    p_add_lab.add_argument("--description", default="", help="Short description")
    p_add_lab.add_argument("--repo-path", default="", help="Relative path in repo")
    p_add_lab.add_argument("--start-date", default="", help="Start date (YYYY-MM-DD)")
    p_add_lab.add_argument("--completion-date", default="", help="Completion date")
    p_add_lab.add_argument(
        "--status", default="not-started",
        choices=["not-started", "in-progress", "completed"],
        help="Current status (default: not-started)",
    )
    p_add_lab.add_argument(
        "--difficulty", default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Difficulty level (default: beginner)",
    )
    p_add_lab.add_argument("--notes", default="", help="Additional notes")
    p_add_lab.add_argument("--verification-link", default="", help="Link to proof")

    # --- update-lab ---
    p_update_lab = subparsers.add_parser("update-lab", help="Update an existing lab")
    p_update_lab.add_argument("--id", required=True, type=int, help="Lab ID to update")
    p_update_lab.add_argument("--name", help="New name")
    p_update_lab.add_argument("--description", help="New description")
    p_update_lab.add_argument("--repo-path", help="New repo path")
    p_update_lab.add_argument("--start-date", help="New start date")
    p_update_lab.add_argument("--completion-date", help="New completion date")
    p_update_lab.add_argument(
        "--status", choices=["not-started", "in-progress", "completed"],
        help="New status",
    )
    p_update_lab.add_argument(
        "--difficulty", choices=["beginner", "intermediate", "advanced"],
        help="New difficulty",
    )
    p_update_lab.add_argument("--notes", help="New notes")
    p_update_lab.add_argument("--verification-link", help="New verification link")

    # --- list-labs ---
    p_list_labs = subparsers.add_parser("list-labs", help="List all labs")
    p_list_labs.add_argument(
        "--status", choices=["not-started", "in-progress", "completed"],
        help="Filter by status",
    )

    # --- add-cert ---
    p_add_cert = subparsers.add_parser("add-cert", help="Add a new certification")
    p_add_cert.add_argument("--name", required=True, help="Certification name")
    p_add_cert.add_argument("--issuer", default="", help="Issuing organization")
    p_add_cert.add_argument("--issue-date", default="", help="Issue date (YYYY-MM-DD)")
    p_add_cert.add_argument("--expiry-date", default="", help="Expiry date")
    p_add_cert.add_argument("--credential-id", default="", help="Credential ID")
    p_add_cert.add_argument("--verification-link", default="", help="Verification URL")
    p_add_cert.add_argument("--notes", default="", help="Additional notes")

    # --- list-certs ---
    subparsers.add_parser("list-certs", help="List all certifications")

    # --- export-md ---
    subparsers.add_parser("export-md", help="Export data as Markdown")

    # --- export-json ---
    subparsers.add_parser("export-json", help="Export data as JSON")

    # --- backup ---
    subparsers.add_parser("backup", help="Create a database backup")

    # --- init ---
    subparsers.add_parser("init", help="Initialize the database (create tables)")

    return parser


def main() -> int:
    """
    CLI entry point. Parses arguments, connects to the database, and
    dispatches to the appropriate function.

    Returns 0 on success, 1 on error.
    """
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        conn = get_connection()
        init_db(conn)

        if args.command == "init":
            print(f"Database initialized at {DB_PATH}")

        elif args.command == "add-lab":
            lab_id = add_lab(
                conn,
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
            print(f"✅ Added lab #{lab_id}: {args.name}")

        elif args.command == "update-lab":
            # Collect only provided fields (excluding 'command' and 'id')
            update_fields = {
                k.replace("-", "_"): v
                for k, v in vars(args).items()
                if k not in ("command", "id") and v is not None
            }
            success = update_lab(conn, args.id, **update_fields)
            if success:
                print(f"✅ Updated lab #{args.id}")
            else:
                print(f"❌ Lab #{args.id} not found or no changes made.")
                return 1

        elif args.command == "list-labs":
            labs = list_labs(conn, status=args.status)
            if not labs:
                print("No labs found.")
            else:
                # Print a formatted table
                print(f"{'ID':>4} | {'Name':<30} | {'Status':<14} | {'Difficulty':<12} | Description")
                print("-" * 90)
                for lab in labs:
                    print(
                        f"{lab['id']:>4} | {lab['name']:<30} | {lab['status']:<14} | "
                        f"{lab['difficulty']:<12} | {lab['description'][:40]}"
                    )

        elif args.command == "add-cert":
            cert_id = add_cert(
                conn,
                name=args.name,
                issuer=args.issuer,
                issue_date=args.issue_date,
                expiry_date=args.expiry_date,
                credential_id=args.credential_id,
                verification_link=args.verification_link,
                notes=args.notes,
            )
            print(f"✅ Added certification #{cert_id}: {args.name}")

        elif args.command == "list-certs":
            certs = list_certs(conn)
            if not certs:
                print("No certifications found.")
            else:
                print(f"{'ID':>4} | {'Name':<30} | {'Issuer':<20} | {'Issue Date':<12} | Expiry")
                print("-" * 90)
                for cert in certs:
                    print(
                        f"{cert['id']:>4} | {cert['name']:<30} | {cert['issuer']:<20} | "
                        f"{cert['issue_date']:<12} | {cert['expiry_date'] or 'N/A'}"
                    )

        elif args.command == "export-md":
            print(export_to_markdown(conn))

        elif args.command == "export-json":
            print(export_to_json(conn))

        elif args.command == "backup":
            result = backup_database()
            if result:
                print(f"✅ Backup created: {result}")
            else:
                print("❌ No database to back up.")
                return 1

        conn.close()
        return 0

    except Exception as e:
        logger.error("Error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
