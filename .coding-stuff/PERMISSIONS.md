# Permissions and activation
| Harness | Versioned configuration | Activation and limit |
| --- | --- | --- |
| Codex 0.163 | .codex/config.toml; .coding-stuff/codex-config.toml | Start with `python scripts/start_codex.py` to pass the tracked TOML as process-local native overrides. No global profile is silently overwritten. Verify the neuralbet profile after startup. Filesystem profiles cannot distinguish Git's own metadata writes from arbitrary subprocess writes. .git is writable for ordinary Git; direct edits are forbidden by instructions and command policy. |
| Claude Code | .coding-stuff/claude/settings.json | setup_workspace.py restores .claude/settings.json. Uses Read/Edit patterns: Write(path) patterns are intentionally absent because they never match. File-tool rules do not constrain arbitrary interpreter subprocesses. |
| Antigravity App 2.25 | `.coding-stuff/antigravity-app-rules-reference.json`; native project settings | Run `python scripts/apply_antigravity_permissions.py --apply` to merge this source into the registered project record and add absolute path denies to `%USERPROFILE%\.gemini\config\config.json`. The script matches this clone's actual folder and project ID, preserves other settings, and backs up both files under `%USERPROFILE%\.gemini\config\workspace_backups\`. `.git` is writable for normal commits. Read-back succeeded; runtime enforcement is still to verify. |
| Antigravity IDE 2.5.5 | `.coding-stuff/antigravity-ide.md`; shared native config | The shared absolute file denies cover the protected paths across Antigravity products. Runtime enforcement in a fresh IDE session is still to verify. |

The intended policy leaves guardrail/configuration directories readable and prohibits direct writes; this is not a claim that all four clients currently enforce it. Secrets remain confidential. The Codex profile requests read-only access outside the workspace, protecting installed binaries and user-level harness configuration when that profile is active. MCP/connectors and computer-use have separate permissions.

The tracked JSON is a portable source, not an automatically loaded profile. Run the setup script again after registering a fresh clone so it can find that clone's native project identity. Absolute shared denials limit writes only at this repository and protected harness paths. `.git` remains writable so Git can commit. Deny rules take precedence over existing shared allows. File read-back is verified; live runtime enforcement is not.
Agents may write code, run checks, commit work branches, push branches and open PRs for authorized tasks. They may not push main/master, force, bypass hooks, modify harness binaries, approve their PRs, merge or publish releases. Humans review and merge. Native permission patterns alone do not make Git branch protection unnecessary.

Sources verified 2026-10-23:
- https://learn.chatgpt.com/docs/permissions
- https://code.claude.com/docs/en/permissions
- https://antigravity.google/docs/permissions/
- https://antigravity.google/docs/settings?tab=ide
