# Contributing to EduPulse

Thank you for your interest in contributing to EduPulse! This project is a multi-agent AI system for student success built on Google ADK. Contributions of all kinds are welcome — code, docs, data, bug reports, and feature ideas.

Please note that this project follows a code of conduct; by participating you agree to abide by its terms.

## Getting Started

1. **Fork** the repository and create your branch from `main`.
2. **Set up a local environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # or `.venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
3. **Run the tests** to confirm your baseline is green:
   ```bash
   python -m pytest tests/ -q
   ```
4. **Run the linter:**
   ```bash
   python -m ruff check edupulse/ tools/
   ```

## Development Workflow

- Keep changes focused. One logical change per pull request.
- Configuration lives in `edupulse/config.py` and is driven by environment variables. **Do not hardcode deployment-specific values** (project IDs, regions, model names, dataset names) in code, scripts, or documentation — always reference env vars or config defaults.
- Follow existing code style (mimic surrounding code; no comments unless they add real value).
- Add or update tests for any behavioral change. All tests must pass and ruff must be clean before submitting.

## Running Tests

```bash
python -m pytest tests/ -q
```

## Running the Agent Locally

```bash
export PROJECT_ID=your-project-id
export GEMINI_API_KEY=your-key
adk web edupulse
```

See [SETUP.md](SETUP.md) and [README.md](README.md) for full setup and deployment instructions.

## Pull Request Checklist

- [ ] Branch from `main` and keep it up to date.
- [ ] No hardcoded deployment variables introduced.
- [ ] Tests pass (`python -m pytest tests/ -q`).
- [ ] Ruff clean (`python -m ruff check edupulse/ tools/`).
- [ ] Docs updated if behavior or config changed.

## Reporting Issues

Before opening an issue, search existing issues to avoid duplicates. Include:
- A clear, descriptive title.
- Steps to reproduce (for bugs).
- Expected vs. actual behavior.
- Environment details (Python version, OS, ADK version).

## License

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE).
