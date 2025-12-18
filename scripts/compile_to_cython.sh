#!/bin/bash
set -e  # Exit on error

CHANGED_FILES="changed_files.txt"
BUILD_DIR="build_cython"
DIST_DIR="dist_so"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Cython Compilation ===${NC}"

# Create output directories
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

# Check if there are files to compile
if [ ! -f "$CHANGED_FILES" ] || [ ! -s "$CHANGED_FILES" ]; then
    echo -e "${RED}No files to compile${NC}"
    exit 0
fi

# Count total files
total_files=$(wc -l < "$CHANGED_FILES")
current=0

# Compile each Python file
while IFS= read -r py_file; do
    if [ -z "$py_file" ]; then
        continue
    fi
    
    current=$((current + 1))
    echo -e "${BLUE}[$current/$total_files] Compiling: $py_file${NC}"
    
    if [ ! -f "$py_file" ]; then
        echo -e "${RED}  File not found, skipping${NC}"
        continue
    fi
    
    # Get directory structure
    dir_path=$(dirname "$py_file")
    file_name=$(basename "$py_file")
    base_name="${file_name%.py}"
    
    # Create directory in dist
    mkdir -p "$DIST_DIR/$dir_path"
    
    # Create temporary setup.py for this file
    cat > "$BUILD_DIR/setup_temp.py" << EOF
from setuptools import setup
from Cython.Build import cythonize
import os

setup(
    name='$base_name',
    ext_modules=cythonize(
        "$py_file",
        compiler_directives={
            'language_level': "3",
            'embedsignature': True,
        },
    ),
    script_args=['build_ext', '--build-lib', '$DIST_DIR/$dir_path'],
)
EOF
    
    # Run compilation
    if python3 "$BUILD_DIR/setup_temp.py" build_ext --build-lib "$DIST_DIR/$dir_path" > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Compiled successfully${NC}"
        
        # Remove generated .c file
        c_file="${py_file%.py}.c"
        if [ -f "$c_file" ]; then
            rm "$c_file"
        fi
        
        # Copy __init__.py if it exists (needed for Python packages)
        if [ "$file_name" != "__init__.py" ] && [ -f "$dir_path/__init__.py" ]; then
            cp "$dir_path/__init__.py" "$DIST_DIR/$dir_path/" 2>/dev/null || true
        fi
    else
        echo -e "${RED}  ✗ Compilation failed${NC}"
        # Clean up .c file even on failure
        c_file="${py_file%.py}.c"
        if [ -f "$c_file" ]; then
            rm "$c_file"
        fi
        # Don't exit, continue with other files
    fi
    
done < "$CHANGED_FILES"

echo -e "${GREEN}=== Compilation Complete ===${NC}"
echo "Compiled files are in: $DIST_DIR/"
