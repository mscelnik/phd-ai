
# Developer Guide (Generic, Agent-Friendly)

Purpose: concise, machine-friendly development rules for contributors and AI agents. Primary language: Python. Optional frontend: React. Data stores: files, relational DBs, document DBs, or other.

---

## Repo setup (required to comply with this guide)
- Provide these files/locations to make automated checks simple:
	- `pyproject.toml` or `requirements.txt` (Python deps)
	- `tests/` (unit + integration tests)
	- `src/` or `backend/` (Python source)
	- `frontend/` (optional React app)
	- `migrations/` or `schema/` (schema definitions & migration scripts)
	- `.env.example` (required env keys)
	- CI config (e.g. `.github/workflows/ci.yml`)
	- `Makefile` or `scripts/` with `setup`, `test`, `lint`, `format` targets
	- `pre-commit` config (recommended)

- Recommended local setup steps (agents should run these automatically):
	- Create and activate a Python virtual env: `python -m venv .venv && source .venv/bin/activate`
	- Install dependencies: `pip install -r requirements.txt` or `pip install .` (or `poetry install`)
	- If frontend exists: `cd frontend && npm install`

---

## Quick rules (agent and human friendly)
- Run tests, linters, and formatters before making changes visible (commit/PR).
- Keep commits small and focused; include a clear, single-line summary and ticket reference when available.
- Follow language conventions: Python = snake_case, Classes = PascalCase; React = camelCase for identifiers.
- Use semantic schema versioning for persisted-data changes (see Data & Schema section).

---

## How AI agents should operate (concise)
- Before editing: fetch and run `make test` or equivalent. Abort if tests fail.
- Make one logical change per branch. Run `make lint` and `make format`.
- Run unit tests covering modified modules. If schema changes are present, run migration tests.
- Produce a PR description with: summary, change-type (patch/minor/major), checklist of automated checks run, and brief risk notes.

Checklist template (machine-friendly):
```
- tests: pass
- lint/format: pass
- schema-migrations: N/A or tested
- env: matched .env.example
- summary: <one-line>
```

Before declaring a change complete, run and pass full end-to-end tests (including UI where relevant). UI verification may be automated (headless browser) or a brief manual check recorded in the PR.

---

## Branching, commits, and PRs
- Branch: `feat/<short>`, `fix/<short>`, `chore/<short>`, `docs/<short>`.
- Commit message format: `type(scope): short description` (e.g. `feat(api): add user export`).
- PR should include automated-check results and a short changelog.

---

## Testing
- Unit tests: isolate functions/modules; fast; run in CI.
- Integration/E2E: exercise real workflows (may require test DB or dockerized services).
- Coverage: aim for meaningful coverage on modified code; CI can enforce thresholds.
- Local commands (examples):
	- `make test` or `pytest tests/ -q`
	- `pytest tests/specific_test.py::test_name -q`

All changes must include passing unit tests and full end-to-end tests (including UI where relevant) before an agent (or human) declares the change complete.

## Non-breaking verification
- Compile/typing checks: run `python -m compileall src/` (or `backend/index`) and any static typing tools (mypy, pyright).
- Schema/DB: ensure migrations, seed data, and sample documents load without error before merging.
- UI smoke: for React apps run the dev server and exercise the modified UI manually or via existing automation; capture the verification status in PRs.
- Performance sanity: quick smoke load test (e.g. single request) to ensure backend compiles and responds.

---

## Linting & formatting
- Ensure PEP8 compliance (e.g. `flake8` or `ruff`) and use `black` for formatting; include `isort` where applicable. For JS/React use `prettier`/`eslint`.
- Automate with pre-commit hooks and CI lint steps.

---

## Data & schema versioning (generic)
Purpose: make schema changes discoverable, reversible, and compatible.

- Versioning model (apply to files, relational schemas, document schemas):
	- PATCH: fixes that do not change schema shape or semantics.
	- MINOR: additive, backward-compatible changes (new optional fields, new views).
	- MAJOR: breaking changes (rename/remove required fields, incompatible type changes).

- Practices:
	- Keep schema definitions in `schema/` or `migrations/`.
	- Provide migration scripts for MAJOR changes; include automated tests that exercise migrating old data to new schema.
	- Prefer additive changes and deprecation windows when possible.
	- Tag schema versions clearly (e.g. `schema/v1.2.0`) and record in a changelog.
	- Use feature flags when deploying non-backward-compatible behavior.

- Agent checklist for schema-affecting change:
	1. Identify change type (patch/minor/major).
	2. Update schema metadata/version file.
	3. Add migration script(s) if MAJOR.
	4. Add tests verifying old data can be upgraded and new data validates.

---

## Releases & tagging
- Use lightweight tags: `vX.Y.Z` for releases.
- Release notes: summary of user-visible changes and schema changes.

---

## Issue / task handling (generic)
- Categorize: bug, feat, chore, doc, incident.
- For incidents, assign severity and mitigation steps; create a follow-up task for root-cause fixes.

---

## Security & secrets
- Never commit secrets. Keep `.env.example` with placeholders.
- Use secret stores for CI and production.

---

## Minimal machine-readable PR checklist (include in PR body)
```
- Tests: [OK/FAIL]
- Lint: [OK/FAIL]
- Schema change: [none/minor/major]
- Migration scripts: [present/NA]
- Notes: <short free text>
```

Include E2E and UI verification status in every PR:
```
- E2E: [OK/FAIL]
- UI verification: [OK/NA]
```

---

## Quick command reference
```
# Install (python)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run tests
make test  # or pytest tests/

# Lint & format
make lint  # or ruff/flake8
make format  # or black/isort

# Start backend (example)
uvicorn src.main:app --reload

# Start frontend (optional)
cd frontend && npm install && npm run dev
```

---

Last updated: 2026-02-02

