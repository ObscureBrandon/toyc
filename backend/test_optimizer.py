"""Tests for Code Optimizer."""
import sys
sys.path.insert(0, ".")

from toyc.parser import parse_code
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator
from toyc.optimizer import Optimizer


def test_int2float_constant_inlining():
    """Test: int2float with constant should be folded to #N.0
    
    Before:
    temp1 = int2float(#5)
    temp2 = temp1 + #3.14
    id1 = temp2
    
    After:
    id1 = #5.0 + #3.14
    """
    code = "result := 5 + 3.14;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: int2float constant inlining ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should have only 1 instruction: id1 = #5.0 + #3.14
    assert len(optimized) == 1, f"Expected 1 instruction, got {len(optimized)}"
    assert optimized[0].op == "+"
    assert optimized[0].arg1 == "#5.0"
    assert optimized[0].arg2 == "#3.14"
    assert optimized[0].result == "id1"
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")
    print(f"✓ int2float operations inlined: {optimizer.stats.int2float_inlined}")


def test_int2float_variable_annotation():
    """Test: int2float with variable should use (f) annotation
    
    Before:
    temp1 = int2float(id1)
    temp2 = temp1 + #3.14
    id2 = temp2
    
    After:
    id2 = id1(f) + #3.14
    """
    code = "x := 5; y := x + 3.14;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: int2float variable annotation ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should have 2 instructions: id1 = #5 and id2 = id1(f) + #3.14
    assert len(optimized) == 2, f"Expected 2 instructions, got {len(optimized)}"
    assert optimized[0].op == "assign"
    assert optimized[0].arg1 == "#5"
    assert optimized[0].result == "id1"
    
    assert optimized[1].op == "+"
    assert optimized[1].arg1 == "id1(f)"
    assert optimized[1].arg2 == "#3.14"
    assert optimized[1].result == "id2"
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")


def test_simple_temp_elimination():
    """Test: Eliminate single-use temporaries
    
    Before:
    temp1 = #3 * #2
    temp2 = #5 + temp1
    id1 = temp2
    
    After:
    temp1 = #3 * #2
    id1 = #5 + temp1
    """
    code = "x := 5 + 3 * 2;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Simple temp elimination ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should eliminate temp2
    assert len(optimized) == 2, f"Expected 2 instructions, got {len(optimized)}"
    assert optimized[0].op == "*"
    assert optimized[1].op == "+"
    assert optimized[1].result == "id1"
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")


def test_algebraic_simplification_add_zero():
    """Test: x + 0 -> x"""
    code = "x := 5; y := x + 0;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Algebraic simplification (x + 0) ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should simplify to: id1 = #5; id2 = id1
    assert optimized[1].op == "assign"
    assert optimized[1].arg1 == "id1"
    assert optimized[1].result == "id2"
    
    print(f"✓ Algebraic simplifications: {optimizer.stats.algebraic_simplifications}")


def test_algebraic_simplification_mul_one():
    """Test: x * 1 -> x"""
    code = "x := 5; y := x * 1;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Algebraic simplification (x * 1) ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should simplify to: id1 = #5; id2 = id1
    assert optimized[1].op == "assign"
    assert optimized[1].arg1 == "id1"
    
    print(f"✓ Algebraic simplifications: {optimizer.stats.algebraic_simplifications}")


def test_algebraic_simplification_mul_zero():
    """Test: x * 0 -> 0"""
    code = "x := 5; y := x * 0;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Algebraic simplification (x * 0) ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should simplify to: id1 = #5; id2 = #0
    assert optimized[1].op == "assign"
    assert optimized[1].arg1 == "#0"
    
    print(f"✓ Algebraic simplifications: {optimizer.stats.algebraic_simplifications}")


def test_if_statement_optimization():
    """Test: Optimization with control flow (if statement)"""
    code = "x := 3; if (x > 5) then y := 10; end"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: If statement optimization ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Labels and control flow should be preserved
    label_count = sum(1 for instr in optimized if instr.op == "label")
    assert label_count == 1, f"Expected 1 label, got {label_count}"
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")


def test_repeat_until_optimization():
    """Test: Optimization with repeat-until loop"""
    code = "z := 0; repeat z := z + 1; until z != 10;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Repeat-until optimization ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Labels and control flow should be preserved
    label_count = sum(1 for instr in optimized if instr.op == "label")
    assert label_count == 1, f"Expected 1 label, got {label_count}"
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")


def test_read_write_preserved():
    """Test: Read/write operations are preserved"""
    code = "read x; write x;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Read/write preservation ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    # Should have exactly 2 instructions: read and write
    assert len(optimized) == 2
    assert optimized[0].op == "read"
    assert optimized[1].op == "write"
    
    print(f"✓ Read/write operations preserved")


def test_complex_expression_optimization():
    """Test: Complex expression with multiple temps"""
    code = "result := 10 + 5 * 2;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Complex expression optimization ===")
    print("Before optimization:")
    for i, instr in enumerate(instructions):
        print(f"  {i+1}. {instr}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print("\nAfter optimization:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print(f"✓ Instructions reduced from {len(instructions)} to {len(optimized)}")
    print(f"✓ Optimization stats:")
    print(f"  - Temps eliminated: {optimizer.stats.temps_eliminated}")
    print(f"  - Reduction: {optimizer.stats.reduction_percentage:.1f}%")


def test_optimization_statistics():
    """Test: Verify optimization statistics are tracked correctly"""
    code = "x := 5 + 3 * 2; y := x + 0;"
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print("\n=== Test: Optimization statistics ===")
    print(f"Original instruction count: {len(instructions)}")
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    print(f"Optimized instruction count: {len(optimized)}")
    print(f"\nOptimization Statistics:")
    print(f"  - Instructions saved: {optimizer.stats.instructions_saved}")
    print(f"  - Temps eliminated: {optimizer.stats.temps_eliminated}")
    print(f"  - Algebraic simplifications: {optimizer.stats.algebraic_simplifications}")
    print(f"  - Reduction percentage: {optimizer.stats.reduction_percentage:.1f}%")
    
    assert optimizer.stats.original_instruction_count == len(instructions)
    assert optimizer.stats.optimized_instruction_count == len(optimized)
    assert optimizer.stats.instructions_saved >= 0
    
    print("✓ Statistics tracking works correctly")


if __name__ == "__main__":
    test_int2float_constant_inlining()
    test_int2float_variable_annotation()
    test_simple_temp_elimination()
    test_algebraic_simplification_add_zero()
    test_algebraic_simplification_mul_one()
    test_algebraic_simplification_mul_zero()
    test_if_statement_optimization()
    test_repeat_until_optimization()
    test_read_write_preserved()
    test_complex_expression_optimization()
    test_optimization_statistics()
    print("\n" + "="*50)
    print("✅ All optimizer tests passed!")
    print("="*50)
