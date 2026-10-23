"""Restore local adapters and activate versioned Git hooks after a clone."""

import shutil
import subprocess
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    if Path(result.stdout.strip()).resolve() != root:
        raise ValueError("Run setup in the actual repository checkout")
    for hook in ("pre-commit", "commit-msg", "pre-push"):
        path = root / ".githooks" / hook
        if not path.is_file():
            raise FileNotFoundError(path)
        path.chmod(path.stat().st_mode | 0o111)
    for source, destination in (
        (".coding-stuff/claude/settings.json", ".claude/settings.json"),
        (".coding-stuff/antigravity-rule.md", ".agents/rules/neuralbet.md"),
    ):
        target = root / destination
        content = (root / source).read_bytes()
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f"Existing local adapter differs: {destination}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(root / source, target)
    subprocess.run(
        ["git", "config", "--local", "core.hooksPath", ".githooks"],
        cwd=root,
        check=True,
        timeout=15,
    )
    print(
        "Three Git hooks active; local client adapters restored. See .coding-stuff/PERMISSIONS.md."
    )


if __name__ == "__main__":
    main()
