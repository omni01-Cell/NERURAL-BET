# Neural Bet
Football analysis using several AI agents, Understat/FBRef data and a Textual terminal interface.

## Development
Python 3.12 and Git are required. From the repository root:
```sh
python -m venv .venv
# Windows: .venv/Scripts/python.exe ; Linux: .venv/bin/python
python -m pip install -e ".[dev]"
python scripts/setup_workspace.py
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m src.tui
```
Use the virtual environment's Python for every command (or activate it first).
The setup command activates the three versioned Git hooks and installs the tracked Claude/Antigravity instruction adapters locally.
The .GCC directory is tracked: read its state before working and record factual verification results at handoff.

## External analysis
The full pipeline requires MISTRAL_API_KEY, GROQ_API_KEY and FIREWORKS_API_KEY supplied by the user outside Git. NEWS_API_KEY is optional. Never commit or read real credentials through an agent.
The default unit tests run offline; tests/integration contains manually selected network/provider probes and is excluded from the ordinary test command.
The analysis providers and model availability require a separate end-to-end verification with user-supplied access. An interface startup is not proof of correct predictions.

## Contribution
Create a work branch, run the checks, commit with Conventional Commits and open a pull request. Direct pushes to main/master and tags are rejected by the local pre-push hook. Humans review and merge. Both maintainers are in .github/CODEOWNERS.
See ARCHITECTURE.md and .coding-stuff/PERMISSIONS.md for the exact boundaries of each harness.
