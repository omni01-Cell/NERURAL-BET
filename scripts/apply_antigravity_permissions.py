"""Merge the tracked Antigravity policy into this clone's native project grants."""

import argparse
import copy
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse


def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def normalize_uri(uri: str) -> str:
    parsed = urlparse(unquote(uri))
    return f"{parsed.netloc}{parsed.path}".replace("\\", "/").rstrip("/").casefold()


def load_project(projects_dir: Path, root: Path) -> tuple[Path, dict]:
    matching = []
    for path in sorted(projects_dir.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8-sig"))
        resources = record.get("projectResources", {}).get("resources", [])
        if any(
            normalize_uri(folder.get("folderUri", "")) == normalize_uri(root.as_uri())
            for resource in resources
            if isinstance(resource, dict)
            and isinstance((folder := resource.get("gitFolder")), dict)
        ):
            matching.append((path, record))
    if len(matching) != 1:
        raise ValueError(
            f"Expected one Antigravity project for this checkout, found {len(matching)}"
        )
    path, record = matching[0]
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise ValueError("Registered Antigravity project has no ID")
    return path, record


def merge(existing: object, additions: list[str]) -> list[str]:
    if not isinstance(existing, list) or not all(
        isinstance(rule, str) for rule in existing
    ):
        raise ValueError("Existing permission lists must contain strings")
    result = list(existing)
    for rule in additions:
        if rule not in result:
            result.append(rule)
    return result


def write_atomic(path: Path, content: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".antigravity-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_source(root: Path) -> dict:
    path = root / ".coding-stuff/antigravity-app-rules-reference.json"
    policy = json.loads(path.read_text(encoding="utf-8-sig"))["permissions"]
    if set(policy) != {"allow", "ask", "deny"}:
        raise ValueError("Permission reference has unexpected access lists")
    for rules in policy.values():
        if not isinstance(rules, list) or not all(
            isinstance(rule, str) and rule for rule in rules
        ):
            raise ValueError("Permission reference must contain nonempty strings")
    if any("write_file(.git/" in rule for rule in policy["deny"]):
        raise ValueError(".git/ must remain writable for ordinary Git operations")
    return policy


def global_file_guards(policy: dict, root: Path) -> list[str]:
    guards = []
    for rule in policy["deny"]:
        match = re.fullmatch(r"(write_file|read_file)\((.+)\)", rule)
        if match is None:
            continue
        action, target = match.groups()
        if not target.startswith("/"):
            target = (root / target).as_posix()
            target = re.sub(r"^[A-Za-z]:", "", target)
        guards.append(f"{action}({target})")
    return guards


def prepare(root: Path) -> tuple[list[tuple[Path, bytes, bytes]], dict]:
    root = root.resolve()
    config = Path.home() / ".gemini/config"
    shared_path = config / "config.json"
    project_path, project = load_project(config / "projects", root)
    policy = load_source(root)
    original_shared = shared_path.read_bytes()
    original_project = project_path.read_bytes()
    shared = json.loads(original_shared.decode("utf-8-sig"))
    shared_before = copy.deepcopy(shared)
    project_before = copy.deepcopy(project)
    project_grants = project.setdefault("permissionGrants", {}).setdefault(
        "permissionGrants", {}
    )
    for access, rules in policy.items():
        project_grants[access] = merge(project_grants.get(access, []), rules)
    project_compare = copy.deepcopy(project)
    project_compare.pop("permissionGrants", None)
    project_before.pop("permissionGrants", None)
    if project_compare != project_before:
        raise ValueError("An unrelated project field changed")
    user_settings = shared.setdefault("userSettings", {})
    global_grants = user_settings.setdefault("globalPermissionGrants", {})
    global_grants["deny"] = merge(
        global_grants.get("deny", []), global_file_guards(policy, root)
    )
    shared_compare = copy.deepcopy(shared)
    shared_compare["userSettings"].pop("globalPermissionGrants", None)
    shared_before["userSettings"].pop("globalPermissionGrants", None)
    if shared_compare != shared_before:
        raise ValueError("An unrelated shared setting changed")
    changes = [
        (shared_path, original_shared, encode(shared)),
        (project_path, original_project, encode(project)),
    ]
    summary = {
        "project_id": project["id"],
        "project_policy_counts": {
            access: len(project_grants[access]) for access in ("allow", "ask", "deny")
        },
        "absolute_shared_file_guards": len(global_grants["deny"])
        - len(
            shared_before["userSettings"]
            .get("globalPermissionGrants", {})
            .get("deny", [])
        ),
        "existing_shared_allow_rules": len(global_grants.get("allow", [])),
        "git_metadata_writable": True,
        "runtime_enforcement_tested": False,
    }
    return changes, summary


def apply(changes: list[tuple[Path, bytes, bytes]]) -> Path:
    backup = (
        Path.home()
        / ".gemini"
        / "config"
        / "workspace_backups"
        / ("antigravity-backup-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
    )
    backup.mkdir(parents=True, exist_ok=False)
    for path, original, _ in changes:
        (backup / (path.parent.name + "-" + path.name)).write_bytes(original)
    written = []
    try:
        for path, original, replacement in changes:
            if path.read_bytes() != original:
                raise ValueError(
                    "Antigravity settings changed during preparation; rerun safely"
                )
            write_atomic(path, replacement)
            written.append((path, original, replacement))
        for path, _, replacement in written:
            if path.read_bytes() != replacement:
                raise ValueError(f"Native settings read-back failed: {path.name}")
    except Exception:
        for path, original, replacement in reversed(written):
            if path.read_bytes() == replacement:
                write_atomic(path, original)
        raise
    return backup


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Merge into this user's Antigravity configuration",
    )
    arguments = parser.parse_args()
    changes, summary = prepare(root)
    if arguments.apply:
        summary["backup"] = str(apply(changes))
        summary["mode"] = "applied"
    else:
        summary["mode"] = "dry-run"
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
