#!/usr/bin/env python3
import subprocess
import os
import fnmatch


def run_git_command(cmd):
    """Run git command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def load_patterns_from_file(file_path):
    """Load patterns from a file.
    Supports:
    - Exact file paths: path/to/file.py
    - Wildcard patterns: *.py, test_*.py
    - Directory patterns: tests/, **/__pycache__/
    - Comments: lines starting with #
    """
    patterns = []

    if not os.path.exists(file_path):
        return patterns

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                patterns.append(line)
    return patterns


def load_exclusion_patterns(ignore_file='.cythonignore'):
    """Load exclusion patterns from .cythonignore file."""
    patterns = load_patterns_from_file(ignore_file)
    if patterns:
        print(f"Loaded {len(patterns)} exclusion pattern(s) from {ignore_file}")
    return patterns


def load_bypass_patterns(bypass_file='.bypass'):
    """Load bypass patterns from .bypass file."""
    patterns = load_patterns_from_file(bypass_file)
    if patterns:
        print(f"Loaded {len(patterns)} bypass pattern(s) from {bypass_file}")
    return patterns


def is_excluded(file_path, patterns):
    """Check if file matches any exclusion pattern."""
    for pattern in patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            if file_path.startswith(pattern) or f"/{pattern}" in file_path:
                return True
        # Handle glob patterns
        elif fnmatch.fnmatch(file_path, pattern):
            return True
        # Handle exact match
        elif file_path == pattern:
            return True
    return False

def get_changed_files():
    """Get list of changed .py files between prod and main.
    Returns: (files_to_compile, files_to_bypass, deleted_files_compiled, deleted_files_bypass)
    """
    # Fetch latest prod branch
    subprocess.run("git fetch origin prod:prod", shell=True)
    # Get added/modified Python files
    changed_cmd = "git diff --name-only --diff-filter=AM origin/prod...HEAD -- '*.py'"
    changed_files = run_git_command(changed_cmd).split('\n')
    # Get deleted Python files
    deleted_cmd = "git diff --name-only --diff-filter=D origin/prod...HEAD -- '*.py'"
    deleted_files = run_git_command(deleted_cmd).split('\n')
    # Filter out empty strings
    changed_files = [f for f in changed_files if f]
    deleted_files = [f for f in deleted_files if f]
    
    # Load exclusion and bypass patterns
    exclusion_patterns = load_exclusion_patterns()
    bypass_patterns = load_bypass_patterns()
    
    # Apply exclusions first
    if exclusion_patterns:
        original_changed = len(changed_files)
        original_deleted = len(deleted_files)
        changed_files = [f for f in changed_files if not is_excluded(f, exclusion_patterns)]
        deleted_files = [f for f in deleted_files if not is_excluded(f, exclusion_patterns)]    
        excluded_changed = original_changed - len(changed_files)
        excluded_deleted = original_deleted - len(deleted_files)
        if excluded_changed > 0:
            print(f"Excluded {excluded_changed} changed file(s) based on .cythonignore")
        if excluded_deleted > 0:
            print(f"Excluded {excluded_deleted} deleted file(s) based on .cythonignore")
    
    # Separate files into bypass and compile lists
    files_to_compile = []
    files_to_bypass = []
    deleted_files_compiled = []
    deleted_files_bypass = []
    
    for f in changed_files:
        if bypass_patterns and is_excluded(f, bypass_patterns):
            files_to_bypass.append(f)
        else:
            files_to_compile.append(f)
    
    for f in deleted_files:
        if bypass_patterns and is_excluded(f, bypass_patterns):
            deleted_files_bypass.append(f)
        else:
            deleted_files_compiled.append(f)
    
    if files_to_bypass:
        print(f"Bypassing Cython for {len(files_to_bypass)} file(s) - will sync as .py")
    
    return files_to_compile, files_to_bypass, deleted_files_compiled, deleted_files_bypass


def main():
    files_to_compile, files_to_bypass, deleted_compiled, deleted_bypass = get_changed_files()
    
    # Write files to compile
    with open('changed_files.txt', 'w') as f:
        f.write('\n'.join(files_to_compile))
    
    # Write files to bypass (sync as .py)
    with open('bypass_files.txt', 'w') as f:
        f.write('\n'.join(files_to_bypass))
    
    # Write deleted compiled files
    with open('deleted_files.txt', 'w') as f:
        f.write('\n'.join(deleted_compiled))
    
    # Write deleted bypass files
    with open('deleted_bypass_files.txt', 'w') as f:
        f.write('\n'.join(deleted_bypass))
    
    print(f"Files to compile: {len(files_to_compile)}")
    print(f"Files to bypass (sync as .py): {len(files_to_bypass)}")
    print(f"Deleted compiled files: {len(deleted_compiled)}")
    print(f"Deleted bypass files: {len(deleted_bypass)}")
    
    if files_to_compile:
        print("\nFiles to compile:")
        for f in files_to_compile:
            print(f"  - {f}")
    
    if files_to_bypass:
        print("\nFiles to bypass (will sync as .py):")
        for f in files_to_bypass:
            print(f"  - {f}")
    
    if deleted_compiled:
        print("\nCompiled files to remove from prod:")
        for f in deleted_compiled:
            print(f"  - {f}")
    
    if deleted_bypass:
        print("\nBypass files to remove from prod:")
        for f in deleted_bypass:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
