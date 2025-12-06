"""Tests for Code Generator."""
import sys
sys.path.insert(0, ".")

from toyc.parser import parse_code
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator
from toyc.optimizer import Optimizer
from toyc.code_generator import CodeGenerator, AssemblyInstruction


def run_pipeline(code: str) -> tuple:
    """Run the full pipeline and return (optimized_tac, assembly, type_map)."""
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    
    icg_gen = ICGGenerator(symbol_table=analyzer.symbol_table)
    instructions = icg_gen.generate(analyzed_ast)
    
    optimizer = Optimizer()
    optimized = optimizer.optimize(instructions)
    
    codegen = CodeGenerator(type_map=icg_gen.type_map)
    assembly = codegen.generate(optimized)
    
    return optimized, assembly, icg_gen.type_map


def test_simple_int_assignment():
    """Test: Simple integer assignment generates STR with literal."""
    code = "x := 5;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Simple integer assignment ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Expected: STR id1, #5
    assert len(assembly) == 1, f"Expected 1 instruction, got {len(assembly)}"
    assert assembly[0].op == "STR"
    assert assembly[0].operands == ["id1", "#5"]
    
    print("PASS: STR id1, #5")


def test_simple_float_assignment():
    """Test: Simple float assignment generates STRF with literal."""
    code = "x := 3.14;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Simple float assignment ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Expected: STRF id1, #3.14
    assert len(assembly) == 1, f"Expected 1 instruction, got {len(assembly)}"
    assert assembly[0].op == "STRF"
    assert assembly[0].operands == ["id1", "#3.14"]
    
    print("PASS: STRF id1, #3.14")


def test_variable_to_variable_assignment():
    """Test: Assignment from variable uses LOAD and STR."""
    code = "x := 5; y := x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Variable to variable assignment ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Expected: STR id1, #5; LOAD R1, id1; STR id2, R1
    assert len(assembly) == 3, f"Expected 3 instructions, got {len(assembly)}"
    assert assembly[0].op == "STR"
    assert assembly[1].op == "LOAD"
    assert assembly[1].operands == ["R1", "id1"]
    assert assembly[2].op == "STR"
    assert assembly[2].operands == ["id2", "R1"]
    
    print("PASS: STR id1, #5; LOAD R1, id1; STR id2, R1")


def test_int_addition_with_literal():
    """Test: Integer addition with literal on right side."""
    code = "x := 5; y := x + 3;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Integer addition with literal ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # First instruction: STR id1, #5
    # Then: LOAD R1, id1; ADD R1, R1, #3; STR id2, R1
    assert assembly[0].op == "STR"
    
    # Find the ADD instruction
    add_instrs = [a for a in assembly if a.op == "ADD"]
    assert len(add_instrs) == 1
    assert add_instrs[0].operands[0] == "R1"
    assert add_instrs[0].operands[1] == "R1"
    assert add_instrs[0].operands[2] == "#3"
    
    print("PASS: Generates LOAD, ADD with literal, STR sequence")


def test_float_addition():
    """Test: Float addition uses LOADF, ADDF, STRF."""
    code = "x := 3.14; y := x + 2.0;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Float addition ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Check for float instructions
    float_ops = [a for a in assembly if a.op.endswith("F")]
    assert len(float_ops) >= 2, f"Expected at least 2 float ops, got {len(float_ops)}"
    
    # Should have LOADF, ADDF, STRF
    ops = [a.op for a in assembly]
    assert "LOADF" in ops or "STRF" in ops
    assert "ADDF" in ops
    
    print("PASS: Uses float instructions (LOADF, ADDF, STRF)")


def test_commutative_swap_addition():
    """Test: Commutative operation swaps operands when literal is first."""
    code = "x := 5; y := 3 + x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Commutative swap (addition) ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # For y := 3 + x, since + is commutative:
    # Should swap to: LOAD R1, id1; ADD R1, R1, #3 (not LOAD R1, #3; LOAD R2, id1; ADD...)
    add_instrs = [a for a in assembly if a.op == "ADD"]
    assert len(add_instrs) == 1
    
    # The third operand should be the literal #3
    assert add_instrs[0].operands[2] == "#3"
    
    # Should NOT have two LOADs before ADD (indicating swap happened)
    # Check that we don't use R2 in the sequence
    add_idx = assembly.index(add_instrs[0])
    if add_idx > 0:
        prev = assembly[add_idx - 1]
        # Should be LOAD R1, id1 (not LOAD R2)
        assert prev.op == "LOAD"
        assert prev.operands[0] == "R1"
    
    print("PASS: Swapped operands for commutative operation")


def test_commutative_swap_multiplication():
    """Test: Commutative operation swaps operands for multiplication."""
    code = "x := 5; y := 2 * x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Commutative swap (multiplication) ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # For y := 2 * x, since * is commutative:
    # Should swap to: LOAD R1, id1; MUL R1, R1, #2
    mul_instrs = [a for a in assembly if a.op == "MUL"]
    assert len(mul_instrs) == 1
    assert mul_instrs[0].operands[2] == "#2"
    
    print("PASS: Swapped operands for commutative multiplication")


