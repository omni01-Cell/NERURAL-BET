"""Validate a requested stable version before proposing a metadata-only PR."""

import os
import re
import tomllib
from pathlib import Path


def main() -> None:
    version = os.environ["NEXT_VERSION"]
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        raise ValueError("Expected a stable major.minor.patch version")
    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    current = tomllib.loads(text)["project"]["version"]
    if tuple(map(int, version.split("."))) <= tuple(map(int, current.split("."))):
        raise ValueError("The proposed version must be higher than the current one")
    previous = f'version = "{current}"'
    if text.count(previous) != 1:
        raise ValueError("Version field is ambiguous")
    path.write_text(text.replace(previous, f'version = "{version}"'), encoding="utf-8")
    print(f"Proposed version: {current} -> {version}; human merge is required")


if __name__ == "__main__":
    main()
