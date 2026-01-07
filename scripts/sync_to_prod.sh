#!/bin/bash
set -e

DIST_DIR="dist_so"
DELETED_FILES="deleted_files.txt"
BYPASS_FILES="bypass_files.txt"
DELETED_BYPASS_FILES="deleted_bypass_files.txt"
NON_PYTHON_FILES="non_python_files.txt"
DELETED_NON_PYTHON_FILES="deleted_non_python_files.txt"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=== Syncing to Prod Branch ===${NC}"

# Checkout prod branch
echo "Switching to prod branch after stashing..."
git fetch origin prod:prod 2>/dev/null || true
git stash 
git checkout -f prod

echo -e "${GREEN}Switched to prod branch.${NC}"
git stash pop || true

# Sync compiled .so files
if [ -d "$DIST_DIR" ]; then
    echo -e "${BLUE}Copying .so files to prod branch...${NC}"
    
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
    echo -e "${BLUE}Copying bypass files directly as .py...${NC}"
    
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

# Sync non-Python files directly from main
if [ -f "$NON_PYTHON_FILES" ] && [ -s "$NON_PYTHON_FILES" ]; then
    echo -e "${BLUE}Syncing non-Python files from main...${NC}"
    
    while IFS= read -r file; do
        if [ -z "$file" ]; then
            continue
        fi
        
        # Create directory if needed
        target_dir=$(dirname "$file")
        mkdir -p "$target_dir"
        
        # Checkout file from main
        git checkout main -- "$file" 2>/dev/null || true
        
        if [ -f "$file" ]; then
            echo -e "${CYAN}  ✓ Synced: $file${NC}"
        fi
    done < "$NON_PYTHON_FILES"
fi

# Handle deleted compiled files
if [ -f "$DELETED_FILES" ] && [ -s "$DELETED_FILES" ]; then
    echo -e "${BLUE}Removing deleted compiled files from prod...${NC}"
    
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
    echo -e "${BLUE}Removing deleted bypass files from prod...${NC}"
    
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

# Handle deleted non-Python files
if [ -f "$DELETED_NON_PYTHON_FILES" ] && [ -s "$DELETED_NON_PYTHON_FILES" ]; then
    echo -e "${BLUE}Removing deleted non-Python files from prod...${NC}"
    
    while IFS= read -r deleted_file; do
        if [ -z "$deleted_file" ]; then
            continue
        fi
        
        if [ -f "$deleted_file" ]; then
            git rm "$deleted_file" 2>/dev/null || rm -f "$deleted_file"
            echo -e "${YELLOW}  ✓ Removed: $deleted_file${NC}"
        fi
    done < "$DELETED_NON_PYTHON_FILES"
fi

# Clean up build artifacts and tracking files
rm -rf "$DIST_DIR" build_cython changed_files.txt deleted_files.txt bypass_files.txt deleted_bypass_files.txt non_python_files.txt deleted_non_python_files.txt

echo -e "${GREEN}=== Sync Complete ===${NC}"