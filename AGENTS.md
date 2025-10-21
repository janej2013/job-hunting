# Repository Guidelines

## Project Structure & Module Organization
The repository root currently contains only `README.md`; keep new code easy to locate as the tree grows. Create an `agents/` package for production-ready agents (one module per agent), `lib/` for reusable tools or API integrations, `prompts/` for prompt templates tied to agents, `data/` for seed datasets or evaluation fixtures, and `assets/` for static collateral such as diagrams or mock UI flows. Keep experimental notebooks inside `experiments/` and commit only lightweight artifacts. Place unit and integration tests in `tests/`, mirroring the package structure they cover.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: standardize on an isolated Python 3.11 environment.
- `pip install -r requirements.txt`: install runtime and dev dependencies; update it whenever packages change.
- `python -m agents.cli --help`: smoke-check that the CLI entry point enumerates available agents.
- `pytest`: run the full test suite; add `-k` selectors for focused work.
- `ruff format && ruff check`: format and lint the codebase before opening a pull request.

## Coding Style & Naming Conventions
Use four-space indentation, type annotations for public callables, and snake_case for modules, files, and functions. Class names should remain in PascalCase and agent identifiers should match their module name (for example, `agents/networking_agent.py` exposes `NetworkingAgent`). Limit functions to focused responsibilities and extract helpers into `lib/` when reuse is expected. Prefer dataclasses to bare dictionaries for structured data.

## Testing Guidelines
Rely on `pytest` with fixtures housed in `tests/conftest.py`. Name test files `test_<topic>.py` and individual tests `test_<behavior>`. Write fast unit tests for each agent tool and at least one integration test that exercises the agent loop with stubbed external services. Target ≥85% branch coverage and document gaps in the pull request description.

## Commit & Pull Request Guidelines
There is no commit history yet; adopt Conventional Commits (for example, `feat: add networking agent skeleton`) so automation hooks stay predictable. Every pull request should include a concise summary, clear testing notes (commands run plus results), linked issue IDs, and screenshots or transcripts for interactive agent flows. Rebase before requesting review and ensure CI is green.

## Environment & Secrets
Store API keys and OAuth tokens in a `.env` file and load them via `python-dotenv` or your preferred secrets layer; never commit secrets or service account JSON. Document any required environment variables in `README.md` and provide sanitized `.env.example` updates when configuration changes.
