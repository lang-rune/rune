# Development Guide

This guide covers everything you need to get Rune running locally, run tests, and add new features.

---

## Prerequisites

- Python 3.10 or later
- Git

No third-party dependencies are required. Rune is built entirely on the Python standard library.

---

## Setup

```bash
git clone https://github.com/kjxcodez/rune-lang.git
cd rune-lang
```

That's it. There is no `pip install` step.

---

## Project Structure

```
rune-lang/
├── rune/                   # main package
│   ├── lexer/              # tokeniser
│   ├── ast/                # AST node definitions
│   ├── parser/             # recursive-descent parser
│   ├── runtime/            # interpreter, environment, builtins
│   ├── cli/                # command-line entry point
│   └── tests/              # test suite
└── docs/                   # documentation
```

The working directory for all commands below is `rune-lang/` (the repository root).

---

## Running a Rune Program

```bash
python -m rune.cli.main path/to/program.rune
```

---

## Running the REPL

```bash
python -m rune.cli.main
```

---

## Running Tests

Always run tests from `rune-lang/` (not from inside `rune/`):

```bash
python -m unittest rune.tests.test_interpreter -v
```

Expected output:

```
test_arithmetic ... ok
test_boolean_logic ... ok
test_closures ... ok
...
----------------------------------------------------------------------
Ran 24 tests in 0.XXXs

OK
```

> **Why from `rune-lang/`?**  
> The `rune/ast/` package would shadow Python's stdlib `ast` module if `rune/` were on `sys.path`. Running from the parent directory ensures `import rune` resolves to the package, and all cross-package imports use relative paths that are immune to `sys.path` order.

---

## Adding a New Language Feature

A typical feature touches three files:

### 1. Add AST node(s) — `rune/ast/nodes.py`

Define a new dataclass inheriting from `Statement` or `Expression`:

```python
@dataclass
class ForEachStatement(Statement):
    variable: str
    iterable: Expression
    body: List[Statement]
```

Then export it from `rune/ast/__init__.py`.

### 2. Add token(s) if needed — `rune/lexer/`

If the feature needs a new keyword, add it to:
- `token_types.py` — new `TokenType` enum variant
- `keywords.py` — mapping from keyword string to `TokenType`

If the feature needs a new operator, add the `TokenType` to `token_types.py` and update `lexer.py` to emit it.

### 3. Add parser rule — `rune/parser/parser.py`

Add a new method to `Parser` and call it from `statement()` (or from the appropriate expression level):

```python
def for_each_stmt(self) -> ForEachStatement:
    self.consume(TokenType.FOR)
    variable = self.consume(TokenType.IDENTIFIER).value
    self.consume(TokenType.IN)
    iterable = self.expression()
    body = self.block()
    return ForEachStatement(variable, iterable, body)
```

### 4. Add interpreter visitor — `rune/runtime/interpreter.py`

Add a `visit_*` method matching the node class name:

```python
def visit_ForEachStatement(self, node: ForEachStatement) -> None:
    items = self.interpret(node.iterable)
    for item in items:
        self.current_env.define(node.variable, item)
        try:
            for stmt in node.body:
                self.interpret(stmt)
        except SkipSignal:
            continue
        except StopSignal:
            break
```

### 5. Write tests

Add test cases to `rune/tests/test_interpreter.py`. Follow the pattern used by existing tests:

```python
def test_for_each(self):
    result = self.run_program("""
        set items = ...
        for x in items {
            write x
        }
    """)
    self.assertEqual(...)
```

---

## Debugging

The simplest debugging approach is to inspect the token list or AST before evaluation:

```python
from rune.lexer import Lexer
from rune.parser import Parser

source = 'set x = 1 + 2'
tokens = Lexer(source).tokenize()
print(tokens)

ast = Parser(tokens).parse()
print(ast)
```

Adding `print()` statements inside `interpret()` or specific `visit_*` methods is also effective for tracing execution.

---

## Releasing

1. Update `docs/changelog.md` with the changes in the new version
2. Update the version constant (if one exists in `cli/main.py`)
3. Tag the commit:
   ```bash
   git tag v0.X.0
   git push origin v0.X.0
   ```
