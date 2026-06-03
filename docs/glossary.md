# Rune Glossary

Terms specific to the Rune language and its implementation.

---

## AST (Abstract Syntax Tree)

A tree data structure that represents the grammatical structure of a Rune program. Each node in the tree corresponds to a language construct: a literal, an operator, a statement, or a block. The parser produces the AST; the interpreter walks it.

Example: the expression `1 + 2 * 3` becomes a tree where `+` is the root, `1` is its left child, and `*` (with children `2` and `3`) is its right child.

See `rune/ast/nodes.py` for all node definitions.

---

## Cast

An explicit invocation of a spell using the `cast` keyword. Semantically identical to a direct call; the keyword is provided for readability and to signal intent.

```
cast greet("world")   # same as greet("world")
```

---

## Closure

A spell that captures (remembers) the environment in which it was defined. When a closure is called later, it can still access variables from its definition scope, even if that scope is no longer active on the call stack.

```
spell make_adder(n) {
    spell add(x) {
        return x + n    # 'n' is captured from make_adder's scope
    }
    return add
}

set add5 = make_adder(5)
write add5(3)   # 8
```

In the implementation, closures are created by `SpellValue` capturing `self.current_env` at definition time.

---

## Environment

A dictionary of variable names mapped to their current values. Environments form a **chain**: each environment has an optional parent, allowing inner scopes to look up variables defined in outer scopes.

The global environment is the root of this chain. Each spell call creates a new environment chained to the spell's closure environment.

See `rune/runtime/environment.py`.

---

## Spell

A named, reusable block of code — Rune's equivalent of a function. Defined with the `spell` keyword. Spells are first-class values: they can be assigned to variables, passed as arguments, and returned from other spells.

```
spell greet(name) {
    write "Hello, " name
}
```

---

## Token

A single meaningful unit produced by the lexer from the raw source text. Every token has a type (e.g. `NUMBER`, `IDENTIFIER`, `PLUS`) and a value (the raw source text, e.g. `"42"`, `"score"`, `"+"`).

The lexer converts the source character stream into a flat list of tokens. The parser then consumes that list.

See `rune/lexer/token.py` and `rune/lexer/token_types.py`.

---

## Tree-Walk Interpreter

An interpreter that directly walks the AST to execute the program, without first compiling to bytecode or machine code. For each AST node, the interpreter calls the corresponding `visit_*` method, which evaluates the node and returns a value.

Tree-walk interpreters are simple to implement and easy to reason about, making them an ideal starting point for language development. The trade-off is performance: traversing Python objects at runtime is significantly slower than executing bytecode or native instructions.

Rune's current interpreter is a tree-walk interpreter. See `rune/runtime/interpreter.py`.

---

## Visitor Pattern

A design pattern used in the interpreter. Instead of putting evaluation logic inside each AST node, a single `Interpreter` object has one method per node type (`visit_NumberLiteral`, `visit_BinaryOp`, etc.). The central `interpret()` dispatcher routes each node to the correct method by name:

```python
method = getattr(self, f'visit_{type(node).__name__}', None)
```

This cleanly separates the data structure (AST nodes) from the operations performed on it (evaluation). Adding a new operation — such as a pretty-printer or a type-checker — means adding a new visitor class without touching the node definitions.
