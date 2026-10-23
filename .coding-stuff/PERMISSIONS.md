# Permissions and activation
| Harness | Versioned configuration | Activation and limit |
| --- | --- | --- |
| Codex 0.163 | .codex/config.toml; .coding-stuff/codex-config.toml | Start with `python scripts/start_codex.py` to pass the tracked TOML as process-local native overrides. No global profile is silently overwritten. Verify the neuralbet profile after startup. Filesystem profiles cannot distinguish Git's own metadata writes from arbitrary subprocess writes. .git is writable for ordinary Git; direct edits are forbidden by instructions and command policy. |
| Claude Code | .coding-stuff/claude/settings.json | setup_workspace.py restores .claude/settings.json. Uses Read/Edit patterns: Write(path) patterns are intentionally absent because they never match. File-tool rules do not constrain arbitrary interpreter subprocesses. |
| Antigravity App 2.25 | .coding-stuff/antigravity-app-permissions.json | Import the permissions object through project settings, preset Default. command(prefix) is a literal token prefix in this version, not an implicit regex. An import file is not an activated policy. |
| Antigravity IDE 2.5.5 | .coding-stuff/antigravity-ide.md and versioned rule template | Configure IDE settings through its UI. No fabricated project JSON is advertised as an enforced filesystem permission profile. |

All guardrail/configuration directories are readable and not directly writable. Secrets remain confidential. The default external filesystem is read-only under the Codex workspace sandbox, protecting installed binaries and user-level harness configuration. MCP/connectors and computer-use have separate permissions.
Agents may write code, run checks, commit work branches, push branches and open PRs for authorized tasks. They may not push main/master, force, bypass hooks, modify harness binaries, approve their PRs, merge or publish releases. Humans review and merge. Native permission patterns alone do not make Git branch protection unnecessary.

Sources verified 2026-10-23:
- https://learn.chatgpt.com/docs/permissions
- https://code.claude.com/docs/en/permissions
- https://antigravity.google/docs/permissions/
- https://antigravity.google/docs/settings?tab=ide
