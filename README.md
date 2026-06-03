# Rune

A beginner-friendly programming language built in Python.

Rune uses plain-English keywords and a clean, consistent grammar that can be learned in an afternoon. It is a dynamically typed, interpreted language with closures, first-class functions, and a small but complete standard library.

```
spell greet(name) {
    write("Hello, " + name + "!")
}

greet("world")
```

---

## Features

- **Plain-English syntax** — `set`, `write`, `if / otherwise`, `while`, `repeat`, `count from/to`
- **Four data types** — `number`, `word`, `boolean` (`yes`/`no`), `empty`
- **First-class spells** — functions as values, closures over their definition scope
- **Loop control** — `skip` (continue) and `stop` (break) in any loop
- **Built-in functions** — `write`, `input`, `type`, `length`, `number`, `word`
- **Zero dependencies** — pure Python 3.10+, nothing to install

---

## Quick Start

**Prerequisites:** Python 3.10 or later.

```bash
git clone https://github.com/kjxcodez/rune-lang.git
cd rune-lang
```

Run a file:

```bash
python -m rune.cli.main my_program.rune
```

Start the REPL:

```bash
python -m rune.cli.main
```

---

## Language at a Glance

### Variables

```
set name = "Rune"
set score = 0
set active = yes
```

### Conditionals

```
if score > 90 {
    write("A")
} otherwise score > 80 {
    write("B")
} otherwise {
    write("Try again")
}
```

### Loops

```
# while loop
while count > 0 {
    write(count)
    set count = count - 1
}

# repeat a fixed number of times
repeat 5 times {
    write("again")
}

# count over a range
count from 1 to 10 as i {
    write(i)
}
```

### Spells (Functions)

```
spell add(a, b) {
    return a + b
}

write(add(3, 7))   # 10
```

### Closures

```
spell make_counter() {
    set n = 0
    spell increment() {
        set n = n + 1
        return n
    }
    return increment
}

set counter = make_counter()
write(counter())   # 1
write(counter())   # 2
write(counter())   # 3
```

### Built-in Functions

| Function        | Description                              |
|-----------------|------------------------------------------|
| `write(…)`      | Print values to stdout                   |
| `input(prompt)` | Read a line from stdin                   |
| `type(value)`   | Return the type name as a word           |
| `length(word)`  | Return the character count of a word     |
| `number(value)` | Convert to number                        |
| `word(value)`   | Convert to word (string representation)  |

---

## Project Structure

```
rune/
├── lexer/        # tokenises source text into tokens
├── ast/          # AST node definitions
├── parser/       # recursive-descent parser
├── runtime/      # tree-walk interpreter, environment, builtins
├── cli/          # command-line entry point and REPL
└── tests/        # integration test suite
```

---

## Running Tests

```bash
cd rune-lang
python -m unittest rune.tests.test_interpreter -v
```

24 tests, all passing.

---

## Documentation

| Document | Description |
|---|---|
| [Language Specification](docs/specification.md) | Complete language reference |
| [Architecture](docs/architecture.md) | How the interpreter is built |
| [Glossary](docs/glossary.md) | Rune-specific terminology |
| [Development Guide](docs/development.md) | Setup, workflow, adding features |
| [Roadmap](docs/roadmap.md) | Completed and planned features |
| [Changelog](docs/changelog.md) | Version history |
| [Contributing](docs/contributing.md) | How to contribute |

---

## Roadmap

Completed: Lexer, Parser, AST, Interpreter, Closures, REPL, Architecture refactor.

Planned: Lists, Modules, Bytecode compiler, Virtual machine, LSP, Formatter, Package manager.

See [docs/roadmap.md](docs/roadmap.md) for the full list.

---

## Contributing

Contributions are welcome — bug reports, documentation, new features, or tooling. See [docs/contributing.md](docs/contributing.md) to get started.

---

## License

MIT License — Copyright (c) 2025 Kapil Jangid. See [LICENSE](LICENSE).
