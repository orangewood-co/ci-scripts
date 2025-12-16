#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def run_git_command(cmd):
    """Run git command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

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
#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def run_git_command(cmd):
    """Run git command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

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
