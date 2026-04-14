# ============================================================================
# Makefile — ProjectPortfolio Build & Maintenance Targets
# ============================================================================
# Quick commands for common repository maintenance tasks.
#
# Usage:
#   make help            Show available targets
#   make lint            Run consistency checks
#   make update-pages    Regenerate GitHub Pages content
#   make maintenance     Full maintenance pass (backup + lint + pages)
#   make fix             Auto-fix formatting issues
#   make db-init         Initialize the labs/certs database
#   make backup          Back up the database
#   make all             Alias for 'maintenance'
# ============================================================================

# Use the Python 3 interpreter available on the system
PYTHON := python3
SCRIPTS := scripts

# Default target — show help
.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help message
	@echo "ProjectPortfolio — Available Make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ── Maintenance ─────────────────────────────────────────────────────────────
.PHONY: maintenance
maintenance: ## Run full maintenance (backup, lint, update pages)
	$(PYTHON) $(SCRIPTS)/run_all_maintenance.py

.PHONY: all
all: maintenance ## Alias for 'maintenance'

# ── Lint / Consistency ──────────────────────────────────────────────────────
.PHONY: lint
lint: ## Run repository consistency checks
	$(PYTHON) $(SCRIPTS)/check_consistency.py

.PHONY: fix
fix: ## Auto-fix formatting issues (line endings, newlines)
	$(PYTHON) $(SCRIPTS)/check_consistency.py --fix

# ── GitHub Pages ────────────────────────────────────────────────────────────
.PHONY: update-pages
update-pages: ## Regenerate GitHub Pages content from repo state
	$(PYTHON) $(SCRIPTS)/update_pages.py

.PHONY: preview-pages
preview-pages: ## Preview Pages content without writing (dry run)
	$(PYTHON) $(SCRIPTS)/update_pages.py --dry-run

# ── Database ────────────────────────────────────────────────────────────────
.PHONY: db-init
db-init: ## Initialize the labs & certifications database
	$(PYTHON) $(SCRIPTS)/database.py init

.PHONY: backup
backup: ## Create a backup of the database
	$(PYTHON) $(SCRIPTS)/database.py backup

.PHONY: list-labs
list-labs: ## List all tracked labs
	$(PYTHON) $(SCRIPTS)/database.py list-labs

.PHONY: list-certs
list-certs: ## List all tracked certifications
	$(PYTHON) $(SCRIPTS)/database.py list-certs

.PHONY: export-md
export-md: ## Export labs & certs as Markdown
	$(PYTHON) $(SCRIPTS)/database.py export-md

.PHONY: export-json
export-json: ## Export labs & certs as JSON
	$(PYTHON) $(SCRIPTS)/database.py export-json
