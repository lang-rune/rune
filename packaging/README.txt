Rune Programming Language v0.2.0
================================
A beginner-friendly, handcrafted programming language.


QUICK START
-----------
No installation required. Just run:

    rune.exe                          Start the interactive REPL
    rune.exe run examples\hello_world.rune   Run an example


COMMANDS
--------
    rune.exe                          Interactive REPL
    rune.exe repl                     Interactive REPL (explicit)
    rune.exe run <file.rune>          Run a source file
    rune.exe <file.rune>              Run a source file (shorthand)
    rune.exe tokenize <file.rune>     Print the token stream (debug)
    rune.exe ast <file.rune>          Print the syntax tree (debug)
    rune.exe --version                Print version
    rune.exe --help                   Show help


EXAMPLES
--------
The examples\ folder contains runnable programs:

    hello_world.rune    — Hello, World!
    variables.rune      — Variables and types
    conditions.rune     — if / otherwise chains
    functions.rune      — Spells (functions) and recursion
    loops.rune          — while, repeat, count loops
    closures.rune       — Closures and higher-order spells

Run any example:

    rune.exe run examples\functions.rune


LANGUAGE QUICK REFERENCE
-------------------------
Variables:      set name = "Alice"
Output:         write("Hello, " + name)
Conditionals:   if score > 90 { write("A") } otherwise { write("F") }
Loops:          while n > 0 { set n = n - 1 }
                repeat 3 times { write("again") }
                count from 1 to 5 as i { write(i) }
Spells:         spell add(a, b) { return a + b }
                write(add(3, 4))
Types:          number  word  boolean (yes/no)  empty
Built-ins:      write()  type()  length()  number()  word()  input()
Comments:       # this is a comment


SYSTEM REQUIREMENTS
-------------------
Windows 10 or Windows 11 (x64)
No Python installation required.


LICENSE
-------
MIT License — see LICENSE file.


SOURCE CODE
-----------
https://github.com/kjxcodez/rune-lang
