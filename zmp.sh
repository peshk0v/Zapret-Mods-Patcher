#!/bin/bash

echo ""
echo "  ===================================="
echo "    Zapret Modifications Patcher"
echo "          by peshk0v"
echo "  ===================================="
echo ""

MOD_PATH=""
ZAPRET_PATH=""

if [ -n "$1" ]; then
    MOD_PATH="$1"
    PARENT_DIR="$(cd "$(dirname "$MOD_PATH")" && pwd)"

    echo "  Archive: $MOD_PATH"
    echo ""

    ARCH_FOUND=0
    if [ -d "$PARENT_DIR/bin" ] && [ -d "$PARENT_DIR/lists" ] && [ -d "$PARENT_DIR/utils" ]; then
        ARCH_FOUND=1
    fi
    if [ "$ARCH_FOUND" -eq 0 ] && [ -d "$PARENT_DIR/src" ] && [ -d "$PARENT_DIR/custom-strategies" ] && [ -d "$PARENT_DIR/user-lists" ]; then
        ARCH_FOUND=1
    fi

    if [ "$ARCH_FOUND" -eq 1 ]; then
        ZAPRET_PATH="$PARENT_DIR"
        echo "  Found Zapret in: $ZAPRET_PATH"
    else
        SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
        SELF_FOUND=0
        if [ -d "$SELF_DIR/bin" ] && [ -d "$SELF_DIR/lists" ] && [ -d "$SELF_DIR/utils" ]; then
            SELF_FOUND=1
        fi
        if [ "$SELF_FOUND" -eq 0 ] && [ -d "$SELF_DIR/src" ] && [ -d "$SELF_DIR/custom-strategies" ] && [ -d "$SELF_DIR/user-lists" ]; then
            SELF_FOUND=1
        fi
        if [ "$SELF_FOUND" -eq 1 ]; then
            ZAPRET_PATH="$SELF_DIR"
            echo "  Found Zapret in: $ZAPRET_PATH"
        else
            echo "  Archive is not in a Zapret folder."
            echo ""
            read -rp "  Enter path to Zapret folder: " ZAPRET_PATH
        fi
    fi
else
    SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

    SELF_FOUND=0
    if [ -d "$SELF_DIR/bin" ] && [ -d "$SELF_DIR/lists" ] && [ -d "$SELF_DIR/utils" ]; then
        SELF_FOUND=1
    fi
    if [ "$SELF_FOUND" -eq 0 ] && [ -d "$SELF_DIR/src" ] && [ -d "$SELF_DIR/custom-strategies" ] && [ -d "$SELF_DIR/user-lists" ]; then
        SELF_FOUND=1
    fi

    if [ "$SELF_FOUND" -eq 1 ]; then
        ZAPRET_PATH="$SELF_DIR"
        echo "  Found Zapret in: $ZAPRET_PATH"
        echo ""
        read -rp "  Enter path to mod archive (.zip): " MOD_PATH
    else
        read -rp "  Enter path to Zapret folder: " ZAPRET_PATH
        echo ""
        read -rp "  Enter path to mod archive (.zip): " MOD_PATH
    fi
fi

echo ""

if [ -z "$ZAPRET_PATH" ]; then
    echo "  ERROR: Zapret path is empty."
    exit 1
fi
if [ -z "$MOD_PATH" ]; then
    echo "  ERROR: Mod archive path is empty."
    exit 1
fi

ZAPRET_PATH="${ZAPRET_PATH//\"/}"
MOD_PATH="${MOD_PATH//\"/}"

if [ ! -d "$ZAPRET_PATH" ]; then
    echo "  ERROR: Zapret folder not found: $ZAPRET_PATH"
    exit 1
fi
if [ ! -f "$MOD_PATH" ]; then
    echo "  ERROR: Mod archive not found: $MOD_PATH"
    exit 1
fi

ARCH=""
LISTS_DIR=""
BATS_DIR=""

if [ -d "$ZAPRET_PATH/bin" ] && [ -d "$ZAPRET_PATH/lists" ] && [ -d "$ZAPRET_PATH/utils" ]; then
    ARCH="Flowseal"
    LISTS_DIR="$ZAPRET_PATH/lists"
    BATS_DIR="$ZAPRET_PATH"
fi

if [ -z "$ARCH" ] && [ -d "$ZAPRET_PATH/src" ] && [ -d "$ZAPRET_PATH/custom-strategies" ] && [ -d "$ZAPRET_PATH/user-lists" ]; then
    ARCH="Sergeydigl3"
    LISTS_DIR="$ZAPRET_PATH/user-lists"
    BATS_DIR="$ZAPRET_PATH/custom-strategies"
fi

if [ -z "$ARCH" ]; then
    echo "  ERROR: Could not determine Zapret architecture."
    echo "  Make sure the path points to a valid Zapret installation."
    exit 1
fi

echo "  Architecture: $ARCH"
echo ""

MOD_DIR="$ZAPRET_PATH/mod"
rm -rf "$MOD_DIR"
mkdir -p "$MOD_DIR"

echo "  Extracting..."
if ! command -v unzip &> /dev/null; then
    echo "  ERROR: 'unzip' command not found. Please install unzip."
    rm -rf "$MOD_DIR"
    exit 1
fi

if ! unzip -q -o "$MOD_PATH" -d "$MOD_DIR" 2>/dev/null; then
    echo "  ERROR: Failed to extract archive."
    rm -rf "$MOD_DIR"
    exit 1
fi

echo "  Applying mod..."

find "$MOD_DIR" -type f -name "*.txt" | while IFS= read -r txt_file; do
    txt_name="$(basename "$txt_file")"
    target="$LISTS_DIR/$txt_name"
    if [ -f "$target" ]; then
        echo "    Appending: $txt_name"
        echo "" >> "$target"
        cat "$txt_file" >> "$target"
    fi
done

find "$MOD_DIR" -type f \( -name "*.bat" -o -name "*.cmd" -o -name "*.sh" \) | while IFS= read -r script_file; do
    echo "    Moving: $(basename "$script_file")"
    mv -f "$script_file" "$BATS_DIR/"
done

rm -rf "$MOD_DIR"

echo ""
echo "  ===================================="
echo "    Mod successfully installed!"
echo "    Architecture: $ARCH"
echo "    Mod: $(basename "$MOD_PATH")"
echo "  ===================================="
echo ""
