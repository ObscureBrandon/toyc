"""Intermediate Code Generator (ICG) for ToyC Compiler.

Generates three-address code (TAC) from the analyzed AST.
Each instruction performs only one operation.
Literal numbers are prefixed with #.
"""

from typing import List, Optional
from dataclasses import dataclass
from .ast import (
    ASTNode,
    ProgramNode,
    BinaryOpNode,
    NumberNode,
    FloatNode,
    IdentifierNode,
    AssignmentNode,
    Int2FloatNode,
    BlockNode,
    IfNode,
    RepeatUntilNode,
    ReadNode,
    WriteNode,
)


@dataclass
class ThreeAddressCode:
    """Represents a single three-address code instruction."""

    op: str  # Operation: 'assign', 'add', 'sub', 'mul', 'div', 'mod', 'int2float', etc.
    arg1: Optional[str] = None  # First operand (can be #literal, temp, or variable)
    arg2: Optional[str] = None  # Second operand (can be #literal, temp, or variable)
    result: Optional[str] = None  # Destination (temp or variable)
    label: Optional[str] = None  # For label instructions

    def __str__(self) -> str:
        """String representation of the instruction."""
        if self.op == "label":
            return f"label {self.label}:"
        elif self.op == "goto":
            return f"goto {self.arg1}"
        elif self.op == "if_false":
            return f"if_false {self.arg1} goto {self.arg2}"
        elif self.op == "if_true":
            return f"if_true {self.arg1} goto {self.arg2}"
        elif self.op == "assign":
            return f"{self.result} = {self.arg1}"
        elif self.op == "read":
            return f"read {self.arg1}"
        elif self.op == "write":
            return f"write {self.arg1}"
        elif self.op == "int2float":
            return f"{self.result} = int2float({self.arg1})"
        elif self.arg2 is None:
            return f"{self.result} = {self.op} {self.arg1}"
        else:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


