# STARSHIP TERMINAL CONFIG
> Universal information-dense retro terminal prompt.  
> No GUI required. Full situational awareness from the command line.

---

## WHAT IT DOES

Every prompt renders four bordered lines of context before your cursor:

```
╔══[ SYS ]══════════════════════════════════════════════════════════════
 [linux] <tree>@hostname [CHG 87%] MEM:42% CPU:9% [2025-06-01 14:32:07]
╠══[ ENV ]══════════════════════════════════════════════════════════════
~/Projects/beaconhold git:(main) [MOD:2][STAGED:1] +44/-12
╠══[ CTX ]══════════════════════════════════════════════════════════════
 py:3.11.9(venv) node:20.11.0 docker:default
╠══[ CMD ]══════════════════════════════════════════════════════════════
 [[ SUDO ACTIVE ]] JOBS:1 [OK] TOOK:1.2s
╚══[ >> ] >_
```

**SYS row** — OS label, username (root blazes red/blink), hostname, battery with charge state and color-coded level, RAM percent, CPU percent, timestamp.

**ENV row** — Full directory path (truncated to 6 levels, repo-aware), git branch, commit hash, repo state (REBASE/MERGE/etc), file-level status counts, and line diff stats.

**CTX row** — Only shows environments actively detected in the current directory. If no Python/Node/Rust/etc is present, nothing renders. Includes Docker context, conda env, Terraform workspace, and Kubernetes context/namespace.

**CMD row** — Sudo session indicator (blinks), background job count (blinks), last command exit code with common meaning (NOTFOUND, SIGINT, etc), pipeline status, and command duration (shown after 500ms, notifies after 30s).

**Right prompt** — Local IP address and shell nesting level (shown when > 1 deep).

---

## PREREQUISITES

### 1. Install Starship

```bash
# Universal installer (Linux/macOS)
curl -sS https://starship.rs/install.sh | sh

# Debian/Ubuntu (alternative)
sudo apt install starship

# Arch
sudo pacman -S starship

# macOS via Homebrew
brew install starship
```

Verify: `starship --version` — requires **v1.16.0 or later** for CPU module support.

### 2. Install a Nerd Font (optional but recommended)

This config uses ASCII fallbacks everywhere, so it works in any terminal. However if you want clean box-drawing characters, ensure your terminal uses a font that supports them (most modern terminal fonts do — Nerd Fonts, JetBrains Mono, Fira Code, etc).

Test box-drawing support in your terminal:
```bash
echo "╔══╗"
echo "║  ║"
echo "╚══╝"
```
If those render as boxes, you're good. If they render as garbage, switch your terminal font.

---

## INSTALLATION

### Step 1 — Place the config file

```bash
# Create the starship config directory if it doesn't exist
mkdir -p ~/.config

# Copy starship.toml to the standard location
cp starship.toml ~/.config/starship.toml
```

### Step 2 — Add Starship init to your shell

#### Bash (`~/.bashrc`)
```bash
eval "$(starship init bash)"
```

#### Zsh (`~/.zshrc`)
```bash
eval "$(starship init zsh)"
```

#### Fish (`~/.config/fish/config.fish`)
```fish
starship init fish | source
```

#### Nushell (`$nu.env-path`)
```nushell
mkdir ~/.cache/starship
starship init nu | save -f ~/.cache/starship/init.nu
```
Then in `$nu.config-path`:
```nushell
source ~/.cache/starship/init.nu
```

### Step 3 — Reload your shell

```bash
# Bash/Zsh
source ~/.bashrc   # or ~/.zshrc

# Or just open a new terminal
```

---

## MULTI-MACHINE DEPLOYMENT

### Symlink from your dotfiles repo

```bash
# If you keep dotfiles in ~/dotfiles or ~/ProjectPortfolio:
ln -sf ~/ProjectPortfolio/starship/starship.toml ~/.config/starship.toml
```

This way, pulling the repo updates your prompt everywhere.

### Via Git clone + setup script

```bash
git clone https://github.com/[your-username]/ProjectPortfolio.git
cd ProjectPortfolio/starship
cp starship.toml ~/.config/starship.toml
# Then add the shell init line manually per shell above
```

### Quick bootstrap (single command)

Add this to a setup script in your repo:

```bash
#!/usr/bin/env bash
set -e

# Install starship if not present
if ! command -v starship &> /dev/null; then
    curl -sS https://starship.rs/install.sh | sh
fi

# Deploy config
mkdir -p ~/.config
cp "$(dirname "$0")/starship.toml" ~/.config/starship.toml

# Detect shell and add init line if not present
SHELL_NAME=$(basename "$SHELL")
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
        echo "Shell $SHELL_NAME not auto-configured. Add starship init manually."
        exit 0
        ;;
esac

grep -qF "$LINE" "$RC" || echo "$LINE" >> "$RC"
echo "Starship deployed for $SHELL_NAME. Reload your shell."
```

