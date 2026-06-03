# Roadmap

This document tracks what has been built and what is planned for future versions of Rune.

---

## Completed

### v0.1.0 — Initial Release

- **Lexer** — tokenises source text; tracks line and column numbers
- **Recursive-descent parser** — produces a typed AST
- **Tree-walk interpreter** — visitor pattern; evaluates all language constructs
- **Data types** — `number`, `word`, `boolean`, `empty`
- **Variables** — `set x = value`
- **Arithmetic operators** — `+`, `-`, `*`, `/`, `%`
- **Comparison operators** — `==`, `!=`, `>`, `<`, `>=`, `<=`
- **Logical operators** — `and`, `or`, `not`
- **String concatenation** — `+` with automatic coercion
- **Conditionals** — `if / otherwise` with else-if chaining
- **While loop** — `while condition { }`
- **Repeat loop** — `repeat N times { }`
- **Count loop** — `count from X to Y as var { }`
- **Loop control** — `skip` (continue), `stop` (break)
- **Spells** — `spell name(params) { }`, first-class values
- **Return values** — `return expr`
- **Closures** — spells capture their definition environment
- **Built-in functions** — `write`, `input`, `type`, `length`, `number`, `word`
- **REPL** — interactive read-eval-print loop
- **CLI file runner** — `python -m rune.cli.main program.rune`

### v0.2.0 — Architecture Refactor

- Split flat files into proper Python packages: `lexer/`, `ast/`, `parser/`, `runtime/`
- Extracted `keywords.py` as language-definition data separate from lexer mechanics
- Added `runtime/signals.py` to isolate control-flow primitives
- Added `runtime/environment.py`, `runtime/values.py`, `runtime/builtins.py`
- Added `parser/precedence.py` for explicit precedence levels and operator groups
- Fixed Python stdlib `ast` shadowing; all cross-package imports use relative paths
- Full 24-test suite passing

---

## Planned

### Near-term

- **Lists** — ordered mutable collections; `set items = [1 2 3]`; `items[0]`; `length(items)`
- **List iteration** — `for item in items { }`
- **String escapes** — `\n`, `\t`, `\\`, `\"` in word literals
- **Multiline strings** — triple-quoted word literals
- **Compound assignment** — `set x += 1`, `set x -= 1`

### Medium-term

- **Modules** — `import math` to load a `.rune` file as a namespace
- **Export** — `export spell_name` to expose spells from a module
- **Error handling** — structured error objects; `try / catch` equivalent
- **Standard library** — built-in modules for math, string manipulation, file I/O

### Long-term

- **Bytecode compiler** — compile AST to a compact instruction set
- **Virtual machine** — stack-based VM to execute bytecode; significant performance gain over tree-walk
- **Language Server Protocol (LSP)** — type inference and error reporting in editors
- **Formatter** — canonical code style enforced by a formatter (like `gofmt`)
- **Package manager** — install and share Rune libraries
- **Type annotations** — optional static types for spell parameters and variables

### Tooling

- **VS Code extension** — syntax highlighting, snippets (community prototype exists)
- **Web playground** — browser-based Rune editor powered by Pyodide

---

## Not planned

The following are explicitly out of scope for the foreseeable future:

- Native compilation (Rune is intended to remain a scripting language)
- Concurrency primitives (keep the language simple)
- Class-based object orientation (closures and spells cover most use cases)
