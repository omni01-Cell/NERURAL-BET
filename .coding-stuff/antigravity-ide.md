# Antigravity IDE 2.5.5
No repository-local permissions JSON loader is verified for this IDE or for the Antigravity App. App settings must not be confused with automatic loading of files tracked in Git.
Use workspace instructions in .agents/rules/neuralbet.md as agent guidance. Configure terminal review manually in the IDE for operations that require review. This does not enforce read-only access to protected paths.
The non-workspace file access switch affects both viewing and editing external files. Disabling it would also restrict reading, so it does not implement the maintainer's write-only restriction. Do not present that switch as a selective write block or change it on that basis.
Do not enable Turbo/full-filesystem access to avoid prompts. Do not claim these instructions enforce read-only policy directories against arbitrary shell subprocesses on Windows.
Use the same protected paths listed in AGENTS.md, and the Git hooks for main-push prevention. These controls are weaker than an OS-level read-only mount; verify settings in the IDE before claiming activation.
Official reference: https://antigravity.google/docs/settings?tab=ide
