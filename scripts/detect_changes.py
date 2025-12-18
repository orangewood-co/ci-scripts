#!/usr/bin/env python3
import subprocess
import os
import fnmatch


def run_git_command(cmd):
    """Run git command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def load_exclusion_patterns(ignore_file='.cythonignore'):
    """Load exclusion patterns from .cythonignore file.
    Supports:
    - Exact file paths: path/to/file.py
    - Wildcard patterns: *.py, test_*.py
    - Directory patterns: tests/, **/__pycache__/
    - Comments: lines starting with #
    """
    patterns = []

    if not os.path.exists(ignore_file):
        return patterns

    with open(ignore_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                patterns.append(line)
    if patterns:
        print(f"Loaded {len(patterns)} exclusion pattern(s) from {ignore_file}")
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
    """Get list of changed .py files between prod and main."""
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
    # Load exclusion patterns
    exclusion_patterns = load_exclusion_patterns()
    # Apply exclusions
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
    return changed_files, deleted_files


def main():
    changed, deleted = get_changed_files()
    # Write changed files to output
    with open('changed_files.txt', 'w') as f:
        f.write('\n'.join(changed))
    # Write deleted files to output
    with open('deleted_files.txt', 'w') as f:
        f.write('\n'.join(deleted))
    print(f"Changed/Added: {len(changed)} files")
    print(f"Deleted: {len(deleted)} files")
    if changed:
        print("\nFiles to compile:")
        for f in changed:
            print(f"  - {f}")
    if deleted:
        print("\nFiles to remove from prod:")
        for f in deleted:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
