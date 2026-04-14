#!/usr/bin/env python3
"""
scripts/run_all_maintenance.py — Full Repository Maintenance Orchestrator

Runs all maintenance tasks in the correct order:
  1. Back up the database (safety first)
  2. Run consistency checks
  3. Regenerate GitHub Pages content
  4. Print a summary report

This is the script behind 'make maintenance'. It coordinates all the
individual maintenance scripts into a single reliable workflow.

Usage:
  python scripts/run_all_maintenance.py          # Run all tasks
  python scripts/run_all_maintenance.py --fix    # Run with auto-fix enabled

Exit codes:
  0 — All tasks completed successfully
  1 — One or more tasks had issues (details in output)
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Task Runner
# ============================================================================

def run_task(name: str, command: list[str]) -> bool:
    """
    Run a maintenance task as a subprocess and report its result.

    Args:
        name: Human-readable task description
        command: Command and arguments to execute

    Returns:
        True if the task succeeded (exit code 0), False otherwise.
    """
    logger.info("─" * 50)
    logger.info("▶ %s", name)
    logger.info("  Command: %s", " ".join(command))
    logger.info("")

    start = time.time()
    result = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=False,  # Let output flow to terminal
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        logger.info("  ✅ %s — completed in %.1fs", name, elapsed)
    else:
        logger.info("  ❌ %s — failed (exit code %d) in %.1fs", name, result.returncode, elapsed)

    return result.returncode == 0


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    """
    Orchestrate all maintenance tasks and produce a summary.

    Steps:
      1. Database backup — Protects data before any changes
      2. Database init — Ensures tables exist
      3. Consistency check — Audits repo formatting standards
      4. Pages update — Regenerates docs/index.md from repo state

    Returns 0 if all tasks pass, 1 if any fail.
    """
    python = sys.executable  # Use the same Python interpreter
    fix_flag = "--fix" in sys.argv

    logger.info("=" * 60)
    logger.info("  Full Repository Maintenance")
    logger.info("  %s", "Auto-fix enabled" if fix_flag else "Check-only mode")
    logger.info("=" * 60)
    logger.info("")

    results = []

    # Task 1: Database backup (non-critical — don't fail if DB doesn't exist yet)
    results.append(run_task(
        "Database Backup",
        [python, str(SCRIPTS_DIR / "database.py"), "backup"],
    ))

    # Task 2: Initialize database (idempotent — safe to run always)
    results.append(run_task(
        "Database Initialize",
        [python, str(SCRIPTS_DIR / "database.py"), "init"],
    ))

    # Task 3: Consistency check
    consistency_cmd = [python, str(SCRIPTS_DIR / "check_consistency.py")]
    if fix_flag:
        consistency_cmd.append("--fix")
    results.append(run_task("Consistency Audit", consistency_cmd))

    # Task 4: Update Pages content
    results.append(run_task(
        "GitHub Pages Update",
        [python, str(SCRIPTS_DIR / "update_pages.py")],
    ))

    # --- Summary ---
    logger.info("")
    logger.info("=" * 60)
    logger.info("  Maintenance Summary")
    logger.info("=" * 60)

    task_names = ["Database Backup", "Database Init", "Consistency Audit", "Pages Update"]
    all_passed = True
    for name, passed in zip(task_names, results):
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info("  %s  %s", status, name)
        if not passed and name != "Database Backup":
            # Database backup failure is non-critical (DB might not exist yet)
            all_passed = False

    logger.info("")
    if all_passed:
        logger.info("✅ All maintenance tasks completed successfully!")
    else:
        logger.info("⚠  Some tasks had issues. Review the output above.")
    logger.info("")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
