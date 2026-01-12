# Repository Guidelines

## Project Structure & Module Organization
This repository is a standalone LMP-based mobile manipulation demo. Core Python modules live at the repo root, with prompts and cache data in subfolders.

- `run_test.py`: main entry point that wires the planner, executor, and mock environment.
- `meta_planner_lmp.py`, `LMP.py`, `condition_checker_lmp.py`: planning, execution, and condition checking logic.
- `mock_env_mobile.py`: mock simulation environment and robot actions.
- `prompts/`: LLM prompt templates (e.g., `prompts/loco_manip_prompt.txt`).
- `requirements.txt`: Python dependencies.
- `cache/`: serialized LLM cache files; treat as generated artifacts.

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install runtime dependencies.
- `python run_test.py`: run the end-to-end demo using the mock environment.
- `python run_test.py` after editing `instruction` near the bottom of `run_test.py` to try new tasks.

## Coding Style & Naming Conventions
- Python 3, 4-space indentation; keep lines readable and avoid unnecessary complexity.
- Use `snake_case` for functions/variables, `CamelCase` for classes, and `UPPER_CASE` for module-level constants.
- Keep prompt text in `prompts/` and avoid hardcoding long prompt strings in code.
- No formatter or linter is configured; keep changes consistent with existing style.

## Testing Guidelines
- No dedicated automated test suite is included; `run_test.py` serves as the primary integration test.
- When adding new behavior, update `run_test.py` or add a small runnable script with a clear entry point.
- Use descriptive task strings and ensure mock environment logs remain readable.

## Commit & Pull Request Guidelines
- Commit messages in this repo are short and direct (e.g., “API Thing”, “README file”). Follow that pattern: brief, present-tense phrases.
- PRs should describe the task, the expected behavior change, and any prompt changes.
- Include sample output snippets or screenshots for behavior changes to planner/executor flows.

## Configuration & Secrets
- API keys are configured in `run_test.py`; do not commit real keys.
- If you add new configuration, document it in `README.md` and keep defaults safe.
