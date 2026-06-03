# Contributing to Rune

Thank you for your interest in contributing! Rune is a beginner-friendly project, and contributions of all kinds are welcome — bug reports, documentation improvements, new language features, or just sharing the project.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rune-lang.git
   cd rune-lang
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b my-feature
   ```

No dependencies to install — Rune runs on Python 3.10+ with no third-party packages.

---

## Development Setup

See [development.md](development.md) for full setup instructions, how to run the REPL, and how to run the test suite.

Quick start:

```bash
python -m unittest rune.tests.test_interpreter -v
```

All 24 tests should pass before you make any changes.

---

## Project Structure

```
rune/
├── lexer/      ← tokenises source text
├── ast/        ← AST node definitions (data only, no logic)
├── parser/     ← converts tokens into an AST
├── runtime/    ← interprets the AST
├── cli/        ← command-line entry point
└── tests/      ← integration tests
```

See [architecture.md](architecture.md) for a deeper explanation of how the pieces fit together.

---

## How to Add a Feature

Adding a new language feature typically requires changes in three places:

1. **`rune/ast/nodes.py`** — define the new AST node
2. **`rune/parser/parser.py`** — add a parsing rule that produces the node
3. **`rune/runtime/interpreter.py`** — add a `visit_*` method that evaluates the node

If the feature needs a new keyword: add the `TokenType` variant to `lexer/token_types.py` and the keyword string to `lexer/keywords.py`.

See [development.md](development.md) for a step-by-step walkthrough with code examples.

---

## Running Tests

```bash
cd rune-lang
python -m unittest rune.tests.test_interpreter -v
```

**Always run tests from `rune-lang/`** (the repository root), not from inside `rune/`.

Tests live in `rune/tests/test_interpreter.py`. Each test runs a short Rune program and checks the result. When adding a feature, add at least one test covering the happy path and one covering an error case.

---

## Pull Requests

Before opening a pull request:

- Run the full test suite and make sure it passes
- Add tests for any new behaviour
- Keep changes focused — one feature or fix per PR
- Update `docs/changelog.md` under `[Unreleased]` with a short description

PR title format:
```
feat: add list literals
fix: division by zero crash in REPL
docs: add contributing guide
```

---

## Code Style

- Python 3.10+ syntax
- 4-space indentation
- Type annotations on function signatures
- No comments unless the *why* is genuinely non-obvious
- No third-party dependencies

Rune follows the patterns already established in the codebase. When in doubt, look at how a similar feature is implemented and match that style.

---

## Reporting Bugs

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- The smallest Rune program that reproduces the problem
- Your Python version (`python --version`)

---

## Questions

Open a GitHub discussion or issue. There are no silly questions.
