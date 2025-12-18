# CI Scripts - Cython Sync Workflow

This repository contains reusable CI/CD scripts for automatically compiling Python files to Cython `.so` files and syncing them to a production branch.

## Features

- 🔍 Automatically detects changed Python files between branches
- 🔨 Compiles Python files to Cython `.so` files for performance and obfuscation
- 🔄 Syncs compiled files to production branch
- 🚫 **Exclusion support** - Skip specific files/directories from compilation and sync
- 🧹 Handles deleted files cleanup

## Usage

### GitHub Workflow Integration

Use this as a reusable workflow in your repository:

```yaml
name: Cython Sync

on:
  push:
    branches:
      - main

jobs:
  sync:
    uses: orangewood-co/ci-scripts/.github/workflows/cython-sync.yml@main
    secrets:
      PAT_TOKEN: ${{ secrets.PAT_TOKEN }}
    with:
      python-version: '3.10'
      prod-branch: 'prod'
```

### Excluding Files from Compilation

Create a `.cythonignore` file in the **root of your repository** (the one using this workflow) to specify which files should NOT be compiled or synced to prod.

#### Creating `.cythonignore`

```bash
# In your project repository (not in ci-scripts)
touch .cythonignore
```

#### `.cythonignore` Syntax

The file supports multiple pattern types:

**Exact file paths:**
```
setup.py
config/settings.py
```

**Wildcard patterns:**
```
test_*.py          # All files starting with test_
*_test.py          # All files ending with _test.py
```

**Directory patterns:**
```
tests/             # Exclude entire tests directory
examples/          # Exclude entire examples directory
scripts/           # Exclude entire scripts directory
```

**Comments and blank lines:**
```
# This is a comment
                   # Blank lines are ignored
```

#### Example `.cythonignore`

```
# Configuration files
setup.py
config.py

# Test files
test_*.py
tests/
conftest.py

# Examples and demos
examples/
demo_*.py
example_*.py

# Development scripts
scripts/dev_*.py
tools/
```

#### How It Works

1. When the workflow runs, it checks for a `.cythonignore` file in your repository root
2. Any files matching the patterns are excluded from:
   - Cython compilation
   - Syncing to the prod branch
3. Excluded files remain as regular `.py` files in the prod branch (if they exist)

### Example Scenarios

**Scenario 1: Exclude test files**
```
# .cythonignore
test_*.py
tests/
```
Result: Test files stay as `.py` in prod, not compiled to `.so`

**Scenario 2: Exclude configuration and setup**
```
# .cythonignore
setup.py
config/*.py
```
Result: Setup and config files remain editable in prod

**Scenario 3: Exclude entire directories**
```
# .cythonignore
examples/
docs/
scripts/
```
Result: These directories are completely skipped from Cython compilation

## Requirements

- Python 3.8+
- Cython
- Git repository with `main` and `prod` branches

## Scripts

- `detect_changes.py` - Detects changed/deleted Python files and applies exclusions
- `compile_to_cython.sh` - Compiles Python files to Cython `.so` files
- `sync_to_prod.sh` - Syncs compiled files to production branch

## License

MIT License