class ICGGenerator:
    """Generates intermediate code (three-address code) from analyzed AST."""

    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.code: List[ThreeAddressCode] = []
        self.identifier_map: dict[str, str] = {}  # Maps variable names to id1, id2, etc.
        self.identifier_counter = 0

    def new_temp(self) -> str:
        """Generate a new temporary variable name (temp1, temp2, ...)."""
        self.temp_counter += 1
        return f"temp{self.temp_counter}"

    def new_label(self) -> str:
        """Generate a new label name (L1, L2, ...)."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def get_identifier(self, name: str) -> str:
        """Get or create normalized identifier (id1, id2, ...) for a variable name."""
        if name not in self.identifier_map:
            self.identifier_counter += 1
            self.identifier_map[name] = f"id{self.identifier_counter}"
        return self.identifier_map[name]

    def emit(
        self,
        op: str,
        arg1: Optional[str] = None,
        arg2: Optional[str] = None,
        result: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """Add a three-address code instruction."""
        instr = ThreeAddressCode(op=op, arg1=arg1, arg2=arg2, result=result, label=label)
        self.code.append(instr)

    def collect_identifiers(self, node: ASTNode):
        """Collect all identifiers from the AST in order of appearance."""
        if isinstance(node, AssignmentNode):
            # First collect the identifier being assigned to
            self.get_identifier(node.identifier)
            # Then collect identifiers in the value expression
            self.collect_identifiers_from_expression(node.value)
        elif isinstance(node, IfNode):
            self.collect_identifiers_from_expression(node.condition)
            self.collect_identifiers(node.then_branch)
            if node.else_branch:
                self.collect_identifiers(node.else_branch)
        elif isinstance(node, RepeatUntilNode):
            self.collect_identifiers(node.body)
            self.collect_identifiers_from_expression(node.condition)
        elif isinstance(node, ReadNode):
            self.get_identifier(node.identifier)
        elif isinstance(node, WriteNode):
            self.collect_identifiers_from_expression(node.expression)
        elif isinstance(node, BlockNode):
            for statement in node.statements:
                self.collect_identifiers(statement)

    def collect_identifiers_from_expression(self, node: ASTNode):
        """Collect identifiers from an expression node."""
        if isinstance(node, IdentifierNode):
            self.get_identifier(node.name)
        elif isinstance(node, BinaryOpNode):
            self.collect_identifiers_from_expression(node.left)
            self.collect_identifiers_from_expression(node.right)
        elif isinstance(node, Int2FloatNode):
            self.collect_identifiers_from_expression(node.child)
        # NumberNode and FloatNode don't have identifiers, so we skip them

    def generate(self, ast: ProgramNode) -> List[ThreeAddressCode]:
        """Generate ICG for the entire program."""
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.identifier_map = {}
        self.identifier_counter = 0

        # First pass: collect all identifiers in order of appearance
        for statement in ast.statements:
            self.collect_identifiers(statement)

        # Second pass: generate the actual code
        for statement in ast.statements:
            self.generate_statement(statement)

        return self.code

    def generate_statement(self, node: ASTNode):
        """Generate ICG for a statement."""
        if isinstance(node, AssignmentNode):
            self.generate_assignment(node)
        elif isinstance(node, IfNode):
            self.generate_if(node)
        elif isinstance(node, RepeatUntilNode):
            self.generate_repeat_until(node)
        elif isinstance(node, ReadNode):
            self.generate_read(node)
        elif isinstance(node, WriteNode):
            self.generate_write(node)
        elif isinstance(node, BlockNode):
            self.generate_block(node)

    def generate_expression(self, node: ASTNode) -> str:
        """Generate ICG for an expression and return the result location (temp var or literal)."""
        if isinstance(node, NumberNode):
            # Literal integers are prefixed with #
            return f"#{node.value}"
        elif isinstance(node, FloatNode):
            # Literal floats are prefixed with #
            return f"#{node.value}"
        elif isinstance(node, IdentifierNode):
            # Variables use normalized identifiers (id1, id2, etc.)
            return self.get_identifier(node.name)
        elif isinstance(node, BinaryOpNode):
            return self.generate_binary_op(node)
        elif isinstance(node, Int2FloatNode):
            return self.generate_int2float(node)
        else:
            # Fallback for unknown expression types
            temp = self.new_temp()
            self.emit("unknown", None, None, temp)
            return temp

    def generate_binary_op(self, node: BinaryOpNode) -> str:
        """Generate ICG for a binary operation."""
        left_result = self.generate_expression(node.left)
        right_result = self.generate_expression(node.right)
        result_temp = self.new_temp()

        # Map operator tokens to ICG operations
        op_map = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
            "==": "==",
            "!=": "!=",
            "&&": "&&",
            "||": "||",
        }

        op = op_map.get(node.operator, node.operator)
        self.emit(op, left_result, right_result, result_temp)
        return result_temp

    def generate_int2float(self, node: Int2FloatNode) -> str:
        """Generate ICG for int to float conversion."""
        child_result = self.generate_expression(node.child)
        result_temp = self.new_temp()
        self.emit("int2float", child_result, None, result_temp)
        return result_temp

    def generate_assignment(self, node: AssignmentNode):
        """Generate ICG for an assignment statement."""
        value_result = self.generate_expression(node.value)
        # Use normalized identifier for the variable
        normalized_id = self.get_identifier(node.identifier)
        self.emit("assign", value_result, None, normalized_id)

    def generate_block(self, node: BlockNode):
        """Generate ICG for a block of statements."""
        for statement in node.statements:
            self.generate_statement(statement)

    def generate_if(self, node: IfNode):
        """Generate ICG for an if statement.
        
        Pattern without else:
            temp1 = condition
            if_false temp1 goto L1
            <then branch>
            label L1:
        
        Pattern with else:
            temp1 = condition
            if_false temp1 goto L1
            <then branch>
            goto L2
            label L1:
            <else branch>
            label L2:
        """
        # Generate condition
        cond_result = self.generate_expression(node.condition)

        # Create labels
        else_label = self.new_label()
        end_label = self.new_label() if node.else_branch else None

        # if_false condition goto else_label
        self.emit("if_false", cond_result, else_label, None)

        # Generate then branch
        self.generate_statement(node.then_branch)

        # If there's an else branch, jump over it
        if node.else_branch:
            self.emit("goto", end_label, None, None)

        # else_label:
        self.emit("label", None, None, None, else_label)

        # Generate else branch if it exists
        if node.else_branch:
            self.generate_statement(node.else_branch)
            # end_label:
            self.emit("label", None, None, None, end_label)

    def generate_repeat_until(self, node: RepeatUntilNode):
        """Generate ICG for a repeat-until loop.
        
        Pattern:
            label L1:
            <body>
            temp1 = condition
            if_false temp1 goto L1
        """
        # Create label for loop start
        loop_start = self.new_label()

        # loop_start:
        self.emit("label", None, None, None, loop_start)

        # Generate body
        self.generate_statement(node.body)

        # Generate condition
        cond_result = self.generate_expression(node.condition)

        # if_false condition goto loop_start (repeat until condition is true)
        self.emit("if_false", cond_result, loop_start, None)

    def generate_read(self, node: ReadNode):
        """Generate ICG for a read statement."""
        # Use normalized identifier for the variable
        normalized_id = self.get_identifier(node.identifier)
        self.emit("read", normalized_id, None, None)

    def generate_write(self, node: WriteNode):
        """Generate ICG for a write statement."""
        expr_result = self.generate_expression(node.expression)
        self.emit("write", expr_result, None, None)
