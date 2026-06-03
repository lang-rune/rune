#!/usr/bin/env python3
import sys
import os
import unittest
from io import StringIO

# Insert rune-lang/ (grandparent of this file) so `import rune` resolves correctly
# and never shadows the stdlib `ast` module.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rune.lexer import Lexer
from rune.parser import Parser
from rune.runtime import Interpreter


class TestCustomLanguage(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def run_code(self, code: str):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return self.interpreter.run(ast)

    def run_code_raises(self, code: str):
        """Like run_code but propagates RuntimeError instead of printing it."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return self.interpreter.interpret(ast)

    def capture_output(self, code: str):
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            self.run_code(code)
            return captured_output.getvalue().strip()
        finally:
            sys.stdout = old_stdout


class TestLexer(TestCustomLanguage):
    def test_tokenize_numbers(self):
        lexer = Lexer("123 45.67 0")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "123")
        self.assertEqual(tokens[1].value, "45.67")
        self.assertEqual(tokens[2].value, "0")

    def test_tokenize_words(self):
        lexer = Lexer('"hello" \'world\'')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "hello")
        self.assertEqual(tokens[1].value, "world")

    def test_tokenize_booleans(self):
        lexer = Lexer("yes no")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "yes")
        self.assertEqual(tokens[1].value, "no")

    def test_tokenize_operators(self):
        lexer = Lexer("+ - * / == != > <")
        tokens = lexer.tokenize()
        operators = [t.value for t in tokens if t.value]
        expected = ["+", "-", "*", "/", "==", "!=", ">", "<"]
        self.assertEqual(operators, expected)


class TestParser(TestCustomLanguage):
    def test_parse_number_literal(self):
        lexer = Lexer("42")
        parser = Parser(lexer.tokenize())
        ast = parser.parse()
        self.assertEqual(len(ast.statements), 1)

    def test_parse_binary_expression(self):
        lexer = Lexer("5 + 3")
        parser = Parser(lexer.tokenize())
        ast = parser.parse()
        self.assertEqual(len(ast.statements), 1)

    def test_parse_write_statement(self):
        lexer = Lexer('write("hello")')
        parser = Parser(lexer.tokenize())
        ast = parser.parse()
        self.assertEqual(len(ast.statements), 1)


class TestInterpreter(TestCustomLanguage):
    def test_number_operations(self):
        self.assertEqual(self.capture_output('write(5 + 3)'), "8")
        self.assertEqual(self.capture_output('write(10 - 4)'), "6")
        self.assertEqual(self.capture_output('write(6 * 7)'), "42")
        self.assertEqual(self.capture_output('write(15 / 3)'), "5")

    def test_modulo(self):
        self.assertEqual(self.capture_output('write(10 % 3)'), "1")
        self.assertEqual(self.capture_output('write(9 % 3)'), "0")
        self.assertEqual(self.capture_output('write(7 % 4)'), "3")

    def test_unary_minus(self):
        self.assertEqual(self.capture_output('write(-5)'), "-5")
        self.assertEqual(self.capture_output('set x = 3\nwrite(-x)'), "-3")

    def test_comparison_operators(self):
        self.assertEqual(self.capture_output('write(5 >= 5)'), "yes")
        self.assertEqual(self.capture_output('write(4 >= 5)'), "no")
        self.assertEqual(self.capture_output('write(3 <= 5)'), "yes")
        self.assertEqual(self.capture_output('write(6 <= 5)'), "no")
        self.assertEqual(self.capture_output('write(3 != 5)'), "yes")
        self.assertEqual(self.capture_output('write(5 != 5)'), "no")
        self.assertEqual(self.capture_output('write(2 < 5)'), "yes")

    def test_logical_operators(self):
        self.assertEqual(self.capture_output('write(yes and yes)'), "yes")
        self.assertEqual(self.capture_output('write(yes and no)'), "no")
        self.assertEqual(self.capture_output('write(no or yes)'), "yes")
        self.assertEqual(self.capture_output('write(no or no)'), "no")
        self.assertEqual(self.capture_output('write(not yes)'), "no")
        self.assertEqual(self.capture_output('write(not no)'), "yes")

    def test_logical_short_circuit(self):
        self.assertEqual(self.capture_output('write(5 > 3 and 2 < 4)'), "yes")
        self.assertEqual(self.capture_output('write(5 > 3 or 2 > 4)'), "yes")

    def test_division_by_zero(self):
        with self.assertRaises(Exception):
            self.run_code_raises('write(1 / 0)')

    def test_undefined_variable(self):
        with self.assertRaises(Exception):
            self.run_code_raises('write(undefined_var)')

    def test_string_operations(self):
        self.assertEqual(self.capture_output('write("Hello" + " " + "World")'), "Hello World")
        self.assertEqual(self.capture_output('write("Age: " + 25)'), "Age: 25")

    def test_boolean_operations(self):
        self.assertEqual(self.capture_output('write(5 > 3)'), "yes")
        self.assertEqual(self.capture_output('write(2 > 5)'), "no")
        self.assertEqual(self.capture_output('write(5 == 5)'), "yes")
        self.assertEqual(self.capture_output('write(3 != 5)'), "yes")

    def test_variables(self):
        code = '''
        set name = "Alice"
        set age = 30
        write(name)
        write(age)
        '''
        output = self.capture_output(code)
        lines = output.split('\n')
        self.assertEqual(lines[0], "Alice")
        self.assertEqual(lines[1], "30")

    def test_boolean_literals(self):
        self.assertEqual(self.capture_output('write(yes)'), "yes")
        self.assertEqual(self.capture_output('write(no)'), "no")

    def test_empty_literal(self):
        self.assertEqual(self.capture_output('write(empty)'), "empty")

    def test_if_statement(self):
        code = '''
        set age = 20
        if age > 18 {
            write("Adult")
        } else {
            write("Minor")
        }
        '''
        self.assertEqual(self.capture_output(code), "Adult")

        code = '''
        set age = 15
        if age > 18 {
            write("Adult")
        } else {
            write("Minor")
        }
        '''
        self.assertEqual(self.capture_output(code), "Minor")

    def test_while_loop(self):
        code = '''
        set counter = 0
        while counter < 3 {
            write(counter)
            set counter = counter + 1
        }
        '''
        output = self.capture_output(code)
        self.assertEqual(output.split('\n'), ["0", "1", "2"])

    def test_builtin_functions(self):
        self.assertEqual(self.capture_output('write(type(42))'), "number")
        self.assertEqual(self.capture_output('write(type("hello"))'), "word")
        self.assertEqual(self.capture_output('write(type(yes))'), "boolean")
        self.assertEqual(self.capture_output('write(length("hello"))'), "5")
        self.assertEqual(self.capture_output('write(number("123"))'), "123")
        self.assertEqual(self.capture_output('write(word(123))'), "123")


class TestEdgeCases(TestCustomLanguage):
    def test_empty_program(self):
        output = self.capture_output('')
        self.assertEqual(output, '')

    def test_comment_only(self):
        output = self.capture_output('# this is a comment')
        self.assertEqual(output, '')

    def test_comment_inline(self):
        output = self.capture_output('write("hi") # say hi')
        self.assertEqual(output, 'hi')

    def test_number_builtin_invalid(self):
        with self.assertRaises(Exception):
            self.run_code_raises('write(number("abc"))')

    def test_multiline_write(self):
        output = self.capture_output('write("a", "b", "c")')
        self.assertEqual(output, 'a b c')


class TestComplexPrograms(TestCustomLanguage):
    def test_fibonacci(self):
        code = '''
        set a = 0
        set b = 1
        set idx = 0

        while idx < 5 {
            write(a)
            set temp = a + b
            set a = b
            set b = temp
            set idx = idx + 1
        }
        '''
        output = self.capture_output(code)
        self.assertEqual(output.split('\n'), ["0", "1", "1", "2", "3"])


class TestSpells(TestCustomLanguage):
    def test_spell_definition_and_cast(self):
        code = '''
        spell greet(name) {
            write("Hello " + name)
        }

        cast greet("Rune")
        '''
        self.assertEqual(self.capture_output(code), "Hello Rune")

    def test_spell_return_value(self):
        code = '''
        spell add(a, b) {
            return a + b
        }

        write(add(2, 3))
        '''
        self.assertEqual(self.capture_output(code), "5")

    def test_spell_return_no_value(self):
        code = '''
        spell early_exit(x) {
            if x < 0 {
                return
            }
            write("positive")
        }
        cast early_exit(-1)
        cast early_exit(1)
        '''
        self.assertEqual(self.capture_output(code), "positive")

    def test_spell_wrong_arg_count(self):
        code = '''
        spell add(a, b) {
            return a + b
        }
        write(add(1))
        '''
        with self.assertRaises(Exception):
            self.run_code_raises(code)

    def test_spell_recursive(self):
        code = '''
        spell factorial(n) {
            if n <= 1 {
                return 1
            }
            return n * factorial(n - 1)
        }
        write(factorial(5))
        '''
        self.assertEqual(self.capture_output(code), "120")

    def test_spell_closure_reads_outer_scope(self):
        code = '''
        set bonus = 10

        spell add_bonus(x) {
            return x + bonus
        }

        write(add_bonus(5))
        '''
        self.assertEqual(self.capture_output(code), "15")

    def test_nested_spell_definitions(self):
        code = '''
        spell outer(x) {
            spell inner(y) {
                return y * 2
            }
            return inner(x) + 1
        }
        write(outer(3))
        '''
        self.assertEqual(self.capture_output(code), "7")


class TestLoops(TestCustomLanguage):
    def test_repeat_statement(self):
        code = '''
        set total = 0

        repeat 5 times {
            set total = total + 1
        }

        write(total)
        '''
        self.assertEqual(self.capture_output(code), "5")

    def test_count_statement_with_skip_and_stop(self):
        code = '''
        count from 1 to 6 as i {
            if i == 2 {
                skip
            }

            if i == 5 {
                stop
            }

            write(i)
        }
        '''
        self.assertEqual(self.capture_output(code).split('\n'), ["1", "3", "4"])

    def test_while_skip_and_stop(self):
        code = '''
        set n = 0
        while n < 6 {
            set n = n + 1
            if n == 2 {
                skip
            }
            if n == 5 {
                stop
            }
            write(n)
        }
        '''
        self.assertEqual(self.capture_output(code).split('\n'), ["1", "3", "4"])

    def test_count_descending(self):
        code = '''
        count from 3 to 1 as i {
            write(i)
        }
        '''
        self.assertEqual(self.capture_output(code).split('\n'), ["3", "2", "1"])


class TestOtherwiseChains(TestCustomLanguage):
    def test_otherwise_chain_middle_branch(self):
        code = '''
        set value = 2

        if value == 1 {
            write("one")
        } otherwise value == 2 {
            write("two")
        } otherwise {
            write("other")
        }
        '''
        self.assertEqual(self.capture_output(code), "two")

    def test_otherwise_chain_fallback_branch(self):
        code = '''
        set value = 9

        if value == 1 {
            write("one")
        } otherwise value == 2 {
            write("two")
        } otherwise {
            write("other")
        }
        '''
        self.assertEqual(self.capture_output(code), "other")


if __name__ == '__main__':
    unittest.main()
