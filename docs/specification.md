# Rune Language Specification

**Version:** 0.2.0  
**Status:** Draft

---

## Table of Contents

1. [Overview](#overview)
2. [Lexical Structure](#lexical-structure)
3. [Data Types](#data-types)
4. [Variables](#variables)
5. [Operators](#operators)
6. [Expressions](#expressions)
7. [Statements](#statements)
8. [Conditionals](#conditionals)
9. [Loops](#loops)
10. [Spells (Functions)](#spells-functions)
11. [Closures](#closures)
12. [Built-in Functions](#built-in-functions)
13. [Truthiness](#truthiness)
14. [Operator Precedence](#operator-precedence)
15. [Grammar Overview](#grammar-overview)

---

## Overview

Rune is a dynamically typed, interpreted programming language designed for beginners. It uses plain-English keywords to reduce syntactic noise, and follows a clean, consistent grammar that can be learned in an afternoon.

Programs are plain text files with the `.rune` extension.

---

## Lexical Structure

### Comments

Single-line comments start with `#` and extend to the end of the line.

```
# This is a comment
set x = 10  # inline comment
```

Multi-line comments are not supported.

### Identifiers

Identifiers name variables and spells. They must:
- Start with a letter (`a–z`, `A–Z`) or underscore (`_`)
- Contain only letters, digits (`0–9`), and underscores

```
myVariable
player_score
_temp
```

Identifiers are case-sensitive. `count` and `Count` are different names.

### Keywords

The following words are reserved and cannot be used as identifiers:

```
write   set     if      otherwise   else    while   repeat   times
count   from    to      as          spell   cast    return
skip    stop    yes     no          empty   and     or
not
```

### Number Literals

Numbers are IEEE 754 double-precision floating-point values. Both integer and decimal forms are accepted:

```
42
3.14
0.5
```

There is no distinction between integers and floats at the language level; both are the `number` type.

### Word Literals

Word literals (strings) are delimited by double or single quotes:

```
"hello"
"Rune is fun!"
""
```

The following escape sequences are supported inside word literals:

| Sequence | Character  |
|----------|------------|
| `\n`     | Newline    |
| `\t`     | Tab        |
| `\\`     | Backslash  |
| `\"`     | Double quote |
| `\'`     | Single quote |

### Boolean Literals

```
yes    # true
no     # false
```

### Empty Literal

```
empty  # null / absence of value
```

---

## Data Types

Rune has four built-in types:

| Type      | Description                         | Example values         |
|-----------|-------------------------------------|------------------------|
| `number`  | Floating-point numeric value        | `42`, `3.14`, `0`      |
| `word`    | Text string                         | `"hello"`, `""`        |
| `boolean` | Logical true or false               | `yes`, `no`            |
| `empty`   | Absence of a value (like null/nil)  | `empty`                |

Types are dynamic — a variable can hold any type and its type can change.

---

## Variables

Variables are declared and assigned with the `set` keyword:

```
set name = "Rune"
set score = 0
set active = yes
set result = empty
```

Variables do not need to be declared before use; `set` both declares and assigns in one step.

Reassignment uses the same syntax:

```
set score = score + 1
```

Variable names follow the identifier rules above.

---

## Operators

### Arithmetic

| Operator | Operation       | Example        |
|----------|-----------------|----------------|
| `+`      | Addition        | `1 + 2` → `3`  |
| `-`      | Subtraction     | `5 - 3` → `2`  |
| `*`      | Multiplication  | `3 * 4` → `12` |
| `/`      | Division        | `10 / 4` → `2.5` |
| `%`      | Modulo          | `10 % 3` → `1` |

Division by zero and modulo by zero are runtime errors.

### String Concatenation

The `+` operator concatenates when either operand is a `word`. The other operand is automatically converted to its string representation:

```
set msg = "Score: " + 42    # "Score: 42"
set both = "yes" + yes      # "yesyes"
```

### Comparison

All comparison operators return a `boolean`:

| Operator | Meaning                  |
|----------|--------------------------|
| `==`     | Equal                    |
| `!=`     | Not equal                |
| `>`      | Greater than             |
| `<`      | Less than                |
| `>=`     | Greater than or equal to |
| `<=`     | Less than or equal to    |

### Logical

| Operator | Meaning   | Short-circuits |
|----------|-----------|----------------|
| `and`    | Logical AND | Yes (left to right) |
| `or`     | Logical OR  | Yes (left to right) |
| `not`    | Logical NOT | N/A            |

`and` and `or` return a `boolean`, not the operand value.

### Unary

```
-x    # negate
+x    # no-op (unary plus)
not x # logical not
```

---

## Expressions

Expressions produce a value. Any expression can appear anywhere a value is expected.

### Primary expressions

- Number, word, boolean, and empty literals
- Identifiers (variable lookup)
- Function calls: `name(arg1, arg2)`
- Parenthesised expressions: `(expr)`

### Complex expressions

Expressions compose using operators according to the precedence rules in the [Operator Precedence](#operator-precedence) section.

---

## Statements

### Write statement

Prints one or more values to standard output, separated by spaces. Arguments are comma-separated inside parentheses:

```
write("hello")
write(x, y, z)
write("Score: ", score)
```

Numbers that are whole values print without a decimal point (`42` not `42.0`). Booleans print as `yes`/`no`. `empty` prints as `empty`.

### Assignment statement

```
set variable = expression
```

### Expression statement

A bare function call (used for its side effects):

```
write "done"
input("Enter name: ")
cast greet("world")
```

---

## Conditionals

### If / otherwise

```
if condition {
    # then-body
}
```

```
if condition {
    # then-body
} otherwise {
    # else-body
}
```

### Else-if chaining

Chain multiple conditions using `otherwise condition`:

```
if score > 90 {
    write "A"
} otherwise score > 80 {
    write "B"
} otherwise score > 70 {
    write "C"
} otherwise {
    write "F"
}
```

Conditions are any expression; truthiness rules apply (see [Truthiness](#truthiness)).

---

## Loops

### While loop

Repeats as long as the condition is truthy:

```
while x > 0 {
    write x
    set x = x - 1
}
```

### Repeat loop

Repeats a fixed number of times. The count is evaluated once at the start:

```
repeat 5 times {
    write "hello"
}

repeat count times {
    write "again"
}
```

The count must be a `number`. Non-integer values are truncated.

### Count loop

Iterates a variable over an inclusive integer range. The step direction is automatic:

```
count from 1 to 5 as i {
    write i
}
# prints 1 2 3 4 5

count from 10 to 1 as n {
    write n
}
# prints 10 9 8 7 6 5 4 3 2 1
```

The loop variable is scoped to the body and is updated before each iteration. Start and end values must be `number`; they are truncated to integers.

### Loop control

`skip` skips to the next iteration (like `continue`):

```
count from 1 to 10 as i {
    if i == 5 {
        skip
    }
    write i
}
```

`stop` exits the loop immediately (like `break`):

```
while yes {
    set x = input("Enter 'quit' to stop: ")
    if x == "quit" {
        stop
    }
    write "You said: " x
}
```

`skip` and `stop` work in `while`, `repeat`, and `count` loops.

---

## Spells (Functions)

Functions in Rune are called **spells**. They are defined with the `spell` keyword:

```
spell greet(name) {
    write "Hello, " name
}
```

### Calling a spell

```
greet("world")       # direct call
cast greet("world")  # explicit cast syntax (identical semantics)
```

Both forms are equivalent. `cast` is optional and provided for readability.

### Return values

Use `return` to return a value from a spell:

```
spell add(a b) {
    return a + b
}

set result = add(3 4)   # 7
```

If a spell reaches the end without `return`, it returns `empty`.

### Parameters

Parameters are space-separated inside the parentheses (no commas required, but commas are allowed):

```
spell sum(a b c) {
    return a + b + c
}
```

The number of arguments at the call site must exactly match the number of parameters. Passing the wrong number of arguments is a runtime error.

### Spells as values

Spells are first-class values. A spell can be assigned to a variable and called through it:

```
spell double(x) {
    return x * 2
}

set fn = double
write fn(5)   # 10
```

---

## Closures

Spells capture the environment in which they are defined. This creates a closure:

```
spell make_adder(n) {
    spell add(x) {
        return x + n    # 'n' is captured from make_adder's scope
    }
    return add
}

set add5 = make_adder(5)
write(add5(3))   # 8
```

**Current limitation:** `set` always writes to the innermost (current) scope. Reading captured variables from outer scopes works correctly, but assigning to them from an inner spell creates a new local variable instead of updating the captured one. Mutable closures (counters, accumulators) are a planned feature.

---

## Built-in Functions

Built-in functions are available everywhere without any import.

### `write(value, ...)`

Prints all arguments to standard output, separated by spaces, followed by a newline.

```
write("hello", "world")   # hello world
write(42)                 # 42
```

Note: `write` is a keyword statement. The parentheses are required.

### `input(prompt)`

Reads a line of text from standard input and returns it as a `word`. The prompt is optional.

```
set name = input("What is your name? ")
```

### `type(value)`

Returns a `word` describing the type of the given value:

| Value         | Returns     |
|---------------|-------------|
| `42`          | `"number"`  |
| `"hello"`     | `"word"`    |
| `yes` / `no`  | `"boolean"` |
| `empty`       | `"empty"`   |

### `length(value)`

Returns the number of characters in a `word` as a `number`. Raises a runtime error for non-word values.

```
write length("hello")   # 5
write length("")        # 0
```

### `number(value)`

Converts a value to a `number`:

- `number` → unchanged
- `word` → parsed as a float; error if not parseable
- `boolean` → `yes` → `1`, `no` → `0`
- `empty` → runtime error

```
write number("3.14")   # 3.14
write number(yes)      # 1
```

### `word(value)`

Converts a value to its `word` (string) representation using the same rules as string coercion:

```
write word(42)     # "42"
write word(yes)    # "yes"
write word(empty)  # "empty"
```

---

## Truthiness

The following values are **falsy**:

- `empty`
- `no` (boolean false)
- `0` (the number zero)
- `""` (empty word)

Everything else is **truthy**, including non-empty words, non-zero numbers, and `yes`.

Truthiness is used in `if`, `while`, and the `not` operator.

---

## Operator Precedence

From lowest to highest:

| Level | Operators              | Associativity |
|-------|------------------------|---------------|
| 1     | `or`                   | Left          |
| 2     | `and`                  | Left          |
| 3     | `==` `!=`              | Left          |
| 4     | `>` `<` `>=` `<=`      | Left          |
| 5     | `+` `-`                | Left          |
| 6     | `*` `/` `%`            | Left          |
| 7     | Unary `-` `+` `not`    | Right         |
| 8     | Primary (literals, calls, `()`) | — |

Higher level = tighter binding. `2 + 3 * 4` evaluates as `2 + (3 * 4)` = `14`.

---

## Grammar Overview

The following is an informal BNF-style grammar for reference. It is not normative.

```
program      = statement* EOF

statement    = write_stmt
             | assign_stmt
             | if_stmt
             | while_stmt
             | repeat_stmt
             | count_stmt
             | spell_def
             | cast_stmt
             | return_stmt
             | skip_stmt
             | stop_stmt
             | expr_stmt

write_stmt   = "write" "(" (expr ("," expr)*)? ")"
assign_stmt  = "set" IDENTIFIER "=" expr
if_stmt      = "if" expr block ("otherwise" (expr block | block))*
while_stmt   = "while" expr block
repeat_stmt  = "repeat" expr "times" block
count_stmt   = "count" "from" expr "to" expr "as" IDENTIFIER block
spell_def    = "spell" IDENTIFIER "(" params? ")" block
cast_stmt    = "cast" call
return_stmt  = "return" expr?
skip_stmt    = "skip"
stop_stmt    = "stop"
expr_stmt    = call

block        = "{" statement* "}"
params       = IDENTIFIER ("," IDENTIFIER)*
call         = IDENTIFIER "(" args? ")"
args         = expr ("," expr)*

expr         = or_expr
or_expr      = and_expr ("or" and_expr)*
and_expr     = equality_expr ("and" equality_expr)*
equality_expr = comparison_expr (("==" | "!=") comparison_expr)*
comparison_expr = term_expr ((">" | "<" | ">=" | "<=") term_expr)*
term_expr    = factor_expr (("+" | "-") factor_expr)*
factor_expr  = unary_expr (("*" | "/" | "%") unary_expr)*
unary_expr   = ("-" | "+" | "not") unary_expr | primary
primary      = NUMBER | STRING | "yes" | "no" | "empty"
             | IDENTIFIER | call | "(" expr ")"
```
