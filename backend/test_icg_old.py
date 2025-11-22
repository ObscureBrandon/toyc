"""Tests for Intermediate Code Generator (ICG)."""
import sys
sys.path.insert(0, ".")

from toyc.parser import parse_code
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator


def test_simple_assignment():
    """Test: x := 5 + 3
    Expected:
      temp1 = #5 + #3
      id1 = temp1  (where id1 represents x)
    """
    code = "x := 5 + 3;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 2
    assert instructions[0].op == "+"
    assert instructions[0].arg1 == "#5"
    assert instructions[0].arg2 == "#3"
    assert instructions[0].result == "temp1"

    assert instructions[1].op == "assign"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].result == "id1"
    
    # Verify identifier mapping
    assert icg_gen.identifier_map == {"x": "id1"}

    print("✓ Simple assignment test passed")


def test_complex_expression():
    """Test: x := 5 + 3 * 2
    Expected:
      temp1 = #3 * #2
      temp2 = #5 + temp1
      x = temp2
    """
    code = "x := 5 + 3 * 2;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 3

    # temp1 = #3 * #2
    assert instructions[0].op == "*"
    assert instructions[0].arg1 == "#3"
    assert instructions[0].arg2 == "#2"
    assert instructions[0].result == "temp1"

    # temp2 = #5 + temp1
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "#5"
    assert instructions[1].arg2 == "temp1"
    assert instructions[1].result == "temp2"

    # x = temp2
    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp2"
    assert instructions[2].result == "x"

    print("✓ Complex expression test passed")


def test_variable_and_literal():
    """Test: x := 10; y := x + 5;
    Expected:
      x = #10
      temp1 = x + #5
      y = temp1
    """
    code = "x := 10; y := x + 5;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 3

    # x = #10
    assert instructions[0].op == "assign"
    assert instructions[0].arg1 == "#10"
    assert instructions[0].result == "x"

    # temp1 = x + #5
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "x"
    assert instructions[1].arg2 == "#5"
    assert instructions[1].result == "temp1"

    # y = temp1
    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp1"
    assert instructions[2].result == "y"

    print("✓ Variable and literal test passed")


def test_float_literal():
    """Test: x := 3.14 + 2.5;
    Expected:
      temp1 = #3.14 + #2.5
      x = temp1
    """
    code = "x := 3.14 + 2.5;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 2
    assert instructions[0].op == "+"
    assert instructions[0].arg1 == "#3.14"
    assert instructions[0].arg2 == "#2.5"
    assert instructions[0].result == "temp1"

    print("✓ Float literal test passed")


def test_int2float_conversion():
    """Test: x := 5 + 3.14;
    Expected:
      temp1 = int2float(#5)
      temp2 = temp1 + #3.14
      x = temp2
    """
    code = "x := 5 + 3.14;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 3

    # temp1 = int2float(#5)
    assert instructions[0].op == "int2float"
    assert instructions[0].arg1 == "#5"
    assert instructions[0].result == "temp1"

    # temp2 = temp1 + #3.14
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].arg2 == "#3.14"
    assert instructions[1].result == "temp2"

    # x = temp2
    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp2"
    assert instructions[2].result == "x"

    print("✓ Int2Float conversion test passed")


def test_if_statement():
    """Test: if (x > 10) then write x; end
    Expected:
      temp1 = x > #10
      if_false temp1 goto L1
      write x
      label L1:
    """
    code = "if (x > 10) then write x; end"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 4

    # temp1 = x > #10
    assert instructions[0].op == ">"
    assert instructions[0].arg1 == "x"
    assert instructions[0].arg2 == "#10"
    assert instructions[0].result == "temp1"

    # if_false temp1 goto L1
    assert instructions[1].op == "if_false"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].arg2 == "L1"

    # write x
    assert instructions[2].op == "write"
    assert instructions[2].arg1 == "x"

    # label L1:
    assert instructions[3].op == "label"
    assert instructions[3].label == "L1"

    print("✓ If statement test passed")


