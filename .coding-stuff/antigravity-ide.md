# Antigravity IDE 2.5.5
This IDE does not document a project-local permissions JSON equivalent to the Antigravity App.
Use workspace instructions in .agents/rules/neuralbet.md. In IDE settings keep non-workspace agent file access disabled and terminal review enabled, allowing the documented project checks and work-branch Git commands.
Do not enable Turbo/full-filesystem access to avoid prompts. Do not claim these instructions enforce read-only policy directories against arbitrary shell subprocesses on Windows.
Use the same protected paths listed in AGENTS.md, and the Git hooks for main-push prevention. These controls are weaker than an OS-level read-only mount; verify settings in the IDE before claiming activation.
Official reference: https://antigravity.google/docs/settings?tab=ide
