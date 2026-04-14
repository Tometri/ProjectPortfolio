#!/usr/bin/env python3
"""
run_all_maintenance.py — One-command maintenance for ProjectPortfolio
=====================================================================
This script runs all maintenance tasks in sequence:
    1. Consistency check (with optional auto-fix)
    2. Pages update (regenerate docs, sitemap, database exports)
    3. Database initialization (if not yet created)
Usage:
    python scripts/run_all_maintenance.py          # Check + update
    python scripts/run_all_maintenance.py --fix    # Auto-fix + update
This is the same as running:
    make maintenance
Dependencies:
    - Python 3.10+ (stdlib only)
"""
import argparse
import subprocess
import sys
from pathlib import Path
# Root of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
def run_script(name: str, args: list[str] | None = None) -> int:
    """
    Run a Python script from the scripts/ directory.
    Args:
        name: Script filename (e.g., 'check_consistency.py')
        args: Additional command-line arguments
    Returns:
        Exit code from the script
    """
    script_path = SCRIPTS_DIR / name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    print(f"\n{'=' * 60}")
    print(f"  Running: {name} {' '.join(args or [])}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode
def main() -> int:
    """Run all maintenance tasks in sequence."""
    parser = argparse.ArgumentParser(
        description="Run all maintenance tasks for ProjectPortfolio"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix safe consistency issues"
    )
    args = parser.parse_args()
    print("╔" + "═" * 58 + "╗")
    print("║  ProjectPortfolio — Full Maintenance Run" + " " * 17 + "║")
    print("╚" + "═" * 58 + "╝")
    exit_code = 0
    # -----------------------------------------------------------------------
    # Step 1: Initialize database if it doesn't exist
    # -----------------------------------------------------------------------
    db_path = REPO_ROOT / "data" / "labs-certs.db"
    if not db_path.exists():
        print("\nDatabase not found — initializing...")
        rc = run_script("database.py", ["init"])
        if rc != 0:
            print("  ⚠ Database initialization had issues")
    else:
        print(f"\n  ✓ Database exists at {db_path.relative_to(REPO_ROOT)}")
    # -----------------------------------------------------------------------
    # Step 2: Consistency check
    # -----------------------------------------------------------------------
    check_args = ["--fix"] if args.fix else []
    rc = run_script("check_consistency.py", check_args)
    if rc != 0 and not args.fix:
        # Non-zero exit means issues found — note but continue
        print("\n  ⚠ Consistency issues found. Run with --fix to auto-fix.")
        exit_code = 1
    # -----------------------------------------------------------------------
    # Step 3: Update pages
    # -----------------------------------------------------------------------
    rc = run_script("update_pages.py")
    if rc != 0:
        print("\n  ⚠ Pages update had issues")
        exit_code = 1
    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print(f"\n{'╔' + '═' * 58 + '╗'}")
    if exit_code == 0:
        print(f"{'║  ✓ All maintenance tasks completed successfully!' + ' ' * 9 + '║'}")
    else:
        print(f"{'║  ⚠ Maintenance completed with warnings (see above)' + ' ' * 6 + '║'}")
    print(f"{'╚' + '═' * 58 + '╝'}")
    return exit_code
if __name__ == "__main__":
    sys.exit(main())

