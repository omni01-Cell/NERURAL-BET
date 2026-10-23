# GitHub governance
CI runs Python quality checks, offline unit tests, package construction and hook behavior checks on PRs and main. Dependency review checks changed dependencies. Workflow hygiene checks pinned Actions and basic workflow safety. PR governance checks Conventional Commit titles and subjects, reports changed protected paths, and requests human review. Issue triage uses the issue templates.
The version workflow accepts a semantic version after manual maintainer dispatch and opens a version-bump pull request; it never pushes main or publishes a tag.
The repository allows GitHub Actions to create pull requests, which this version workflow requires. Default workflow permissions remain read-only; only its version job requests scoped write access. GitHub groups PR creation and approval under one repository setting, but the workflow never submits approvals and cannot satisfy the named human Code Owner requirement.
CODEOWNERS lists both named maintainers. Effective server enforcement requires a GitHub ruleset requiring pull requests and relevant checks. A local pre-push hook is a development guard, not a remote access control.
ANTIBUG and scheduled AI audits are intentionally absent.

For version PRs created with GITHUB_TOKEN, GitHub queues pull_request workflows for human approval. Approve those runs in the PR banner. CI is also dispatched explicitly by the version workflow. This is an intentional human review step; no secondary check is claimed to have run before approval.

