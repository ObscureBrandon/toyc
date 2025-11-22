"""Tests for Intermediate Code Generator (ICG) with normalized identifiers."""
import sys
sys.path.insert(0, ".")

from toyc.parser import parse_code
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator


def test_simple_assignment():
    """Test: x := 5 + 3
    Expected:
      temp1 = #5 + #3
      id1 = temp1
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
    
    assert icg_gen.identifier_map == {"x": "id1"}
    print("✓ Simple assignment test passed")


def test_complex_expression():
    """Test: x := 5 + 3 * 2
    Expected:
      temp1 = #3 * #2
      temp2 = #5 + temp1
      id1 = temp2
    """
    code = "x := 5 + 3 * 2;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 3
    assert instructions[0].op == "*"
    assert instructions[0].result == "temp1"

    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "#5"
    assert instructions[1].arg2 == "temp1"
    assert instructions[1].result == "temp2"

    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp2"
    assert instructions[2].result == "id1"

    print("✓ Complex expression test passed")


def test_variable_and_literal():
    """Test: y := x + 5
    Expected:
      temp1 = id1 + #5
      id2 = temp1
    """
    code = "x := 10; y := x + 5;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    # First assignment: x := 10
    assert instructions[0].op == "assign"
    assert instructions[0].arg1 == "#10"
    assert instructions[0].result == "id1"

    # Second assignment: y := x + 5
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "id1"  # x is id1
    assert instructions[1].arg2 == "#5"
    assert instructions[1].result == "temp1"

    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp1"
    assert instructions[2].result == "id2"  # y is id2

    assert icg_gen.identifier_map == {"x": "id1", "y": "id2"}
    print("✓ Variable and literal test passed")


def test_float_literal():
    """Test: result := 3.14 * 2.0"""
    code = "result := 3.14 * 2.0;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 2
    assert instructions[0].op == "*"
    assert instructions[0].arg1 == "#3.14"
    assert instructions[0].arg2 == "#2.0"
    assert instructions[0].result == "temp1"

    assert instructions[1].op == "assign"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].result == "id1"

    print("✓ Float literal test passed")


def test_int2float_conversion():
    """Test: result := 5 + 3.14 (requires int to float conversion)"""
    code = "result := 5 + 3.14;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    # Should have: int2float conversion, addition, assignment
    assert len(instructions) == 3
    
    # int2float(#5)
    assert instructions[0].op == "int2float"
    assert instructions[0].arg1 == "#5"
    assert instructions[0].result == "temp1"
    
    # temp2 = temp1 + #3.14
    assert instructions[1].op == "+"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].arg2 == "#3.14"
    assert instructions[1].result == "temp2"
    
    # id1 = temp2
    assert instructions[2].op == "assign"
    assert instructions[2].arg1 == "temp2"
    assert instructions[2].result == "id1"

    print("✓ Int2float conversion test passed")


def test_if_statement():
    """Test: if (x > 5) then y := 10; end"""
    code = "x := 3; if (x > 5) then y := 10; end"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    # x := 3
    assert instructions[0].op == "assign"
    assert instructions[0].arg1 == "#3"
    assert instructions[0].result == "id1"

    # temp1 = x > #5
    assert instructions[1].op == ">"
    assert instructions[1].arg1 == "id1"
    assert instructions[1].arg2 == "#5"
    assert instructions[1].result == "temp1"

    # if_false temp1 goto L1
    assert instructions[2].op == "if_false"
    assert instructions[2].arg1 == "temp1"
    assert instructions[2].arg2 == "L1"

    # y := 10
    assert instructions[3].op == "assign"
    assert instructions[3].arg1 == "#10"
    assert instructions[3].result == "id2"

    # label L1:
    assert instructions[4].op == "label"
    assert instructions[4].label == "L1"

    print("✓ If statement test passed")


def test_if_else_statement():
    """Test: if (x >= 3) then read y; else write x % 2; end"""
    code = "x := 5; if (x >= 3) then read y; else write x % 2; end"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    # x := 5
    assert instructions[0].op == "assign"
    assert instructions[0].result == "id1"

    # temp1 = x >= #3
    assert instructions[1].op == ">="
    assert instructions[1].arg1 == "id1"

    # if_false temp1 goto L1
    assert instructions[2].op == "if_false"

    # read y
    assert instructions[3].op == "read"
    assert instructions[3].arg1 == "id2"

    # goto L2
    assert instructions[4].op == "goto"

    # label L1:
    assert instructions[5].op == "label"

    # temp2 = x % #2
    assert instructions[6].op == "%"
    assert instructions[6].arg1 == "id1"

    # write temp2
    assert instructions[7].op == "write"
    assert instructions[7].arg1 == "temp2"

    # label L2:
    assert instructions[8].op == "label"

    print("✓ If-else statement test passed")


def test_repeat_until():
    """Test: repeat z := z + 1; until z != 10;"""
    code = "z := 0; repeat z := z + 1; until z != 10;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    # z := 0
    assert instructions[0].op == "assign"
    assert instructions[0].result == "id1"

    # label L1:
    assert instructions[1].op == "label"
    assert instructions[1].label == "L1"

    # temp1 = z + #1
    assert instructions[2].op == "+"
    assert instructions[2].arg1 == "id1"

    # z = temp1
    assert instructions[3].op == "assign"
    assert instructions[3].arg1 == "temp1"
    assert instructions[3].result == "id1"

    # temp2 = z != #10
    assert instructions[4].op == "!="
    assert instructions[4].arg1 == "id1"

    # if_false temp2 goto L1
    assert instructions[5].op == "if_false"
    assert instructions[5].arg2 == "L1"

    print("✓ Repeat-until test passed")


def test_read_write():
    """Test: read x; write x;"""
    code = "read x; write x;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 2

    # read x
    assert instructions[0].op == "read"
    assert instructions[0].arg1 == "id1"

    # write x
    assert instructions[1].op == "write"
    assert instructions[1].arg1 == "id1"

    assert icg_gen.identifier_map == {"x": "id1"}
    print("✓ Read/write test passed")


def test_modulo_operation():
    """Test: result := 10 % 3;"""
    code = "result := 10 % 3;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)

    assert len(instructions) == 2
    
    # temp1 = #10 % #3
    assert instructions[0].op == "%"
    assert instructions[0].arg1 == "#10"
    assert instructions[0].arg2 == "#3"
    assert instructions[0].result == "temp1"
    
    # id1 = temp1
    assert instructions[1].op == "assign"
    assert instructions[1].arg1 == "temp1"
    assert instructions[1].result == "id1"

    print("✓ Modulo operation test passed")


if __name__ == "__main__":
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
