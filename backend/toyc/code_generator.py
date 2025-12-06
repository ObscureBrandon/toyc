"""Code Generator for ToyC Compiler.

Generates assembly-like code from optimized three-address code (TAC).
Target architecture has only 2 registers: R1 and R2.

Instructions:
- LOAD/LOADF: Load integer/float into register
- STR/STRF: Store integer/float from register to memory
- ADD/ADDF, SUB/SUBF, MUL/MULF, DIV/DIVF, MOD/MODF: Arithmetic operations

For 3-operand instructions: destination, source1, source2

Key design: Temporaries stay in registers and are never stored to memory.
Only final assignments to identifiers (id1, id2, etc.) generate STR instructions.
"""

from typing import List, Optional
from dataclasses import dataclass
from .icg import ThreeAddressCode


@dataclass
class AssemblyInstruction:
    """Represents a single assembly-like instruction."""

    op: str  # LOAD, LOADF, STR, STRF, ADD, ADDF, SUB, SUBF, MUL, MULF, DIV, DIVF, MOD, MODF
    operands: List[str]  # [R1, x] or [R1, R1, #5] or [x, R1]

    def __str__(self) -> str:
        """String representation of the instruction."""
        return f"{self.op} {', '.join(self.operands)}"


class CodeGenerator:
    """Generates assembly-like code from optimized three-address code.
    
    Register allocation strategy:
    - R1: Primary register for computation results
    - R2: Secondary register for second operand when needed
    - Temps stay in registers (tracked via register_contents)
    - Only final identifier assignments generate STR
    """

    # Mapping from TAC operators to assembly mnemonics
    OP_MAP_INT = {
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "/": "DIV",
        "%": "MOD",
    }

    OP_MAP_FLOAT = {
        "+": "ADDF",
        "-": "SUBF",
        "*": "MULF",
        "/": "DIVF",
        "%": "MODF",
    }

    # Commutative operators (can swap operands)
    COMMUTATIVE_OPS = {"+", "*"}

    def __init__(self, type_map: dict[str, str]):
        """Initialize the code generator.

        Args:
            type_map: Maps identifiers and temps to their types ("int" or "float")
        """
        self.type_map = type_map
        self.code: List[AssemblyInstruction] = []
        # Track which temps are currently in which registers
        # Maps temp name -> register name (e.g., "temp1" -> "R1")
        self.register_contents: dict[str, str] = {}

    def generate(self, instructions: List[ThreeAddressCode]) -> List[AssemblyInstruction]:
        """Generate assembly code from TAC instructions.

        Args:
            instructions: List of three-address code instructions

        Returns:
            List of assembly instructions
        """
        self.code = []
        self.register_contents = {}

        for instr in instructions:
            self._generate_instruction(instr)

        return self.code

    def _emit(self, op: str, operands: List[str]) -> None:
        """Emit an assembly instruction."""
        self.code.append(AssemblyInstruction(op=op, operands=operands))

    def _is_literal(self, operand: Optional[str]) -> bool:
        """Check if operand is a literal (starts with #)."""
        return operand is not None and operand.startswith("#")

    def _is_temp(self, operand: Optional[str]) -> bool:
        """Check if operand is a temporary variable."""
        return operand is not None and operand.startswith("temp")

    def _is_in_register(self, operand: Optional[str]) -> bool:
        """Check if operand is currently in a register."""
        return operand is not None and operand in self.register_contents

    def _get_register(self, operand: str) -> str:
        """Get the register containing this operand."""
        return self.register_contents[operand]

    def _is_float_type(self, operand: Optional[str]) -> bool:
        """Determine if operand is float type."""
        if operand is None:
            return False
        if self._is_literal(operand):
            # For literals, check if it contains a decimal point
            return "." in operand
        # Handle optimizer's float annotation: id1(f) means float
        if operand.endswith("(f)"):
            return True
        # For identifiers and temps, look up in type_map
        return self.type_map.get(operand, "int") == "float"

    def _get_load_op(self, is_float: bool) -> str:
        """Get the appropriate load instruction."""
        return "LOADF" if is_float else "LOAD"

    def _get_store_op(self, is_float: bool) -> str:
        """Get the appropriate store instruction."""
        return "STRF" if is_float else "STR"

    def _get_arith_op(self, tac_op: str, is_float: bool) -> str:
        """Get the appropriate arithmetic instruction."""
        op_map = self.OP_MAP_FLOAT if is_float else self.OP_MAP_INT
        return op_map.get(tac_op, tac_op)

    def _get_free_register(self, exclude: set[str] | None = None) -> str:
        """Get a register that's not currently holding a needed temp.
        
        Args:
            exclude: Set of registers to exclude from consideration
            
        Returns:
            "R1" or "R2", preferring R1 if both are free
        """
        if exclude is None:
            exclude = set()
        
        # Check which registers are currently holding temps
        temps_in_r1 = any(reg == "R1" for reg in self.register_contents.values())
        temps_in_r2 = any(reg == "R2" for reg in self.register_contents.values())
        
        # Prefer R1 if it's free and not excluded
        if not temps_in_r1 and "R1" not in exclude:
            return "R1"
        if not temps_in_r2 and "R2" not in exclude:
            return "R2"
        
        # Both have temps - use R1 unless excluded (will overwrite)
        if "R1" not in exclude:
            return "R1"
        return "R2"

    def _generate_instruction(self, instr: ThreeAddressCode) -> None:
        """Generate assembly for a single TAC instruction."""
        if instr.op == "assign":
            self._generate_assign(instr)
        elif instr.op in self.OP_MAP_INT:
            self._generate_binary_op(instr)
        # Skip control flow, I/O, comparisons for now
        # These would be: label, goto, if_false, if_true, read, write
        # And comparison ops: <, >, <=, >=, ==, !=, &&, ||

    def _generate_assign(self, instr: ThreeAddressCode) -> None:
        """Generate assembly for assignment: result = arg1.

        Patterns:
        - id1 = #5       -> STR id1, #5 (direct store for literal)
        - id1 = id2      -> LOAD R1, id2; STR id1, R1
        - id1 = temp1    -> STR id1, R1 (if temp1 is in R1, no LOAD needed)
        - temp1 = id1    -> LOAD R1, id1 (temp stays in R1, no STR)
        - temp1 = temp2  -> (no-op if same register, or track new location)
        """
        arg1 = instr.arg1
        result = instr.result

        if arg1 is None or result is None:
            return  # Invalid instruction, skip

        # Determine if we're dealing with floats
        is_float = self._is_float_type(arg1) or self._is_float_type(result)
        load_op = self._get_load_op(is_float)
        store_op = self._get_store_op(is_float)

        result_is_temp = instr.is_temp or self._is_temp(result)

        if result_is_temp:
            # Result is a temp - load value into register, don't store
            if self._is_in_register(arg1):
                # Source is already in a register, just track it
                src_reg = self._get_register(arg1)
                self.register_contents[result] = src_reg
            elif self._is_literal(arg1):
                # Load literal into R1
                self._emit(load_op, ["R1", arg1])
                self.register_contents[result] = "R1"
            else:
                # Load identifier into R1
                self._emit(load_op, ["R1", arg1])
                self.register_contents[result] = "R1"
        else:
            # Result is an identifier - must store to memory
            if self._is_in_register(arg1):
                # Source is in a register, store directly
                src_reg = self._get_register(arg1)
                self._emit(store_op, [result, src_reg])
            elif self._is_literal(arg1):
                # Direct store for literals
                self._emit(store_op, [result, arg1])
            else:
                # Load into R1, then store
                self._emit(load_op, ["R1", arg1])
                self._emit(store_op, [result, "R1"])

    def _generate_binary_op(self, instr: ThreeAddressCode) -> None:
        """Generate assembly for binary operation: result = arg1 op arg2.

        Key insight: If either operand is a temp in a register, use that register.
        If result is a temp, don't emit STR - just track which register has the result.

        Patterns:
        - id1 = id2 + #5     -> LOAD R1, id2; ADD R1, R1, #5; STR id1, R1
        - id1 = temp1 + #5   -> ADD R1, R1, #5; STR id1, R1 (temp1 already in R1)
        - temp2 = temp1 + #5 -> ADD R1, R1, #5 (no STR, temp2 now in R1)
        - temp2 = id1 * temp1 -> LOAD R2, id1; MUL R1, R2, R1 (temp1 in R1, result in R1)
        """
        arg1 = instr.arg1
        arg2 = instr.arg2
        result = instr.result
        op = instr.op

        if arg1 is None or arg2 is None or result is None:
            return  # Invalid instruction, skip

        # Determine if this is a float operation
        is_float = (
            self._is_float_type(arg1)
            or self._is_float_type(arg2)
            or self._is_float_type(result)
        )

        load_op = self._get_load_op(is_float)
        store_op = self._get_store_op(is_float)
        arith_op = self._get_arith_op(op, is_float)

        result_is_temp = instr.is_temp or self._is_temp(result)

        # Check if operands are in registers
        arg1_in_reg = self._is_in_register(arg1)
        arg2_in_reg = self._is_in_register(arg2)
        arg1_is_literal = self._is_literal(arg1)
        arg2_is_literal = self._is_literal(arg2)

        # Determine which register holds the result after the operation
        result_reg = "R1"

        if arg1_in_reg and arg2_in_reg:
            # Both operands are temps in registers
            reg1 = self._get_register(arg1)
            reg2 = self._get_register(arg2)
            # Perform operation: result in R1
            self._emit(arith_op, ["R1", reg1, reg2])
            result_reg = "R1"

        elif arg1_in_reg and not arg2_in_reg:
            # First operand is in register, second is literal or identifier
            reg1 = self._get_register(arg1)
            if arg2_is_literal:
                # temp1 + #5 -> ADD R1, R1, #5
                self._emit(arith_op, [reg1, reg1, arg2])
                result_reg = reg1
            else:
                # temp1 + id2 -> LOAD R2, id2; ADD R1, R1, R2
                self._emit(load_op, ["R2", arg2])
                self._emit(arith_op, [reg1, reg1, "R2"])
                result_reg = reg1

        elif not arg1_in_reg and arg2_in_reg:
            # Second operand is in register, first is literal or identifier
            reg2 = self._get_register(arg2)
            if arg1_is_literal:
                if op in self.COMMUTATIVE_OPS:
                    # Commutative: #5 + temp1 -> ADD R1, R1, #5
                    self._emit(arith_op, [reg2, reg2, arg1])
                    result_reg = reg2
                else:
                    # Non-commutative: #5 - temp1 -> LOAD R1, #5; SUB R1, R1, reg2
                    # But we need to be careful: temp1 might be in R1
                    if reg2 == "R1":
                        # Load literal into R2, then operate
                        self._emit(load_op, ["R2", arg1])
                        self._emit(arith_op, ["R1", "R2", "R1"])
                        result_reg = "R1"
                    else:
                        self._emit(load_op, ["R1", arg1])
                        self._emit(arith_op, ["R1", "R1", reg2])
                        result_reg = "R1"
            else:
                # id1 * temp1 -> LOAD R2, id1; MUL R1, R2, R1 (or MUL R1, R2, reg2)
                # Load identifier into the OTHER register
                if reg2 == "R1":
                    self._emit(load_op, ["R2", arg1])
                    self._emit(arith_op, ["R1", "R2", "R1"])
                    result_reg = "R1"
                else:
                    self._emit(load_op, ["R1", arg1])
                    self._emit(arith_op, ["R1", "R1", reg2])
                    result_reg = "R1"

        else:
            # Neither operand is in a register
            # Choose the primary register carefully to avoid overwriting temps
            primary_reg = self._get_free_register()
            secondary_reg = "R2" if primary_reg == "R1" else "R1"
            
            # Check if we have a temp in the secondary register that we need to preserve
            temp_in_secondary = any(reg == secondary_reg for reg in self.register_contents.values())
            
            if arg1_is_literal and arg2_is_literal:
                # Both literals - rare case (should be constant folded)
                self._emit(load_op, [primary_reg, arg1])
                self._emit(arith_op, [primary_reg, primary_reg, arg2])
                result_reg = primary_reg
            elif arg1_is_literal and not arg2_is_literal:
                # First is literal, second is identifier
                if op in self.COMMUTATIVE_OPS:
                    # Commutative: swap to avoid loading literal
                    # LOAD primary_reg, arg2; OP primary_reg, primary_reg, arg1
                    self._emit(load_op, [primary_reg, arg2])
                    self._emit(arith_op, [primary_reg, primary_reg, arg1])
                else:
                    # Non-commutative: #5 - id2
                    # If we can't use secondary_reg (has a temp), use arg2 directly as operand
                    if temp_in_secondary:
                        # LOAD primary_reg, arg1; OP primary_reg, primary_reg, arg2 (memory operand)
                        self._emit(load_op, [primary_reg, arg1])
                        self._emit(arith_op, [primary_reg, primary_reg, arg2])
                    else:
                        self._emit(load_op, [primary_reg, arg1])
                        self._emit(load_op, [secondary_reg, arg2])
                        self._emit(arith_op, [primary_reg, primary_reg, secondary_reg])
                result_reg = primary_reg
            elif not arg1_is_literal and arg2_is_literal:
                # First is identifier, second is literal
                # LOAD primary_reg, arg1; OP primary_reg, primary_reg, arg2
                self._emit(load_op, [primary_reg, arg1])
                self._emit(arith_op, [primary_reg, primary_reg, arg2])
                result_reg = primary_reg
            else:
                # Both are identifiers: id1 op id2
                # If we can't use secondary_reg (has a temp), use arg2 directly as operand
                if temp_in_secondary:
                    # LOAD primary_reg, arg1; OP primary_reg, primary_reg, arg2 (memory operand)
                    self._emit(load_op, [primary_reg, arg1])
                    self._emit(arith_op, [primary_reg, primary_reg, arg2])
                else:
                    self._emit(load_op, [primary_reg, arg1])
                    self._emit(load_op, [secondary_reg, arg2])
                    self._emit(arith_op, [primary_reg, primary_reg, secondary_reg])
                result_reg = primary_reg

        # Handle result
        if result_is_temp:
            # Track that this temp is now in result_reg
            self.register_contents[result] = result_reg
        else:
            # Store to memory (this is a final identifier)
            self._emit(store_op, [result, result_reg])
