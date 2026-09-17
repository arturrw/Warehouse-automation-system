# Contributing

Thanks for taking a look at the Warehouse Automation System. This started as a
university UX/UI course project, so the codebase is intentionally small and
readable — please keep contributions in that spirit.

## Getting set up

```bash
git clone https://github.com/arturrw/Warehouse-automation-system.git
cd Warehouse-automation-system
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python main.py
```

Python 3.10+ is required. See [README.md](README.md) for default login
credentials and a tour of the roles.

## Project layout

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before making structural
changes. In short:

- `warehouse_system/data/` — SQLite access and dataclasses. No PyQt6 imports.
- `warehouse_system/domain/` — role/permission rules. No PyQt6 or SQL imports.
- `warehouse_system/ui/` — PyQt6 windows and pages. No raw SQL.

Keep new code on the correct side of those boundaries — it's what keeps
`tests/test_db_manager.py` able to run without a display.

## Making a change

1. Open an issue or comment on an existing one before starting non-trivial work,
   so effort isn't duplicated.
2. Create a branch off `main`: `git checkout -b feature/short-description`.
3. Keep commits focused; write messages that explain *why*, not just *what*.
4. Match the existing style:
   - Type-hint public method signatures.
   - Docstrings only where behavior isn't obvious from the name.
   - UI pages stay dumb — persistence and rules belong in `data/` or `domain/`.
5. Run the test suite and, if you touched a page, launch the app and click
   through the affected screen(s) manually (PyQt6 UI logic isn't covered by
   automated tests yet).

## Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests target `DatabaseManager` against an in-memory SQLite database (see the
`db` fixture in `tests/test_db_manager.py`). If you add a method to
`DatabaseManager` or a rule to `role_policy`, add a test alongside the existing
ones rather than a new file, unless you're covering a new module.

## Pull requests

- Describe what changed and why in the PR description; link the issue if there
  is one.
- Make sure `python -m pytest tests/ -v` passes.
- Keep the diff scoped to the change described — unrelated formatting or
  refactors make review harder and belong in a separate PR.
- Update [README.md](README.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) or
  [docs/API.md](docs/API.md) if the change affects setup, structure, or the
  `DatabaseManager` interface.

## Reporting bugs

Open a GitHub issue with: steps to reproduce, what you expected, what actually
happened, and your OS/Python version. Screenshots help a lot for UI issues.
