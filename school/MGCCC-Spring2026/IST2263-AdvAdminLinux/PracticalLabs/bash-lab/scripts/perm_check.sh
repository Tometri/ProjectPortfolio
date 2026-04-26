#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 DIRECTORY_PATH"
    exit 1
fi
DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "Error: '$DIR' is not a directory."
    exit 1
fi
for ITEM in "$DIR"/*; do
    echo "Checking: $ITEM"
done
for ITEM in "$DIR"/*; do
    # Skip if glob didn't match anything
    [ ! -e "$ITEM" ] && continue

    echo "Item: $ITEM"

    if [ -r "$ITEM" ]; then
        echo "  readable: yes"
    else
        echo "  readable: no"
    fi

    if [ -w "$ITEM" ]; then
        echo "  writable: yes"
    else
        echo "  writable: no"
    fi

    if [ -x "$ITEM" ]; then
        echo "  executable: yes"
    else
        echo "  executable: no"
    fi

    echo
done
