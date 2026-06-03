# Rune — Architecture

This document describes the internal design of the Rune interpreter. It is intended for contributors and anyone curious about how the language works under the hood.

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Package Structure](#package-structure)
3. [Lexer (`rune/lexer/`)](#lexer-runelexer)
4. [AST (`rune/ast/`)](#ast-runeast)
5. [Parser (`rune/parser/`)](#parser-runeparser)
6. [Runtime (`rune/runtime/`)](#runtime-runeruntime)
7. [Environment & Scoping](#environment--scoping)
8. [Closures](#closures)
9. [Control Flow Signals](#control-flow-signals)
10. [Dependency Graph](#dependency-graph)
11. [Future: Bytecode Compiler](#future-bytecode-compiler)

---

## Pipeline Overview

Source code travels through four stages before producing output:

```
Source text (.rune)
        │
        ▼
  ┌──────────┐
  │  Lexer   │  Tokenise characters into a flat list of Tokens
  └──────────┘
        │  List[Token]
        ▼
  ┌──────────┐
  │  Parser  │  Consume tokens, build an Abstract Syntax Tree
  └──────────┘
        │  Program (AST root)
        ▼
  ┌─────────────┐
  │ Interpreter │  Walk the AST, evaluate nodes, produce side-effects
  └─────────────┘
        │
        ▼
   stdout / return values
```

Each stage is entirely separate. The lexer knows nothing about grammar; the parser knows nothing about evaluation. This makes each component easy to test and replace.

---

## Package Structure

```
rune/
├── __init__.py          # makes rune an importable package
├── lexer/
│   ├── __init__.py      # exports Lexer, Token, TokenType
│   ├── lexer.py         # Lexer class
│   ├── token.py         # Token dataclass
│   ├── token_types.py   # TokenType enum (all ~50 variants)
│   └── keywords.py      # keyword → TokenType mapping (language-definition data)
├── ast/
│   ├── __init__.py      # exports all 22 node classes
│   └── nodes.py         # ASTNode hierarchy
├── parser/
│   ├── __init__.py      # exports Parser
│   ├── parser.py        # recursive-descent Parser
│   └── precedence.py    # precedence levels and operator token-type groups
├── runtime/
│   ├── __init__.py      # exports Interpreter
│   ├── signals.py       # RuntimeError, ReturnSignal, SkipSignal, StopSignal
│   ├── environment.py   # Environment (lexical scope chain)
│   ├── values.py        # SpellValue (first-class function representation)
│   ├── builtins.py      # Builtins class + to_rune_string() helper
│   └── interpreter.py   # tree-walk Interpreter (visitor pattern)
├── cli/
│   └── main.py          # entry point: file runner + REPL
└── tests/
    ├── __init__.py
    └── test_interpreter.py
```

---

## Lexer (`rune/lexer/`)

The lexer converts raw source text into a flat list of `Token` objects. It operates as a single-pass scanner.

### `token_types.py`

Defines the `TokenType` enum using `auto()`. Every distinct token the language can produce has an entry: literals (`NUMBER`, `STRING`, `BOOLEAN`, `EMPTY`), operators (`PLUS`, `MINUS`, ...), delimiters (`LBRACE`, `RBRACE`, `LPAREN`, `RPAREN`), keywords (`WRITE`, `SET`, `IF`, ...), and `EOF`.

### `token.py`

```python
class Token:
    type: TokenType
    value: str      # raw text from source
    line: int
    column: int
```

The `value` field always holds the raw source text (e.g. `"42"`, `"hello"`, `"+"`). Parsing into Python values (e.g. `float(token.value)`) happens in the parser.

### `keywords.py`

A plain dict mapping keyword strings to `TokenType` values. This is **language-definition data**, not lexer logic — adding a new keyword only requires editing this file.

### `lexer.py`

The `Lexer` class drives the scan. Key responsibilities:
- Walk character by character through the source
- Emit `Token` objects with accurate line/column tracking
- Distinguish identifiers from keywords by checking `KEYWORDS` after scanning an identifier
- Handle numeric literals (int and float)
- Handle string literals (double-quoted)
- Skip whitespace and comments

---

## AST (`rune/ast/`)

The AST is a tree of node objects. Every node is a plain Python dataclass — no methods, no logic.

### Node hierarchy

```
ASTNode
├── Expression
│   ├── NumberLiteral     (value: float)
│   ├── WordLiteral       (value: str)
│   ├── BooleanLiteral    (value: bool)
│   ├── EmptyLiteral
│   ├── Identifier        (name: str)
│   ├── BinaryOp          (operator: str, left: Expression, right: Expression)
│   ├── UnaryOp           (operator: str, operand: Expression)
│   └── FunctionCall      (name: str, args: List[Expression])
└── Statement
    ├── Program            (statements: List[Statement])
    ├── WriteStatement     (args: List[Expression])
    ├── AssignmentStatement (variable: str, value: Expression)
    ├── ExpressionStatement (expression: Expression)
    ├── IfStatement        (condition, then_body, else_body)
    ├── WhileStatement     (condition, body)
    ├── RepeatStatement    (count: Expression, body)
    ├── CountStatement     (variable, start, end, body)
    ├── SpellDefinition    (name, params, body)
    ├── CastStatement      (call: FunctionCall)
    ├── ReturnStatement    (value: Expression | None)
    ├── SkipStatement
    └── StopStatement
```

---

## Parser (`rune/parser/`)

The parser uses **recursive descent** — one method per grammar rule, calling each other to form a natural call-stack representation of precedence.

### `precedence.py`

Stores two things per level:
1. An integer constant (`PRECEDENCE_OR = 1`, `PRECEDENCE_AND = 2`, ...)
2. A tuple of `TokenType` values that belong to that level

```python
TERM_OPS = (TokenType.PLUS, TokenType.MINUS)
FACTOR_OPS = (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO)
```

The parser calls `self.match(*TERM_OPS)` instead of spelling out token types inline. All knowledge of "which tokens belong to which level" lives in one place — structural preparation for future Pratt parsing.

### `parser.py`

Key methods:

| Method            | Grammar level                       |
|-------------------|-------------------------------------|
| `parse()`         | `program → statement*`              |
| `statement()`     | dispatches to specific statement parsers |
| `expression()`    | delegates to `or_expr()`            |
| `or_expr()`       | `and_expr ("or" and_expr)*`         |
| `and_expr()`      | `equality_expr ("and" equality_expr)*` |
| `equality_expr()` | `comparison_expr (("==" \| "!=") ...)*` |
| `comparison_expr()` | `term_expr ((">" \| "<" \| ...) ...)*` |
| `term_expr()`     | `factor_expr (("+" \| "-") ...)*`   |
| `factor_expr()`   | `unary_expr (("*" \| "/" \| "%") ...)*` |
| `unary_expr()`    | `("-" \| "+" \| "not") unary \| primary` |
| `primary()`       | literals, identifiers, calls, `(expr)` |

---

## Runtime (`rune/runtime/`)

### `signals.py`

Defines all exceptions used for control flow:

- `RuntimeError` — language-level error (shadows Python's builtin within this package, intentionally)
- `ReturnSignal(value)` — raised by `return`, caught in `visit_FunctionCall`
- `SkipSignal` — raised by `skip`, caught in loop visitors
- `StopSignal` — raised by `stop`, caught in loop visitors

Isolating these means `environment.py` and `builtins.py` can import `RuntimeError` without circular dependencies.

### `environment.py`

```
Environment(parent=None)
├── variables: dict[str, Any]
└── parent: Environment | None
```

Variable lookup walks the chain toward the root. `define()` always writes to the current environment. `set()` walks toward root looking for the name, falls back to current env if not found (variable hoisting behaviour).

### `values.py`

`SpellValue` represents a first-class spell:

```python
class SpellValue:
    name: str
    params: List[str]
    body: List[Statement]   # typed Any to avoid coupling to ast package at import time
    closure: Environment    # captured at definition
```

### `builtins.py`

`Builtins` is a class whose methods map to Rune's built-in functions. They are bound and stored in a dict on the `Interpreter`:

```python
self.builtins = {
    'write': _b.write,
    'input': _b.input,
    'type':  _b.type_of,
    ...
}
```

`to_rune_string()` is a module-level function (not a method) because it is also used by `interpreter.py` for string coercion during `+` operations.

### `interpreter.py`

The `Interpreter` is a **tree-walk interpreter** using the **visitor pattern**:

```python
def interpret(self, node: ASTNode) -> Any:
    method = getattr(self, f'visit_{type(node).__name__}', None)
    if method:
        return method(node)
    self.error(f"No visit method for {type(node)}")
```

Every AST node type has a corresponding `visit_*` method. Adding a new node type to the language requires:
1. Adding a node class to `ast/nodes.py`
2. Adding a `visit_*` method to `interpreter.py`
3. Adding a parser rule that produces the node

---

## Environment & Scoping

Rune uses **lexical scoping** via a chain of `Environment` objects.

When the interpreter starts, it creates a single `global_env`. Each spell call creates a new `Environment` with `parent=spell.closure` (not `parent=current_env`), which is what makes closures work correctly.

```
global_env
    └── make_counter call env (count = 0)
            └── increment call env (empty — reads 'count' from parent)
```

Lookup: `get("count")` on the innermost env walks up the chain until it finds the name or raises `RuntimeError`.

---

## Closures

When a `SpellDefinition` node is visited, a `SpellValue` is created and `self.current_env` is captured as `.closure`:

```python
def visit_SpellDefinition(self, node):
    self.current_env.define(
        node.name,
        SpellValue(node.name, node.params, node.body, self.current_env)
    )
```

When the spell is later called, the execution environment is created as:

```python
call_env = Environment(spell.closure)   # parent = closure, not current call site
```

This ensures the spell sees variables from where it was **defined**, not where it was **called**.

---

## Control Flow Signals

`skip`, `stop`, and `return` are implemented as Python exceptions that propagate up through `interpret()` calls until caught by the appropriate loop or function visitor:

```
visit_StopStatement  →  raise StopSignal
visit_WhileStatement →  except StopSignal: break
visit_FunctionCall   →  except ReturnSignal as ret: return_value = ret.value
```

This cleanly separates control flow from evaluation logic without needing explicit state flags.

---

## Dependency Graph

```
lexer/token_types  ←  lexer/token  ←  lexer/lexer  ←  lexer/__init__
lexer/keywords     ←  lexer/lexer

ast/nodes  ←  ast/__init__

lexer/__init__  ←  parser/precedence
lexer/__init__  ←  parser/parser
ast/__init__    ←  parser/parser
parser/precedence ←  parser/parser

runtime/signals     ←  runtime/environment
runtime/signals     ←  runtime/builtins
runtime/signals     ←  runtime/interpreter
runtime/environment ←  runtime/interpreter
runtime/values      ←  runtime/interpreter
runtime/builtins    ←  runtime/interpreter
ast/__init__        ←  runtime/interpreter
```

There are no circular dependencies.

---

## Future: Bytecode Compiler

The current tree-walk interpreter re-traverses the AST on every execution. A natural next step is a bytecode compiler:

```
AST  →  Compiler  →  Bytecode  →  Virtual Machine
```

The visitor pattern in the interpreter maps almost directly onto a compiler: instead of evaluating, each `visit_*` method would emit instructions. The `Environment` chain would become a stack frame. This transformation can be done incrementally — the AST and parser packages would remain unchanged.
