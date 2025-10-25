from toyc.parser import parse_code
from toyc.ast import (
    AssignmentNode,
    BlockNode,
    IfNode,
    RepeatUntilNode,
    ReadNode,
    WriteNode,
    BinaryOpNode,
    NumberNode,
)


def test_assignment():
    code = "x := 5;"
    ast = parse_code(code)
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert isinstance(stmt, AssignmentNode)
    assert stmt.identifier == "x"
    assert isinstance(stmt.value, NumberNode)
    assert stmt.value.value == 5
    print("✓ Assignment test passed")


def test_arithmetic_operators():
    code = "result := 10 + 5 * 2 % 3;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, AssignmentNode)
    print("✓ Arithmetic operators test passed")


def test_comparison_operators():
    code = "x := 5 < 10;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, AssignmentNode)
    assert isinstance(stmt.value, BinaryOpNode)
    assert stmt.value.operator == "<"
    print("✓ Comparison operators test passed")


def test_logical_operators():
    code = "x := 5 > 3 && 10 < 20;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, AssignmentNode)
    assert isinstance(stmt.value, BinaryOpNode)
    assert stmt.value.operator == "&&"
    print("✓ Logical operators test passed")


def test_if_statement_with_else():
    code = """
    if (x >= 3)
        write 10;
    else
        write 20;
    end
    """
    ast = parse_code(code)
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert stmt.condition is not None
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 1
    assert isinstance(stmt.else_branch, BlockNode)
    assert len(stmt.else_branch.statements) == 1
    print("✓ If-else statement test passed")


def test_if_statement_without_else():
    code = """
    if (x > 0)
        write x;
    end
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert stmt.condition is not None
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 1
    assert stmt.else_branch is None
    print("✓ If statement (no else) test passed")


def test_repeat_until():
    code = """
    repeat
        z := z + 1;
    until z != 10;
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, RepeatUntilNode)
    assert isinstance(stmt.body, BlockNode)
    assert len(stmt.body.statements) == 1
    assert stmt.condition is not None
    print("✓ Repeat-until test passed")


def test_read_statement():
    code = "read x;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, ReadNode)
    assert stmt.identifier == "x"
    print("✓ Read statement test passed")


def test_write_statement():
    code = "write x * 2;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, WriteNode)
    assert isinstance(stmt.expression, BinaryOpNode)
    print("✓ Write statement test passed")


def test_complex_program():
    code = """
    x := 5;
    if (x >= 3)
        read y;
    else
        write x % 2;
    end
    repeat
        z := z + 1;
    until z != 10;
    """
    ast = parse_code(code)
    assert len(ast.statements) == 3
    assert isinstance(ast.statements[0], AssignmentNode)
    assert isinstance(ast.statements[1], IfNode)
    assert isinstance(ast.statements[2], RepeatUntilNode)
    print("✓ Complex program test passed")


def test_expression_precedence():
    code = "x := 1 + 2 * 3;"
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, AssignmentNode)
    value = stmt.value
    assert isinstance(value, BinaryOpNode)
    assert value.operator == "+"
    assert isinstance(value.right, BinaryOpNode)
    assert value.right.operator == "*"
    print("✓ Expression precedence test passed")


def test_multi_statement_if_block():
    code = """
    if (x > 0)
        read y;
        write y;
        z := y + 1;
    end
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 3
    assert isinstance(stmt.then_branch.statements[0], ReadNode)
    assert isinstance(stmt.then_branch.statements[1], WriteNode)
    assert isinstance(stmt.then_branch.statements[2], AssignmentNode)
    print("✓ Multi-statement if block test passed")


def test_multi_statement_if_else_blocks():
    code = """
    if (x > 0)
        read y;
        write y;
    else
        write 0;
        z := 1;
    end
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 2
    assert isinstance(stmt.else_branch, BlockNode)
    assert len(stmt.else_branch.statements) == 2
    print("✓ Multi-statement if-else blocks test passed")


def test_multi_statement_repeat_block():
    code = """
    repeat
        read x;
        y := x * 2;
        write y;
        z := z + 1;
    until z >= 10;
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, RepeatUntilNode)
    assert isinstance(stmt.body, BlockNode)
    assert len(stmt.body.statements) == 4
    assert isinstance(stmt.body.statements[0], ReadNode)
    assert isinstance(stmt.body.statements[1], AssignmentNode)
    assert isinstance(stmt.body.statements[2], WriteNode)
    assert isinstance(stmt.body.statements[3], AssignmentNode)
    print("✓ Multi-statement repeat block test passed")


def test_nested_if_statements():
    code = """
    if (x > 0)
        if (y > 0)
            write 1;
        end
        write 2;
    end
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 2
    assert isinstance(stmt.then_branch.statements[0], IfNode)
    assert isinstance(stmt.then_branch.statements[1], WriteNode)
    print("✓ Nested if statements test passed")


def test_nested_repeat_in_if():
    code = """
    if (x > 0)
        repeat
            write i;
            i := i + 1;
        until i >= 10;
    end
    """
    ast = parse_code(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfNode)
    assert isinstance(stmt.then_branch, BlockNode)
    assert len(stmt.then_branch.statements) == 1
    assert isinstance(stmt.then_branch.statements[0], RepeatUntilNode)
    nested_repeat = stmt.then_branch.statements[0]
    assert isinstance(nested_repeat.body, BlockNode)
    assert len(nested_repeat.body.statements) == 2
    print("✓ Nested repeat in if test passed")


if __name__ == "__main__":
    test_assignment()
    test_arithmetic_operators()
    test_comparison_operators()
    test_logical_operators()
    test_if_statement_with_else()
    test_if_statement_without_else()
    test_repeat_until()
    test_read_statement()
    test_write_statement()
    test_complex_program()
    test_expression_precedence()
    test_multi_statement_if_block()
    test_multi_statement_if_else_blocks()
    test_multi_statement_repeat_block()
    test_nested_if_statements()
    test_nested_repeat_in_if()
    print("\n✅ All parser tests passed!")
