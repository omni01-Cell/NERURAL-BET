# Execution Plan: workspace configuration
## 📋 Target Invariant & Pre-requisites
Preserve application behavior and secret confidentiality; protect instructions/configuration from direct writes while allowing routine implementation and work-branch PR delivery.
## 🛠️ Step-by-Step Sequence
1. Configure Python metadata, tests and three hooks -> verify: offline tests, lint, staged-snapshot and pre-push rejection scenarios.
2. Configure versioned instructions and four harness adapters -> verify: parsing, official schema checks and fresh-agent bootstrap where executable.
3. Configure GitHub delivery -> verify: CODEOWNERS, version workflow, remote PR checks and no main push.
## Verification Proof
Local outputs after the CRLF fix:
```text
18 passed in 11.64s
All checks passed!
42 files already formatted
No known vulnerabilities found
Successfully built neural_bet-0.1.0.tar.gz and neural_bet-0.1.0-py3-none-any.whl
Quality gate: full, 98 files checked.
Validation succeeded: 6 workflow(s) compliant.
```
PR #1 is open. All four GitHub job annotations report:
```text
The job was not started because your account is locked due to a billing issue.
```
Native Codex permission probes passed separately; fresh Codex startup failed before instruction loading. Claude and Antigravity client activation remains unverified. Full observations are in test.md. Keep this plan active.
## ⚠️ Mitigations & Edge Cases
Profiles are not interchangeable. Windows IDE controls and unavailable harness executables must be reported explicitly. Keep this plan active until human confirmation.
