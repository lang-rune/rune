# Changelog

All notable changes to Rune are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

---

## [Unreleased]

---

## [0.2.0] — 2025-06-01

### Added

- `rune/lexer/keywords.py` — keyword-to-TokenType mapping extracted from the lexer into its own file; language keywords are now a single source of truth
- `rune/parser/precedence.py` — explicit integer precedence levels and token-type groups per level; replaces inline token references throughout the parser
- `rune/runtime/signals.py` — `RuntimeError`, `ReturnSignal`, `SkipSignal`, `StopSignal` isolated as control-flow primitives; imported by environment, builtins, and interpreter
- `rune/runtime/environment.py` — `Environment` class with lexical scope chain (`get`, `define`, `set`)
- `rune/runtime/values.py` — `SpellValue` dataclass representing a first-class spell with its closure
- `rune/runtime/builtins.py` — `Builtins` class and `to_rune_string()` module-level helper isolated from interpreter logic
- `rune/__init__.py` — makes `rune` a proper importable top-level package
- `rune/tests/__init__.py` — enables `rune.tests.test_interpreter` module path for test discovery

### Changed

- Flat files (`lexer.py`, `tokens.py`, `ast_nodes.py`, `parser.py`, `interpreter.py`) reorganised into packages: `lexer/`, `ast/`, `parser/`, `runtime/`
- All cross-package imports converted to relative imports (`from ..ast import ...`, `from ..lexer import ...`)
- Test runner command changed to `python -m unittest rune.tests.test_interpreter -v` (run from `rune-lang/`)
- Parser uses `self.match(*TERM_OPS)` instead of inline token-type references

### Fixed

- Python stdlib `ast` module no longer shadowed when running tests or importing `rune`

---

## [0.1.0] — 2025-01-01

### Added

- Lexer with line and column tracking
- Recursive-descent parser producing a typed AST
- Tree-walk interpreter using the visitor pattern
- Data types: `number` (float), `word` (string), `boolean` (`yes`/`no`), `empty` (null)
- Variables: `set x = value`
- Arithmetic operators: `+`, `-`, `*`, `/`, `%`
- Comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical operators: `and`, `or`, `not`
- String concatenation via `+` with automatic coercion
- Conditionals: `if / otherwise` with else-if chaining
- Loops: `while`, `repeat N times`, `count from X to Y as var`
- Loop control: `skip` (continue), `stop` (break)
- Spells: `spell name(params) { }`, first-class values, closures
- Return values: `return expr`
- Built-in functions: `write`, `input`, `type`, `length`, `number`, `word`
- REPL and file runner CLI
- 24-test integration test suite

[Unreleased]: https://github.com/kjxcodez/rune-lang/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/kjxcodez/rune-lang/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kjxcodez/rune-lang/releases/tag/v0.1.0
