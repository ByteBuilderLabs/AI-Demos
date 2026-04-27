---
name: python-style
description: Python formatting and style conventions for this project. Use when writing, editing, or reviewing Python code.
---

# Python Style Guide

## Type Hints
- Every function parameter and return type must be annotated
- Use `from __future__ import annotations` for forward refs
- Prefer `list[str]` over `List[str]` (PEP 585)

## Error Handling
- Never use bare `except:` clauses
- Catch specific exceptions or `Exception` with logging
- Re-raise with `raise ... from e` to preserve traceback