# =============================================================================
# Makefile — Convenient targets for ProjectPortfolio maintenance
# =============================================================================
#
# Usage:
#   make lint           — Run the consistency audit (report only)
#   make fix            — Run the consistency audit with auto-fix
#   make update-pages   — Regenerate GitHub Pages files from repo state
#   make db-init        — Initialize the labs/certs database
#   make maintenance    — Run full maintenance (lint + update-pages)
#   make all            — Same as maintenance
#
# Requirements:
#   - Python 3.10+
# =============================================================================

# Use Python 3 — override with: make PYTHON=python3.12
PYTHON ?= python3

# Default target
.DEFAULT_GOAL := all

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

.PHONY: all lint fix update-pages db-init maintenance help

## Run full maintenance suite (consistency check + pages update)
all: maintenance

## Run consistency audit — reports issues without modifying files
lint:
	$(PYTHON) scripts/check_consistency.py

## Run consistency audit with auto-fix for safe issues
fix:
	$(PYTHON) scripts/check_consistency.py --fix

## Regenerate GitHub Pages files (docs/index.md, sitemap.xml, data exports)
update-pages:
	$(PYTHON) scripts/update_pages.py

## Initialize the labs & certifications database (safe to run multiple times)
db-init:
	$(PYTHON) scripts/database.py init

## Run all maintenance tasks: consistency check + pages update + database
maintenance:
	$(PYTHON) scripts/run_all_maintenance.py

## Show available targets
help:
	@echo "Available targets:"
	@echo "  make lint           — Run consistency audit (report only)"
	@echo "  make fix            — Run consistency audit with auto-fix"
	@echo "  make update-pages   — Regenerate GitHub Pages files"
	@echo "  make db-init        — Initialize labs/certs database"
	@echo "  make maintenance    — Full maintenance (lint + update)"
	@echo "  make all            — Same as maintenance"
	@echo "  make help           — Show this help message"
