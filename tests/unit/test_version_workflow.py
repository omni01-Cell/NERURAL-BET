"""Exercise the actual version script against isolated metadata, not this checkout."""

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "version", ["0.1.0", "0.0.1", "01.2.3", "1.2", "1; echo unsafe"]
)
def test_invalid_or_non_increasing_version_is_rejected(tmp_path, version):
    script, metadata = prepare(tmp_path)
    before = metadata.read_bytes()
    result = invoke(script, version)
    assert result.returncode != 0
    assert metadata.read_bytes() == before


def test_higher_version_updates_only_the_version(tmp_path):
    script, metadata = prepare(tmp_path)
    result = invoke(script, "0.2.0")
    assert result.returncode == 0, result.stderr
    assert tomllib.loads(metadata.read_text()) == {
        "project": {"name": "fixture", "version": "0.2.0"}
    }


def prepare(root):
    scripts = root / "scripts"
    scripts.mkdir()
    script = scripts / "propose_version.py"
    shutil.copyfile(
        Path(__file__).resolve().parents[2] / "scripts/propose_version.py", script
    )
    metadata = root / "pyproject.toml"
    metadata.write_text(
        '[project]\nname = "fixture"\nversion = "0.1.0"\n', encoding="utf-8"
    )
    return script, metadata


def invoke(script, version):
    environment = dict(os.environ, NEXT_VERSION=version)
    return subprocess.run(
        [sys.executable, str(script)],
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
    )
