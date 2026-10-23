# Architecture
- src/cli.py: installed terminal and pipeline entry points.
- src/tui.py and src/ui/: Textual presentation and user interaction.
- src/agents/: dispatcher, data mining, statistical/tactical/context analysis and synthesis.
- src/core/: shared schemas, state, errors, model factories and provider interfaces.
- src/providers/: football statistics and news adapters; network I/O belongs here.
- tests/unit/: deterministic agent error handling; no external service.
- tests/integration/: network and model probes, selected explicitly by a maintainer.
- scripts/: workspace installation and validation commands.
- .githooks/: exactly three Git integration points.
- .github/: Python CI, dependency review, governance, triage, version workflow.
- .GCC/: versioned objectives, decisions, active plans and verification history.
- .gouvernance/: delivery and review rules shared by all harnesses.

Python 3.12; Poetry Core remains the wheel-building backend. Standard project metadata and requirements.txt declare the same pinned direct dependencies. requirements-dev.lock records the complete development resolution.
Provider calls and agent reasoning are distinct from the offline unit suite. Runtime provider compatibility is not asserted by CI alone.
