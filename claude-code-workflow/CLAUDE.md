# Project: API Service

## Conventions
- Python 3.11 with type hints everywhere
- All functions must have docstrings
- Use Pydantic for data models, never plain dicts
- Tests live in `tests/` mirroring the source structure

## Workflow
- The quality gate hook runs automatically after edits
- For multi-file refactors, use the `code-reviewer` subagent
- Reference the `python-style` skill for formatting decisions