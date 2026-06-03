#!/usr/bin/env python3
"""Rune language CLI — REPL and file runner."""

import sys
import os

VERSION = "0.2.0"

# When running directly (not installed), ensure `rune-lang/` is on sys.path
# so that `import rune` resolves correctly.
_cli_dir = os.path.dirname(os.path.abspath(__file__))   # rune/cli/
_pkg_dir = os.path.dirname(_cli_dir)                    # rune/
_root_dir = os.path.dirname(_pkg_dir)                   # rune-lang/
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from rune.lexer import Lexer
from rune.parser import Parser
from rune.runtime import Interpreter


# ── Source runner ──────────────────────────────────────────────────────────────

def run_source(source: str, filename: str = "<input>") -> bool:
    """Lex, parse, and interpret *source*. Returns True on success."""
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        Interpreter().run(ast)
        return True
    except SyntaxError as e:
        print(f"Syntax Error in {filename}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error in {filename}: {e}", file=sys.stderr)
        return False


def _read_file(path: str):
    """Read a source file and return its contents, or None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"rune: file not found: '{path}'", file=sys.stderr)
        return None
    except OSError as e:
        print(f"rune: cannot read '{path}': {e}", file=sys.stderr)
        return None


def run_file(path: str) -> int:
    """Run a .rune file. Returns exit code."""
    source = _read_file(path)
    if source is None:
        return 1
    return 0 if run_source(source, path) else 1


# ── Debug subcommands ──────────────────────────────────────────────────────────

def cmd_tokenize(path: str) -> int:
    """Print the token stream for a source file."""
    source = _read_file(path)
    if source is None:
        return 1
    try:
        tokens = Lexer(source).tokenize()
    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        return 1

    col_w = max(len(t.type.name) for t in tokens) + 2
    for tok in tokens:
        if tok.type.name == "EOF":
            break
        print(f"{tok.line:4}:{tok.column:<4} {tok.type.name:<{col_w}} {tok.value!r}")
    return 0


def cmd_ast(path: str) -> int:
    """Print the Abstract Syntax Tree for a source file."""
    source = _read_file(path)
    if source is None:
        return 1
    try:
        tokens = Lexer(source).tokenize()
        tree = Parser(tokens).parse()
    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        return 1

    _print_ast(tree)
    return 0


def _print_ast(node, indent: int = 0) -> None:
    prefix = "  " * indent
    name = type(node).__name__

    # Leaf nodes — print on one line
    from rune.ast import (
        NumberLiteral, WordLiteral, BooleanLiteral, EmptyLiteral,
        Identifier, Program,
        BinaryOp, UnaryOp, FunctionCall,
        WriteStatement, AssignmentStatement, ExpressionStatement,
        IfStatement, WhileStatement,
        SpellDefinition, CastStatement, ReturnStatement,
        RepeatStatement, CountStatement, SkipStatement, StopStatement,
    )

    if isinstance(node, NumberLiteral):
        print(f"{prefix}NumberLiteral({node.value})")
    elif isinstance(node, WordLiteral):
        print(f"{prefix}WordLiteral({node.value!r})")
    elif isinstance(node, BooleanLiteral):
        print(f"{prefix}BooleanLiteral({'yes' if node.value else 'no'})")
    elif isinstance(node, EmptyLiteral):
        print(f"{prefix}EmptyLiteral()")
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier({node.name!r})")
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp({node.operator!r})")
        _print_ast(node.left, indent + 1)
        _print_ast(node.right, indent + 1)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp({node.operator!r})")
        _print_ast(node.operand, indent + 1)
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall({node.name!r}, {len(node.args)} args)")
        for arg in node.args:
            _print_ast(arg, indent + 1)
    elif isinstance(node, WriteStatement):
        print(f"{prefix}WriteStatement({len(node.args)} args)")
        for arg in node.args:
            _print_ast(arg, indent + 1)
    elif isinstance(node, AssignmentStatement):
        print(f"{prefix}AssignmentStatement({node.variable!r})")
        _print_ast(node.value, indent + 1)
    elif isinstance(node, ExpressionStatement):
        print(f"{prefix}ExpressionStatement()")
        _print_ast(node.expression, indent + 1)
    elif isinstance(node, IfStatement):
        print(f"{prefix}IfStatement()")
        print(f"{prefix}  condition:")
        _print_ast(node.condition, indent + 2)
        print(f"{prefix}  then:")
        for s in node.then_body:
            _print_ast(s, indent + 2)
        if node.else_body:
            print(f"{prefix}  else:")
            for s in node.else_body:
                _print_ast(s, indent + 2)
    elif isinstance(node, WhileStatement):
        print(f"{prefix}WhileStatement()")
        print(f"{prefix}  condition:")
        _print_ast(node.condition, indent + 2)
        print(f"{prefix}  body:")
        for s in node.body:
            _print_ast(s, indent + 2)
    elif isinstance(node, SpellDefinition):
        params = ", ".join(node.params)
        print(f"{prefix}SpellDefinition({node.name!r}, params=[{params}])")
        for s in node.body:
            _print_ast(s, indent + 1)
    elif isinstance(node, CastStatement):
        print(f"{prefix}CastStatement()")
        _print_ast(node.call, indent + 1)
    elif isinstance(node, ReturnStatement):
        print(f"{prefix}ReturnStatement()")
        if node.value is not None:
            _print_ast(node.value, indent + 1)
    elif isinstance(node, RepeatStatement):
        print(f"{prefix}RepeatStatement()")
        print(f"{prefix}  count:")
        _print_ast(node.count, indent + 2)
        print(f"{prefix}  body:")
        for s in node.body:
            _print_ast(s, indent + 2)
    elif isinstance(node, CountStatement):
        print(f"{prefix}CountStatement(var={node.variable!r})")
        print(f"{prefix}  start:")
        _print_ast(node.start, indent + 2)
        print(f"{prefix}  end:")
        _print_ast(node.end, indent + 2)
        print(f"{prefix}  body:")
        for s in node.body:
            _print_ast(s, indent + 2)
    elif isinstance(node, SkipStatement):
        print(f"{prefix}SkipStatement()")
    elif isinstance(node, StopStatement):
        print(f"{prefix}StopStatement()")
    elif isinstance(node, Program):
        print(f"{prefix}Program({len(node.statements)} statements)")
        for s in node.statements:
            _print_ast(s, indent + 1)
    else:
        print(f"{prefix}{node!r}")


# ── REPL ───────────────────────────────────────────────────────────────────────

def repl() -> None:
    """Start the interactive REPL."""
    print(f"Rune {VERSION}  |  type 'exit' or Ctrl-C to quit, 'help' for help")
    print("-" * 60)

    # Persistent interpreter so variables survive between lines
    interpreter = Interpreter()

    while True:
        try:
            line = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not line:
            continue

        if line.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if line.lower() == "help":
            _print_help()
            continue

        try:
            tokens = Lexer(line).tokenize()
            ast = Parser(tokens).parse()
            interpreter.run(ast)
        except SyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def _print_help() -> None:
    print("""
