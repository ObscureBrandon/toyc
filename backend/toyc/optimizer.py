"""Code Optimizer for ToyC Compiler.

Optimizes three-address code (TAC) by:
1. Inlining int2float operations (with constant folding for literals)
2. Eliminating unnecessary temporary variables
3. Copy propagation
4. Algebraic simplifications
5. Dead code elimination
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from .icg import ThreeAddressCode


@dataclass
class OptimizationStats:
    """Statistics about optimizations performed."""
    
    original_instruction_count: int = 0
    optimized_instruction_count: int = 0
    int2float_inlined: int = 0
    temps_eliminated: int = 0
    copies_propagated: int = 0
    algebraic_simplifications: int = 0
    dead_code_eliminated: int = 0
    
    @property
    def instructions_saved(self) -> int:
        return self.original_instruction_count - self.optimized_instruction_count
    
    @property
    def reduction_percentage(self) -> float:
        if self.original_instruction_count == 0:
            return 0.0
        return (self.instructions_saved / self.original_instruction_count) * 100


class Optimizer:
    """Optimizes intermediate code (three-address code)."""
    
    def __init__(self):
        self.stats = OptimizationStats()
        
    def optimize(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Apply all optimization passes to the instruction list."""
        self.stats = OptimizationStats()
        self.stats.original_instruction_count = len(instructions)
        
        optimized = instructions[:]
        
        # Apply optimization passes iteratively until no more changes
        max_iterations = 10
        for iteration in range(max_iterations):
            prev_length = len(optimized)
            
            # Pass 1: Inline int2float operations
            optimized = self._inline_int2float(optimized)
            
            # Pass 2: Eliminate single-use temporaries
            optimized = self._eliminate_single_use_temps(optimized)
            
            # Pass 3: Algebraic simplifications
            optimized = self._algebraic_simplification(optimized)
            
            # Pass 4: Copy propagation
            optimized = self._copy_propagation(optimized)
            
            # Pass 5: Dead code elimination
            optimized = self._dead_code_elimination(optimized)
            
            # If no changes, we're done
            if len(optimized) == prev_length:
                break
        
        # Final pass: Renumber temps sequentially for clarity
        optimized = self._renumber_temps(optimized)
        
        self.stats.optimized_instruction_count = len(optimized)
        return optimized
    
    def _inline_int2float(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Inline int2float operations.
        
        Rules:
        - int2float(#5) -> #5.0 (constant folding)
        - int2float(id1) -> id1(f) (variable annotation)
        - Eliminate the int2float instruction entirely
        """
        result = []
        replacements: Dict[str, str] = {}  # Maps temp variables to their replacement
        
        for instr in instructions:
            if instr.op == "int2float":
                # Record the replacement
                operand = instr.arg1
                result_var = instr.result
                
                if operand and result_var:
                    if operand.startswith("#"):
                        # Constant: convert #5 to #5.0
                        try:
                            int_value = int(operand[1:])
                            replacements[result_var] = f"#{int_value}.0"
                        except ValueError:
                            # Already a float or invalid, keep as-is
                            replacements[result_var] = operand
                    else:
                        # Variable or temp: add (f) annotation
                        replacements[result_var] = f"{operand}(f)"
                    
                    # Don't include this instruction in the result
                    self.stats.int2float_inlined += 1
                    continue
            
            # Apply replacements to current instruction
            new_instr = self._apply_replacements(instr, replacements)
            result.append(new_instr)
        
        return result
    
    def _eliminate_single_use_temps(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Eliminate temporary variables that are only used once.
        
        Strategy: If temp is used exactly once and next instruction uses it,
        inline the temp's value into that instruction.
        
        Example:
        temp1 = #5 + #3
        id1 = temp1
        
        Becomes:
        id1 = #5 + #3
        """
        # Count uses of each variable
        use_count = self._count_variable_uses(instructions)
        
        result = []
        i = 0
        
        while i < len(instructions):
            instr = instructions[i]
            
            # Always keep labels, control flow, and I/O
            if instr.op in ["label", "goto", "if_false", "if_true", "read", "write"]:
                result.append(instr)
                i += 1
                continue
            
            # Check if this instruction defines a temp that's used exactly once
            if (instr.result and instr.result.startswith("temp") and 
                use_count.get(instr.result, 0) == 1 and
                i + 1 < len(instructions)):
                
                next_instr = instructions[i + 1]
                
                # If next instruction is simple assignment from this temp: id = temp
                if (next_instr.op == "assign" and 
                    next_instr.arg1 == instr.result and 
                    not next_instr.arg2):
                    
                    # Inline: change temp's result to final destination
                    # Result is now an identifier, not a temp
                    new_instr = ThreeAddressCode(
                        op=instr.op,
                        arg1=instr.arg1,
                        arg2=instr.arg2,
                        result=next_instr.result,
                        label=None,
                        is_temp=next_instr.result.startswith("temp") if next_instr.result else False
                    )
                    result.append(new_instr)
                    self.stats.temps_eliminated += 1
                    i += 2  # Skip both instructions
                    continue
                
                # If next instruction uses this temp in an operation
                elif (next_instr.arg1 == instr.result or next_instr.arg2 == instr.result):
                    # For now, just keep both - we'll handle more complex cases later
                    result.append(instr)
                    i += 1
                    continue
            
            result.append(instr)
            i += 1
        
        return result
    
    def _copy_propagation(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Propagate copies to eliminate intermediate assignments.
        
        Only removes temporary variable copies, keeps user variable assignments.
        
        Example:
        temp1 = id1
        temp2 = temp1 + #5
        
        Becomes:
        temp2 = id1 + #5
        """
        result = []
        copies: Dict[str, str] = {}  # Maps variables to what they're copies of
        
        for instr in instructions:
            # Reset on labels (control flow boundary)
            if instr.op == "label":
                copies.clear()
                result.append(instr)
                continue
            
            # Track simple copies: temp = something (only for temps)
            if (instr.op == "assign" and instr.arg1 and not instr.arg2 and
                instr.result and instr.result.startswith("temp") and
                not instr.arg1.startswith("#")):  # Not a literal
                
                copies[instr.result] = instr.arg1
                # Don't add this instruction yet, it might be eliminable
                continue
            
            # Apply copy propagation to current instruction
            new_instr = self._apply_replacements(instr, copies)
            result.append(new_instr)
        
        return result
    
    def _algebraic_simplification(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Apply algebraic simplifications.
        
        Rules:
        - x + #0 -> x
        - x * #1 -> x
        - x * #0 -> #0
        - x - #0 -> x
        - #0 + x -> x
        - #1 * x -> x
        """
        result = []
        
        for instr in instructions:
            simplified = self._simplify_instruction(instr)
            if simplified != instr:
                self.stats.algebraic_simplifications += 1
            result.append(simplified)
        
        return result
    
    def _dead_code_elimination(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Remove instructions that compute values that are never used.
        
        Note: Keep all assignments to user variables (id1, id2, etc.) as they are program outputs.
        Only remove unused temporary variables.
        """
        use_count = self._count_variable_uses(instructions)
        result = []
        
        for instr in instructions:
            # Always keep labels, control flow, and I/O
            if instr.op in ["label", "goto", "if_false", "if_true", "read", "write"]:
                result.append(instr)
                continue
            
            # If instruction produces a temporary that's never used, remove it
            if instr.result and instr.result.startswith("temp"):
                if use_count.get(instr.result, 0) == 0:
                    self.stats.dead_code_eliminated += 1
                    continue
            
            # Keep all other instructions (including assignments to user variables)
            result.append(instr)
        
        return result
    
    def _apply_replacements(self, instr: ThreeAddressCode, replacements: Dict[str, str]) -> ThreeAddressCode:
        """Apply variable replacements to an instruction."""
        new_arg1 = replacements.get(instr.arg1, instr.arg1) if instr.arg1 else None
        new_arg2 = replacements.get(instr.arg2, instr.arg2) if instr.arg2 else None
        
        return ThreeAddressCode(
            op=instr.op,
            arg1=new_arg1,
            arg2=new_arg2,
            result=instr.result,
            label=instr.label,
            is_temp=instr.is_temp
        )
    
    def _simplify_instruction(self, instr: ThreeAddressCode) -> ThreeAddressCode:
        """Apply algebraic simplifications to a single instruction."""
        # x + 0 or 0 + x -> x
        if instr.op == "+" and (instr.arg2 == "#0" or instr.arg1 == "#0"):
            other = instr.arg1 if instr.arg2 == "#0" else instr.arg2
            return ThreeAddressCode(op="assign", arg1=other, result=instr.result, is_temp=instr.is_temp)
        
        # x - 0 -> x
        if instr.op == "-" and instr.arg2 == "#0":
            return ThreeAddressCode(op="assign", arg1=instr.arg1, result=instr.result, is_temp=instr.is_temp)
        
        # x * 1 or 1 * x -> x
        if instr.op == "*" and (instr.arg2 == "#1" or instr.arg1 == "#1"):
            other = instr.arg1 if instr.arg2 == "#1" else instr.arg2
            return ThreeAddressCode(op="assign", arg1=other, result=instr.result, is_temp=instr.is_temp)
        
        # x * 0 or 0 * x -> 0
        if instr.op == "*" and (instr.arg2 == "#0" or instr.arg1 == "#0"):
            return ThreeAddressCode(op="assign", arg1="#0", result=instr.result, is_temp=instr.is_temp)
        
        return instr
    
    def _count_variable_uses(self, instructions: List[ThreeAddressCode]) -> Dict[str, int]:
        """Count how many times each variable is used (not defined)."""
        use_count: Dict[str, int] = {}
        
        for instr in instructions:
            # Count uses in arg1 and arg2 (not in result, that's a definition)
            if instr.arg1 and not instr.arg1.startswith("#"):
                use_count[instr.arg1] = use_count.get(instr.arg1, 0) + 1
            if instr.arg2 and not instr.arg2.startswith("#"):
                use_count[instr.arg2] = use_count.get(instr.arg2, 0) + 1
        
        return use_count
    
    def _find_next_use(self, instructions: List[ThreeAddressCode], var: str, start_idx: int) -> Optional[int]:
        """Find the index of the next instruction that uses the given variable."""
        for i in range(start_idx + 1, len(instructions)):
            instr = instructions[i]
            if instr.arg1 == var or instr.arg2 == var:
                return i
        return None
    
    def _renumber_temps(self, instructions: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        """Renumber temporary variables sequentially (temp1, temp2, temp3, ...).
        
        This is done for clarity and aesthetic reasons after optimization.
        """
        # Collect all temps in order of first appearance
        temp_map: Dict[str, str] = {}
        next_temp_num = 1
        
        # First pass: build mapping
        for instr in instructions:
            # Check result
            if instr.result and instr.result.startswith("temp") and instr.result not in temp_map:
                temp_map[instr.result] = f"temp{next_temp_num}"
                next_temp_num += 1
            
            # Check arg1
            if instr.arg1 and instr.arg1.startswith("temp") and instr.arg1 not in temp_map:
                temp_map[instr.arg1] = f"temp{next_temp_num}"
                next_temp_num += 1
            
            # Check arg2
            if instr.arg2 and instr.arg2.startswith("temp") and instr.arg2 not in temp_map:
                temp_map[instr.arg2] = f"temp{next_temp_num}"
                next_temp_num += 1
        
        # Second pass: apply renumbering
        result = []
        for instr in instructions:
            new_result = temp_map.get(instr.result, instr.result) if instr.result else None
            new_arg1 = temp_map.get(instr.arg1, instr.arg1) if instr.arg1 else None
            new_arg2 = temp_map.get(instr.arg2, instr.arg2) if instr.arg2 else None
            
            new_instr = ThreeAddressCode(
                op=instr.op,
                arg1=new_arg1,
                arg2=new_arg2,
                result=new_result,
                label=instr.label,
                is_temp=instr.is_temp
            )
            result.append(new_instr)
        
        return result
