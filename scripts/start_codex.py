"""Launch Codex with the versioned profile as explicit process-local overrides."""

import json
import subprocess
import sys
import tomllib
from pathlib import Path


def literal(value):
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(
                json.dumps(key) + "=" + literal(item) for key, item in value.items()
            )
            + "}"
        )
    if isinstance(value, bool):
        return str(value).lower()
    return json.dumps(value)


def main():
    root = Path(__file__).resolve().parents[1]
    profile = tomllib.loads(
        (root / ".coding-stuff/codex-config.toml").read_text(encoding="utf-8")
    )
    command = ["codex", "-C", str(root)]
    for key, value in profile.items():
        command.extend(["-c", key + "=" + literal(value)])
    command.extend(sys.argv[1:])
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL if "exec" in sys.argv[1:] else None,
        check=False,
        timeout=28800,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
