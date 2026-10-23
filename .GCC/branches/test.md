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
