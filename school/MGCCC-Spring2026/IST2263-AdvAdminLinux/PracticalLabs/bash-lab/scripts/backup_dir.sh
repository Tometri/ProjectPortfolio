#!/bin/bash
read -p "Enter directory to back up:" SRC_DIR
if [ ! -d "$SRC_DIR" ]; then
	echo "ERROR: Directory '$SRC_DIR' does not exist."
	exit 1
fi
BACKUP_DIR="$HOME/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date)
SRC_BASENAME=$(basename "$SRC_DIR")
BACKUP_FILE="$BACKUP_DIR/${SRC_BASENAME}_${TIMESTAMP}.tar.gz"

tar -czf "$BACKUP_FILE" -C "$(dirname "$SRC_DIR")" "$SRC_BASENAME"
if [ $? -ne 0 ]; then
    echo "Backup failed."
    exit 1
fi

echo "Backup created: $BACKUP_FILE"
