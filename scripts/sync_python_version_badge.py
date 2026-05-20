#!/usr/bin/env python3
"""Sync the Python version badge in README.md with pyproject.toml.

Badge format: python-X.Y%2B-blue  (shields.io URL-encoded '+')
pyproject.toml format: requires-python = ">=X.Y"

Exits 0 if nothing changed, 1 if the README was updated (so pre-commit
fails and forces the user to `git add README.md` before committing again).
"""
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).parent.parent

    # --- pyproject.toml -------------------------------------------------
    pyproject = (root / "pyproject.toml").read_text()
    m = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)"', pyproject)
    if not m:
        print("ERROR: Could not find `requires-python = \">=X.Y\"` in pyproject.toml")
        return 1
    toml_version = m.group(1)  # e.g. "3.9"

    # --- README.md badge -------------------------------------------------
    readme_path = root / "README.md"
    readme = readme_path.read_text()
    # Matches both URL-encoded (%2B) and literal (+) forms
    if not re.search(r"python-\d+\.\d+(?:%2B|\+)-blue", readme):
        print("ERROR: Could not find Python version badge in README.md")
        print("       Expected pattern: python-X.Y%2B-blue")
        return 1

    # --- Auto-fix --------------------------------------------------------
    new_readme = re.sub(
        r"(python-)(\d+\.\d+)((?:%2B|\+)-blue)",
        lambda mo: f"{mo.group(1)}{toml_version}{mo.group(3)}",
        readme,
    )

    if new_readme == readme:
        print(f"OK: Python version consistent ({toml_version}+)")
        return 0

    # Extract old version for the message
    old_version = re.search(r"python-(\d+\.\d+)(?:%2B|\+)-blue", readme).group(1)
    readme_path.write_text(new_readme)
    print(f"FIXED: README.md badge updated {old_version}+ → {toml_version}+")
    print("       Please `git add README.md` and commit again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
