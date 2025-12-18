#!/bin/bash
set -e

DIST_DIR="dist_so"
DELETED_FILES="deleted_files.txt"
BYPASS_FILES="bypass_files.txt"
DELETED_BYPASS_FILES="deleted_bypass_files.txt"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}=== Syncing to Prod Branch ===${NC}"

# Checkout prod branch
echo "Switching to prod branch..."
git fetch origin prod:prod 2>/dev/null || true
git checkout prod

# Sync compiled .so files
if [ -d "$DIST_DIR" ]; then
    echo "Copying .so files to prod branch..."
    
    # Find all .so files in dist directory
    find "$DIST_DIR" -name "*.so" | while read -r so_file; do
        # Get relative path (remove dist_so prefix)
        rel_path="${so_file#$DIST_DIR/}"
        target_dir=$(dirname "$rel_path")
        
        # Create target directory if needed
        mkdir -p "$target_dir"
        
        # Copy .so file
        cp "$so_file" "$rel_path"
        echo -e "${GREEN}  ✓ Synced: $rel_path${NC}"
    done
    
    # Copy __init__.py files (needed for package structure)
    find "$DIST_DIR" -name "__init__.py" | while read -r init_file; do
        rel_path="${init_file#$DIST_DIR/}"
        target_dir=$(dirname "$rel_path")
        mkdir -p "$target_dir"
        cp "$init_file" "$rel_path"
        echo -e "${YELLOW}  ℹ Synced: $rel_path${NC}"
    done
fi

# Sync bypass files (direct .py copy)
if [ -f "$BYPASS_FILES" ] && [ -s "$BYPASS_FILES" ]; then
    echo "Copying bypass files directly as .py..."
    
    while IFS= read -r py_file; do
        if [ -z "$py_file" ]; then
            continue
        fi
        
        # Switch back to main to get the file
        git checkout main -- "$py_file" 2>/dev/null || true
        
        if [ -f "$py_file" ]; then
            echo -e "${YELLOW}  ✓ Bypassed (copied as .py): $py_file${NC}"
        fi
    done < "$BYPASS_FILES"
fi

# Handle deleted compiled files
if [ -f "$DELETED_FILES" ] && [ -s "$DELETED_FILES" ]; then
    echo "Removing deleted compiled files from prod..."
    
    while IFS= read -r deleted_py; do
        if [ -z "$deleted_py" ]; then
            continue
        fi
        
        # Convert .py path to .so path
        so_file="${deleted_py%.py}.*.so"
        
        # Remove matching .so files
        for f in $so_file; do
            if [ -f "$f" ]; then
                git rm "$f" 2>/dev/null || rm -f "$f"
                echo -e "${YELLOW}  ✓ Removed: $f${NC}"
            fi
        done
    done < "$DELETED_FILES"
fi

# Handle deleted bypass files
if [ -f "$DELETED_BYPASS_FILES" ] && [ -s "$DELETED_BYPASS_FILES" ]; then
    echo "Removing deleted bypass files from prod..."
    
    while IFS= read -r deleted_py; do
        if [ -z "$deleted_py" ]; then
            continue
        fi
        
        if [ -f "$deleted_py" ]; then
            git rm "$deleted_py" 2>/dev/null || rm -f "$deleted_py"
            echo -e "${YELLOW}  ✓ Removed: $deleted_py${NC}"
        fi
    done < "$DELETED_BYPASS_FILES"
fi

# Clean up build artifacts
rm -rf "$DIST_DIR" build_cython changed_files.txt deleted_files.txt bypass_files.txt deleted_bypass_files.txt

echo -e "${GREEN}=== Sync Complete ===${NC}"

