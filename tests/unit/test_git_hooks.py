"""Exercise real Git hooks in isolated repositories, including index snapshots."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def command(arguments, directory, *, content=None):
    environment = dict(os.environ)
    environment["PATH"] = (
        str(Path(sys.executable).parent) + os.pathsep + environment["PATH"]
    )
    if arguments[0] == "sh" and not shutil.which("sh"):
        git = shutil.which("git")
        if git is None:
            raise FileNotFoundError("Git is required to exercise its hooks")
        git_root = Path(git).resolve().parents[1]
        shell = next(
            (
                p
                for p in (git_root / "bin/sh.exe", git_root / "usr/bin/sh.exe")
                if p.is_file()
            ),
            None,
        )
        if shell is None:
            raise FileNotFoundError("The Git for Windows shell is missing")
        environment["PATH"] = (
            str(git_root / "usr/bin") + os.pathsep + environment["PATH"]
        )
        arguments = [str(shell), *arguments[1:]]
    return subprocess.run(
        arguments,
        cwd=directory,
        env=environment,
        input=content,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def repository(tmp_path):
    command(["git", "init", "-b", "fixture"], tmp_path).check_returncode()
    for name in (".githooks", "scripts"):
        (tmp_path / name).mkdir()
    for name in ("pre-commit", "commit-msg", "pre-push"):
        shutil.copyfile(ROOT / ".githooks" / name, tmp_path / ".githooks" / name)
    shutil.copyfile(
        ROOT / "scripts/quality_gate.py", tmp_path / "scripts/quality_gate.py"
    )
    shutil.copyfile(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    return tmp_path


def test_commit_message_contract(repository):
    message = repository / "message.txt"
    message.write_text("bad\n", encoding="utf-8")
    assert (
        command(["sh", ".githooks/commit-msg", str(message)], repository).returncode
        != 0
    )
    message.write_text("fix(provider): handle a missing match\n", encoding="utf-8")
    assert (
        command(["sh", ".githooks/commit-msg", str(message)], repository).returncode
        == 0
    )


def test_empty_index_passes(repository):
    assert (
        command(
            [sys.executable, "scripts/quality_gate.py", "staged"], repository
        ).returncode
        == 0
    )


def test_staged_defect_is_not_hidden_by_a_clean_working_copy(repository):
    candidate = repository / "candidate.py"
    candidate.write_text("answer = missing_name\n", encoding="utf-8")
    command(["git", "add", "candidate.py"], repository).check_returncode()
    candidate.write_text("answer = 42\n", encoding="utf-8")
    assert (
        command(
            [sys.executable, "scripts/quality_gate.py", "staged"], repository
        ).returncode
        != 0
    )


def test_unstaged_defect_does_not_block_a_clean_staged_copy(repository):
    candidate = repository / "candidate.py"
    candidate.write_text("answer = 42\n", encoding="utf-8")
    command(["git", "add", "candidate.py"], repository).check_returncode()
    candidate.write_text("answer = missing_name\n", encoding="utf-8")
    assert (
        command(
            [sys.executable, "scripts/quality_gate.py", "staged"], repository
        ).returncode
        == 0
    )


@pytest.mark.parametrize(
    "reference", ["refs/heads/main", "refs/heads/master", "refs/tags/v1.0.0"]
)
def test_protected_destinations_are_rejected(repository, reference):
    payload = f"refs/heads/fixture {'1' * 40} {reference} {'0' * 40}\n"
    result = command(["sh", ".githooks/pre-push"], repository, content=payload)
    assert result.returncode != 0
    assert "pull request" in result.stderr