def test_non_commutative_subtraction():
    """Test: Non-commutative operation requires both registers when literal first."""
    code = "x := 5; y := 10 - x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Non-commutative subtraction ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # For y := 10 - x with literal first:
    # Must use: LOAD R1, #10; LOAD R2, id1; SUB R1, R1, R2; STR id2, R1
    sub_instrs = [a for a in assembly if a.op == "SUB"]
    assert len(sub_instrs) == 1
    
    # Should use R1, R1, R2 (both registers)
    assert sub_instrs[0].operands == ["R1", "R1", "R2"]
    
    print("PASS: Non-commutative uses both registers")


def test_non_commutative_division():
    """Test: Division with literal first uses both registers."""
    code = "x := 2; y := 10 / x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Non-commutative division ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    div_instrs = [a for a in assembly if a.op == "DIV"]
    assert len(div_instrs) == 1
    assert div_instrs[0].operands == ["R1", "R1", "R2"]
    
    print("PASS: Division uses both registers when literal first")


def test_modulo_operation():
    """Test: Modulo operation generates MOD instruction."""
    code = "x := 10; y := x % 3;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Modulo operation ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    mod_instrs = [a for a in assembly if a.op == "MOD"]
    assert len(mod_instrs) == 1
    assert mod_instrs[0].operands[2] == "#3"
    
    print("PASS: Modulo generates MOD instruction")


def test_two_variable_addition():
    """Test: Adding two variables uses both registers."""
    code = "x := 5; y := 3; z := x + y;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Two variable addition ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    add_instrs = [a for a in assembly if a.op == "ADD"]
    assert len(add_instrs) == 1
    
    # Should be: LOAD R1, id1; LOAD R2, id2; ADD R1, R1, R2
    assert add_instrs[0].operands == ["R1", "R1", "R2"]
    
    print("PASS: Two variables use LOAD R1, LOAD R2, ADD R1, R1, R2")


def test_mixed_type_operation():
    """Test: Mixed int/float operation uses float instructions."""
    code = "x := 5 + 3.14;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Mixed type operation ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should use float instructions due to type coercion
    ops = [a.op for a in assembly]
    # At least one float operation
    float_ops = [op for op in ops if op.endswith("F")]
    assert len(float_ops) >= 1, f"Expected float operations, got {ops}"
    
    print("PASS: Mixed types use float instructions")


def test_float_annotation_from_optimizer():
    """Test: Handles id1(f) annotation from optimizer."""
    code = "x := 5; y := x + 3.14;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Float annotation from optimizer ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Check that we have ADDF for the float operation
    add_f_instrs = [a for a in assembly if a.op == "ADDF"]
    assert len(add_f_instrs) == 1
    
    print("PASS: Handles (f) annotation correctly")


def test_complex_expression():
    """Test: Complex expression with multiple operations."""
    code = "result := 10 + 5 * 2;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Complex expression ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should have MUL and ADD
    mul_instrs = [a for a in assembly if a.op == "MUL"]
    add_instrs = [a for a in assembly if a.op == "ADD"]
    
    assert len(mul_instrs) == 1, f"Expected 1 MUL, got {len(mul_instrs)}"
    assert len(add_instrs) == 1, f"Expected 1 ADD, got {len(add_instrs)}"
    
    print("PASS: Complex expression generates correct operations")


def test_multiple_statements():
    """Test: Multiple statements generate correct sequence."""
    code = "a := 1; b := 2; c := a + b;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Multiple statements ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Count operations
    str_count = len([a for a in assembly if a.op == "STR"])
    load_count = len([a for a in assembly if a.op == "LOAD"])
    add_count = len([a for a in assembly if a.op == "ADD"])
    
    assert str_count == 3, f"Expected 3 STR, got {str_count}"
    assert load_count == 2, f"Expected 2 LOAD, got {load_count}"
    assert add_count == 1, f"Expected 1 ADD, got {add_count}"
    
    print("PASS: Multiple statements generate correct sequence")


def test_assembly_instruction_str():
    """Test: AssemblyInstruction __str__ method."""
    instr = AssemblyInstruction(op="LOAD", operands=["R1", "id1"])
    assert str(instr) == "LOAD R1, id1"
    
    instr2 = AssemblyInstruction(op="ADD", operands=["R1", "R1", "#5"])
    assert str(instr2) == "ADD R1, R1, #5"
    
    print("\n=== Test: AssemblyInstruction __str__ ===")
    print(f"  LOAD R1, id1 -> {instr}")
    print(f"  ADD R1, R1, #5 -> {instr2}")
    print("PASS: __str__ formats correctly")


def test_control_flow_skipped():
    """Test: Control flow instructions (if, goto, label) are skipped."""
    code = "x := 5; if (x > 3) then y := 10; end"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Control flow skipped ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should NOT have label, goto, if_false in assembly
    for instr in assembly:
        assert instr.op not in ["label", "goto", "if_false", "if_true", ">"]
    
    # But should still have STR for the assignments
    str_count = len([a for a in assembly if a.op == "STR"])
    assert str_count >= 1
    
    print("PASS: Control flow instructions are skipped")


