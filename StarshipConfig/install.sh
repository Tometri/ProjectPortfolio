#!/usr/bin/env bash
# =============================================================================
# install.sh — Deploy starship config to current machine
# Usage: bash install.sh
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SRC="$SCRIPT_DIR/starship.toml"
CONFIG_DST="$HOME/.config/starship.toml"

echo "[starship-deploy] Checking for starship..."

if ! command -v starship &> /dev/null; then
    echo "[starship-deploy] Not found. Installing..."
    curl -sS https://starship.rs/install.sh | sh
else
    INSTALLED=$(starship --version | awk '{print $2}')
    echo "[starship-deploy] Found starship $INSTALLED"
fi

echo "[starship-deploy] Deploying config to $CONFIG_DST"
mkdir -p ~/.config
cp "$CONFIG_SRC" "$CONFIG_DST"
echo "[starship-deploy] Config deployed."

SHELL_NAME=$(basename "$SHELL")
echo "[starship-deploy] Detected shell: $SHELL_NAME"

case "$SHELL_NAME" in
    bash)
        RC="$HOME/.bashrc"
        LINE='eval "$(starship init bash)"'
        ;;
    zsh)
        RC="$HOME/.zshrc"
        LINE='eval "$(starship init zsh)"'
        ;;
    fish)
        RC="$HOME/.config/fish/config.fish"
        LINE='starship init fish | source'
        ;;
    *)
        echo "[starship-deploy] Shell '$SHELL_NAME' not auto-configured."
        echo "  Manually add the starship init line for your shell. See README.md."
        exit 0
        ;;
esac

if grep -qF "$LINE" "$RC" 2>/dev/null; then
    echo "[starship-deploy] Init line already present in $RC — skipping."
else
    echo "$LINE" >> "$RC"
    echo "[starship-deploy] Added init line to $RC"
fi

echo ""
echo "[starship-deploy] DONE. Reload your shell:"
echo "  source $RC"
echo "  -- or open a new terminal --"
