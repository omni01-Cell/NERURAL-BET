"""Validate committed candidates; staged mode reads the index, never working copies."""

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(arguments: list[str], *, cwd: Path | None = None) -> bytes:
    return subprocess.run(
        arguments, check=True, capture_output=True, cwd=cwd, timeout=180
    ).stdout


def main() -> int:
    scope = sys.argv[1] if len(sys.argv) == 2 else "staged"
    if scope not in {"staged", "full"}:
        raise ValueError("Expected staged or full scope")
    root = Path(run(["git", "rev-parse", "--show-toplevel"]).decode().strip())
    args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    if scope == "full":
        args = ["git", "ls-files", "-z"]
    names = [os.fsdecode(name) for name in run(args, cwd=root).split(b"\0") if name]
    if not names:
        print("Quality gate: no staged changes.")
        return 0
    patterns = (
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"\bAKIA[A-Z0-9]{16}\b",
        r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}\b",
        r"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b",
    )
    with tempfile.TemporaryDirectory(prefix="neuralbet-gate-") as temporary:
        snapshot = Path(temporary)
        python_files = []
        for name in names:
            path = Path(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe repository path")
            if (
                path.name.startswith(".env") and path.name != ".env.example"
            ) or path.suffix in {".pem", ".key"}:
                raise ValueError(f"Secret file cannot be committed: {name}")
            content = (
                run(["git", "show", f":{name}"], cwd=root)
                if scope == "staged"
                else (root / path).read_bytes()
            )
            if b"\0" in content:
                continue
            text = content.decode("utf-8-sig")
            if any(re.search(pattern, text) for pattern in patterns):
                raise ValueError(
                    f"Potential secret in {name}; value deliberately hidden"
                )
            if path.suffix == ".py":
                ast.parse(text, filename=name)
                target = snapshot / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
                python_files.append(str(target))
        if python_files:
            for operation in (["check"], ["format", "--check"]):
                command = [
                    sys.executable,
                    "-m",
                    "ruff",
                    *operation,
                    "--config",
                    str(root / "pyproject.toml"),
                    *python_files,
                ]
                subprocess.run(command, check=True, timeout=180)
    if scope == "full":
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip_audit",
                "-r",
                str(root / "requirements-dev.lock"),
                "--disable-pip",
                "--no-deps",
                "--progress-spinner",
                "off",
            ],
            cwd=root,
            check=True,
            timeout=180,
        )
        subprocess.run(
            [sys.executable, "-m", "build", "--no-isolation"],
            cwd=root,
            check=True,
            timeout=180,
        )
    print(f"Quality gate: {scope}, {len(names)} files checked.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Quality gate failed: {error}", file=sys.stderr)
        sys.exit(1)