def test_if_else_statement():
    """Test: if (x >= 3) then y := x + 5; else y := 0; end
    Expected:
      temp1 = x >= #3
      if_false temp1 goto L1
      temp2 = x + #5
      y = temp2
      goto L2
      label L1:
      y = #0
      label L2:
    """
    code = "if (x >= 3) then y := x + 5; else y := 0; end"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 8

    # temp1 = x >= #3
    assert instructions[0].op == ">="
    assert instructions[0].arg1 == "x"
    assert instructions[0].arg2 == "#3"

    # if_false temp1 goto L1
    assert instructions[1].op == "if_false"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].arg2 == "L1"

    # temp2 = x + #5
    assert instructions[2].op == "+"
    assert instructions[2].arg1 == "x"
    assert instructions[2].arg2 == "#5"

    # y = temp2
    assert instructions[3].op == "assign"
    assert instructions[3].arg1 == "temp2"
    assert instructions[3].result == "y"

    # goto L2
    assert instructions[4].op == "goto"
    assert instructions[4].arg1 == "L2"

    # label L1:
    assert instructions[5].op == "label"
    assert instructions[5].label == "L1"

    # y = #0
    assert instructions[6].op == "assign"
    assert instructions[6].arg1 == "#0"
    assert instructions[6].result == "y"

    # label L2:
    assert instructions[7].op == "label"
    assert instructions[7].label == "L2"

    print("✓ If-else statement test passed")


def test_repeat_until():
    """Test: repeat x := x + 1; until x > 10;
    Expected:
      label L1:
      temp1 = x + #1
      x = temp1
      temp2 = x > #10
      if_false temp2 goto L1
    """
    code = "repeat x := x + 1; until x > 10;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 5

    # label L1:
    assert instructions[0].op == "label"
    assert instructions[0].label == "L1"

    # temp1 = x + #1
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "x"
    assert instructions[1].arg2 == "#1"
    assert instructions[1].result == "temp1"

    # x = temp1
    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp1"
    assert instructions[2].result == "x"

    # temp2 = x > #10
    assert instructions[3].op == ">"
    assert instructions[3].arg1 == "x"
    assert instructions[3].arg2 == "#10"
    assert instructions[3].result == "temp2"

    # if_false temp2 goto L1
    assert instructions[4].op == "if_false"
    assert instructions[4].arg1 == "temp2"
    assert instructions[4].arg2 == "L1"

    print("✓ Repeat-until test passed")


def test_read_write():
    """Test: read x; write x * 2;
    Expected:
      read x
      temp1 = x * #2
      write temp1
    """
    code = "read x; write x * 2;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 3

    # read x
    assert instructions[0].op == "read"
    assert instructions[0].arg1 == "x"

    # temp1 = x * #2
    assert instructions[1].op == "*"
    assert instructions[1].arg1 == "x"
    assert instructions[1].arg2 == "#2"
    assert instructions[1].result == "temp1"

    # write temp1
    assert instructions[2].op == "write"
    assert instructions[2].arg1 == "temp1"

    print("✓ Read/Write test passed")


def test_modulo_operation():
    """Test: result := 10 + 5 * 2 % 3;
    Expected:
      temp1 = #5 * #2
      temp2 = temp1 % #3
      temp3 = #10 + temp2
      result = temp3
    """
    code = "result := 10 + 5 * 2 % 3;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 4

    # temp1 = #5 * #2
    assert instructions[0].op == "*"
    assert instructions[0].arg1 == "#5"
    assert instructions[0].arg2 == "#2"

    # temp2 = temp1 % #3
    assert instructions[1].op == "%"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].arg2 == "#3"

    # temp3 = #10 + temp2
    assert instructions[2].op == "+"
    assert instructions[2].arg1 == "#10"
    assert instructions[2].arg2 == "temp2"

    # result = temp3
    assert instructions[3].op == "assign"
    assert instructions[3].arg1 == "temp3"
    assert instructions[3].result == "result"

    print("✓ Modulo operation test passed")


if __name__ == "__main__":
    print("Running ICG tests...\n")
    test_simple_assignment()
    test_complex_expression()
    test_variable_and_literal()
    test_float_literal()
    test_int2float_conversion()
    test_if_statement()
    test_if_else_statement()
    test_repeat_until()
    test_read_write()
    test_modulo_operation()
    print("\n✅ All ICG tests passed!")
