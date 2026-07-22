# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repository is a fresh, unstarted scaffold (project name suggests an intended LangChain experiment). Current state:

- `main.py` is the untouched PyCharm "Hello World" template — no actual application code yet.
- `.venv` exists but has no packages installed beyond `pip` (no `langchain` or any other dependency installed yet).
- No `requirements.txt`, `pyproject.toml`, or `setup.py` — dependency management has not been set up.
- No git commits yet (repo is initialized but `master` has no history).
- No README, no Cursor/Copilot rule files, no tests, no build/lint tooling configured.

## Working in this repo

Since there is no established structure, build system, or test suite yet:

- Before adding dependencies, check whether the user wants a `requirements.txt` or `pyproject.toml`-based setup and use the existing `.venv`.
- Don't invent architecture, folder structure, or conventions — none exist yet. Ask the user for direction on structure before scaffolding a larger app.
- Once real code/dependencies/tests are added, this file should be updated with actual run/build/lint/test commands and the real architecture.