def test_io_skipped():
    """Test: I/O instructions (read, write) are skipped."""
    code = "x := 5; read y; write x;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: I/O skipped ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should NOT have read or write in assembly
    for instr in assembly:
        assert instr.op not in ["read", "write"]
    
    print("PASS: I/O instructions are skipped")


def test_empty_input():
    """Test: Empty instruction list returns empty assembly."""
    codegen = CodeGenerator(type_map={})
    assembly = codegen.generate([])
    
    print("\n=== Test: Empty input ===")
    assert len(assembly) == 0
    print("PASS: Empty input returns empty assembly")


def test_temps_stay_in_registers():
    """Test: Temporaries stay in registers - no intermediate STR.
    
    For x := y * (z - 2), should generate:
    LOAD R1, id3
    SUB R1, R1, #2
    LOAD R2, id2
    MUL R1, R2, R1
    STR id1, R1
    
    NOT:
    LOAD R1, id3
    SUB R1, R1, #2
    STR temp1, R1      <- WRONG
    LOAD R1, id2
    LOAD R2, temp1     <- WRONG
    MUL R1, R1, R2
    STR id1, R1
    """
    code = "x := y * (z - 2);"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Temps stay in registers ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should have exactly ONE STR instruction (for the final result)
    str_instrs = [a for a in assembly if a.op == "STR"]
    assert len(str_instrs) == 1, f"Expected 1 STR, got {len(str_instrs)}: {[str(s) for s in str_instrs]}"
    
    # The STR should be for id1, not any temp
    assert str_instrs[0].operands[0] == "id1", f"Expected STR to id1, got {str_instrs[0]}"
    
    # Should have SUB and MUL operations
    sub_instrs = [a for a in assembly if a.op == "SUB"]
    mul_instrs = [a for a in assembly if a.op == "MUL"]
    assert len(sub_instrs) == 1
    assert len(mul_instrs) == 1
    
    # Verify no temp appears in any STR or LOAD operand
    for instr in assembly:
        for operand in instr.operands:
            if operand.startswith("temp"):
                assert False, f"Found temp in assembly: {instr}"
    
    print("PASS: Only one STR for final result, temps stay in registers")


def test_nested_expression():
    """Test: Nested expression (a + b) * (c - d) generates minimal stores."""
    code = "a := 1; b := 2; c := 3; d := 4; result := (a + b) * (c - d);"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Nested expression ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Count STR instructions - should be exactly 5 (one per variable: a, b, c, d, result)
    str_instrs = [a for a in assembly if a.op == "STR"]
    assert len(str_instrs) == 5, f"Expected 5 STR (one per variable), got {len(str_instrs)}"
    
    # Verify stored variables are id1-id5, not temps
    stored_vars = [s.operands[0] for s in str_instrs]
    for var in stored_vars:
        assert var.startswith("id"), f"Expected id, got {var}"
    
    print("PASS: Nested expression has minimal stores")


def test_chained_operations():
    """Test: Chained operations a + b + c generate minimal stores."""
    code = "a := 1; b := 2; c := 3; result := a + b + c;"
    optimized, assembly, type_map = run_pipeline(code)
    
    print("\n=== Test: Chained operations ===")
    print("Optimized TAC:")
    for i, instr in enumerate(optimized):
        print(f"  {i+1}. {instr}")
    
    print("\nGenerated Assembly:")
    for i, instr in enumerate(assembly):
        print(f"  {i+1}. {instr}")
    
    # Should have exactly 4 STR instructions (a, b, c, result)
    str_instrs = [a for a in assembly if a.op == "STR"]
    assert len(str_instrs) == 4, f"Expected 4 STR, got {len(str_instrs)}"
    
    # Should have 2 ADD instructions
    add_instrs = [a for a in assembly if a.op == "ADD"]
    assert len(add_instrs) == 2, f"Expected 2 ADD, got {len(add_instrs)}"
    
    print("PASS: Chained operations have minimal stores")


if __name__ == "__main__":
    test_simple_int_assignment()
    test_simple_float_assignment()
    test_variable_to_variable_assignment()
    test_int_addition_with_literal()
    test_float_addition()
    test_commutative_swap_addition()
    test_commutative_swap_multiplication()
    test_non_commutative_subtraction()
    test_non_commutative_division()
    test_modulo_operation()
    test_two_variable_addition()
    test_mixed_type_operation()
    test_float_annotation_from_optimizer()
    test_complex_expression()
    test_multiple_statements()
    test_assembly_instruction_str()
    test_control_flow_skipped()
    test_io_skipped()
    test_empty_input()
    test_temps_stay_in_registers()
    test_nested_expression()
    test_chained_operations()
    
    print("\n" + "="*50)
    print("All code generator tests passed!")
    print("="*50)