Save as `starship/install.sh`, `chmod +x starship/install.sh`, run it on any new machine.

---

## MODULE REFERENCE

| Section | Module | What It Shows |
|---------|--------|---------------|
| SYS | `os` | OS identifier in ASCII (linux, deb, arch, win, osx…) |
| SYS | `username` | Current user; root turns red and blinks |
| SYS | `hostname` | Machine hostname; always shown (not SSH-only) |
| SYS | `battery` | State (CHG/BAT/!!!), percentage, color by level |
| SYS | `memory_usage` | RAM usage percent |
| SYS | `cpu` | CPU usage percent (v1.16+) |
| SYS | `time` | ISO date + 24h time |
| ENV | `directory` | Path, 6 levels max, repo-aware, RO indicator |
| ENV | `git_branch` | Current branch |
| ENV | `git_commit` | Short hash + tag label |
| ENV | `git_state` | Active git operation (REBASE, MERGE, etc) |
| ENV | `git_status` | File counts: MOD, STAGED, NEW, DEL, REN, STASH |
| ENV | `git_metrics` | Line-level diff (+added/-deleted) |
| CTX | `python` | Version + virtualenv name if active |
| CTX | `nodejs` | Node version if package.json present |
| CTX | `rust` | Rust version if Cargo.toml present |
| CTX | `golang` | Go version if go.mod present |
| CTX | `java` | Java version if pom.xml / build.gradle present |
| CTX | `docker_context` | Active Docker context |
| CTX | `conda` | Active conda environment |
| CTX | `terraform` | TF version + workspace |
| CTX | `kubernetes` | Current k8s context + namespace |
| CMD | `sudo` | `[[ SUDO ACTIVE ]]` blinks when sudo session cached |
| CMD | `jobs` | Background job count; blinks when nonzero |
| CMD | `status` | OK / FAIL / NOEXEC / NOTFOUND / SIGINT + exit code |
| CMD | `cmd_duration` | Execution time (shown >500ms, notifies >30s) |
| RIGHT | `localip` | Machine's local IPv4 |
| RIGHT | `shlvl` | Shell nesting depth (shown when >1) |
| INPUT | `character` | `>_` success / `!>` error / `CMD/VIS/RR` for vim modes |

---

## BATTERY COLOR THRESHOLDS

| Level | Display | Color |
|-------|---------|-------|
| 0–10% | `[!!!]` | Red blinking |
| 11–25% | `[BAT 22%]` | Red |
| 26–50% | `[BAT 44%]` | Yellow |
| 51–100% | `[BAT 87%]` | Green |
| Charging | `[CHG 67%]` | Green |

---

## CUSTOMIZATION

### Disable modules you don't need

In `starship.toml`, find the module and set `disabled = true`:
```toml
[kubernetes]
disabled = true
```

### Change the color palette

Edit the `[palettes.retro_green]` section. Want amber-on-black (classic CRT)?

```toml
[palettes.retro_green]
bright    = "#FFB000"
dim       = "#7A5000"
warn      = "#FF8C00"
danger    = "#FF3131"
ok        = "#FFD700"
neutral   = "#AAAAAA"
muted     = "#555555"
accent    = "#FF6600"
highlight = "#FFFF00"
```

### Flatten to a single-line prompt

Replace the entire `format` block with:
```toml
format = "$os$username$hostname $directory$git_branch$git_status $status$character"
```
Useful for terminals with limited height or tmux panes.

---

## NOTES & KNOWN LIMITATIONS

- **CPU module** requires Starship v1.16.0+. Run `starship --version` to check. If your version is older, add `disabled = true` under `[cpu]` or upgrade.
- **Battery module** shows `[???]` on desktop machines with no battery — this is expected. Set `disabled = true` under `[battery]` on desktops.
- **`cmd_duration`** only measures the previous command's wall time, not active process CPU usage. For real-time process monitoring, pair this config with `htop`, `btop`, or a tmux status bar.
- **Right prompt** (`localip`, `shlvl`) may not render in all terminals. It works in most modern emulators (Alacritty, Kitty, WezTerm, GNOME Terminal 3.36+).
- **Box-drawing characters** (`╔╠╚`) rely on UTF-8 locale. Verify with `echo $LANG` — should show `UTF-8`. If not: `export LANG=en_US.UTF-8`.
- **Sudo indicator** reflects cached sudo credentials, not active root shell. It will appear after running `sudo <cmd>` and disappear after the timeout (typically 15 min or on `sudo -k`).

---

## REPO STRUCTURE SUGGESTION

```
ProjectPortfolio/
└── starship/
    ├── starship.toml       # The config
    ├── README.md           # This file
    └── install.sh          # Bootstrap script
```

---

## REFERENCES

- [Starship documentation](https://starship.rs/config/)
- [Module list](https://starship.rs/config/#prompt)
- [Nerd Fonts](https://www.nerdfonts.com/)
- [Starship releases](https://github.com/starship/starship/releases)
