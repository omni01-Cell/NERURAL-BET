# Permissions and activation
| Harness | Versioned configuration | Activation and limit |
| --- | --- | --- |
| Codex 0.163 | .codex/config.toml; .coding-stuff/codex-config.toml | Start with `python scripts/start_codex.py` to pass the tracked TOML as process-local native overrides. No global profile is silently overwritten. Verify the neuralbet profile after startup. Filesystem profiles cannot distinguish Git's own metadata writes from arbitrary subprocess writes. .git is writable for ordinary Git; direct edits are forbidden by instructions and command policy. |
| Claude Code | .coding-stuff/claude/settings.json | setup_workspace.py restores .claude/settings.json. Uses Read/Edit patterns: Write(path) patterns are intentionally absent because they never match. File-tool rules do not constrain arbitrary interpreter subprocesses. |
| Antigravity App 2.25 | .coding-stuff/antigravity-app-rules-reference.json | Manual reference only, not a native repository configuration or a verified import format. The App documentation describes permissions entered in application/project settings; it does not document automatic loading of this file or JSON import. Configure supported rules manually in the client. command(prefix) is literal, not an implicit regex. No App permission activation has been verified. |
| Antigravity IDE 2.5.5 | .coding-stuff/antigravity-ide.md and versioned rule template | Configure IDE settings through its UI. No fabricated project JSON is advertised as an enforced filesystem permission profile. |

The intended policy leaves guardrail/configuration directories readable and prohibits direct writes; this is not a claim that all four clients currently enforce it. Secrets remain confidential. The Codex profile requests read-only access outside the workspace, protecting installed binaries and user-level harness configuration when that profile is active. MCP/connectors and computer-use have separate permissions.

Neither Antigravity App nor IDE has a verified repository-local permission loader in this setup. The workspace instruction rule is guidance, not a filesystem permission engine. App project settings are distinct from files tracked in Git; cloning the reference JSON does not apply permissions. The maintainer chose to configure the clients manually; no desktop control or application settings change is pending from the agent.
Agents may write code, run checks, commit work branches, push branches and open PRs for authorized tasks. They may not push main/master, force, bypass hooks, modify harness binaries, approve their PRs, merge or publish releases. Humans review and merge. Native permission patterns alone do not make Git branch protection unnecessary.

Sources verified 2026-10-23:
- https://learn.chatgpt.com/docs/permissions
- https://code.claude.com/docs/en/permissions
- https://antigravity.google/docs/permissions/
- https://antigravity.google/docs/settings?tab=ide