Rune Language Quick Reference
==============================

Data types
  number    42, 3.14, -5
  word      "hello", "world"
  boolean   yes, no
  empty     empty

Variables
  set name = "Alice"
  set score = 0

Output
  write("Hello, world!")
  write("Score:", score)

Arithmetic
  set result = 5 + 3 * 2
  set rem = 10 % 3

Comparisons
  5 > 3    5 == 5    3 != 5    5 >= 5

Logic
  x > 0 and x < 10
  not active

Conditionals
  if score > 90 {
      write("A")
  } otherwise score > 80 {
      write("B")
  } otherwise {
      write("F")
  }

Loops
  while counter < 5 {
      write(counter)
      set counter = counter + 1
  }

  repeat 3 times {
      write("again")
  }

  count from 1 to 5 as i {
      write(i)
  }

  skip   -- next iteration
  stop   -- break loop

Spells (functions)
  spell add(a, b) {
      return a + b
  }
  write(add(3, 4))

Built-ins
  write(value, ...)   type(value)
  input(prompt)       length(word)
  number(value)       word(value)
""")


# ── Entry point ────────────────────────────────────────────────────────────────

def _usage() -> None:
    print(f"""\
Rune {VERSION} — a beginner-friendly programming language

Usage:
  rune                       Start the interactive REPL
  rune repl                  Start the interactive REPL
  rune run <file.rune>       Run a Rune source file
  rune <file.rune>           Run a Rune source file (shorthand)
  rune tokenize <file.rune>  Print the token stream (debug)
  rune ast <file.rune>       Print the Abstract Syntax Tree (debug)
  rune --version             Print version and exit
  rune --help                Show this help message
""")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        repl()
        return

    if args[0] in ("--version", "-V"):
        print(f"Rune {VERSION}")
        return

    if args[0] in ("--help", "-h"):
        _usage()
        return

    if args[0] == "repl":
        repl()
        return

    if args[0] == "run":
        if len(args) < 2:
            print("rune: 'run' requires a file argument", file=sys.stderr)
            print("Usage: rune run <file.rune>", file=sys.stderr)
            sys.exit(1)
        sys.exit(run_file(args[1]))

    if args[0] == "tokenize":
        if len(args) < 2:
            print("rune: 'tokenize' requires a file argument", file=sys.stderr)
            print("Usage: rune tokenize <file.rune>", file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_tokenize(args[1]))

    if args[0] == "ast":
        if len(args) < 2:
            print("rune: 'ast' requires a file argument", file=sys.stderr)
            print("Usage: rune ast <file.rune>", file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_ast(args[1]))

    # Bare file path: rune file.rune
    if len(args) == 1:
        sys.exit(run_file(args[0]))

    print(f"rune: unknown command '{args[0]}'", file=sys.stderr)
    _usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
