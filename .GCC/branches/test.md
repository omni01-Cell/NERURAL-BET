# Test Execution Log
## Verification Runs
### 2026-10-23 — workspace configuration
- Initial unit suite: 4 passed, 2 UTC deprecation warnings. Replaced utcnow() with datetime.now(UTC).
- Initial hook test: 4 failed, 7 passed; Windows Git shell not on PATH. Locator now resolves Git usr/bin/sh.exe.
- Corrected suite: 11 passed in 6.42s; main/master/tags rejected; index-vs-working-copy behavior verified.
- Version script scenarios added; final combined suite pending below.
- Ruff: All checks passed!; 70 files already formatted.
- Python build: Successfully built neural_bet-0.1.0.tar.gz and neural_bet-0.1.0-py3-none-any.whl.
- pip-audit: No known vulnerabilities found.
- Workflow validator: Validation succeeded: 6 workflow(s) compliant.
- Native Codex profile: initial uv Python spawn denied; explicit runtime read grant fixed execution (output 42).
- Native sandbox: read .github/CODEOWNERS succeeded; write .github/.permission-probe refused; src/.permission-probe wrote successfully and was removed.
- GitHub: leandre755 write role verified after accepted invitation; main requires PR, one review, Code Owner review and Python CI, including administrators. Force pushes and deletion disabled.
- Independent reviewer findings: fixed Codex env glob coverage, App literal command prefixes, routed network permissions. GitHub current documentation confirms bot PR workflows wait for human approval; policy now describes that step.
- Fresh-agent bootstrap is still being verified; no success claim yet.

- Additional version tests: invalid/non-increasing versions rejected without metadata changes; higher version changes only the version.
- Fresh Codex CLI session: FAILED before instruction loading with helper_sandbox_lock_failed / NtCreateFile access denied on the installed .codex/.sandbox-bin runtime. Do not modify installed harness binaries to mask this. The native sandbox profile command probes passed separately.
- First real pre-push: unit suite passed, then Ruff rejected the temporary snapshot because Windows CRLF was translated twice. Snapshot writes now preserve original bytes. Added a real staged-CRLF regression; all 18 unit tests passed in 16.79s.
- Corrected real pre-push: 18 passed in 11.64s; Ruff check and formatting passed; audit reported no known vulnerabilities; wheel and sdist built; full gate checked 98 files. Branch published normally, without bypass flags.
- PR #1 opened: https://github.com/omni01-Cell/NERURAL-BET/pull/1. GitHub CI has no executed steps: "The job was not started because your account is locked due to a billing issue." Required CI remains enforced.
- PR discussion read in full: Greptile has no review credits; CodeRabbit skipped automatic review; Codex remote review is running. No inline review comments or submitted reviews were present at this observation.
- Final static recheck: Ruff passed, 71 files formatted, six workflows compliant. setup_workspace.py restored the updated local Claude adapter and confirmed three active hooks.
- Latest native Codex probe of the added start_codex.py protection could not execute: the same helper_sandbox_lock_failed runtime error now blocks sandbox provisioning. Earlier native probes passed; do not extrapolate them to a runtime pass for the final profile.
- Follow-up pre-push at a495fce: 18 passed in 24.96s; full gate checked 98 files; audit clean and sdist/wheel built. Branch published without bypass; local and remote work-branch SHAs matched. Main remains 9479023.
- All four initial GitHub check annotations were read and reported the same billing lock; no job started. Re-read protection via GitHub API: required CI and one Code Owner review, administrators included, force/deletion disabled.
- Remote Codex review completed with one P2: USER_GUIDE.md retained python src/tui.py after removal of the path bootstrap. Updated installation and launch instructions to python -m src.tui and documented actual keyboard shortcuts. The exact module command displayed startup; Ctrl+P opened the palette, screenshot export succeeded, Ctrl+Q exited with code 0. No provider request was submitted.
- Full code graph refreshed: quality_gate.main, setup_workspace.main, propose_version.main and start_codex.main each have an incoming module entry call. Hook and version tests exercised their real integration paths separately.
- Documentation correction 1b096f9 published after 18 tests passed in 8.43s, Ruff/format/audit/build passed and full gate checked 98 files. Remote review thread PRRT_kwDORGeUys6vvG9D was resolved, then independently fetched with is_resolved=true. No other inline findings were present. Working tree was clean after publication.
