from typing import Dict, Literal, Optional
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


NodeType = Literal["int", "float", "unknown"]


class SemanticAnalyzer:
    """Performs semantic analysis with type checking and coercion"""

    def __init__(self, predefined_types: Optional[Dict[str, NodeType]] = None):
        self.symbol_table: Dict[str, NodeType] = {}
        # Pre-populate symbol table with user-provided types for undefined variables
        if predefined_types:
            for var, var_type in predefined_types.items():
                self.symbol_table[var] = var_type

    def analyze(self, ast: ProgramNode) -> ProgramNode:
        """Analyze the AST and insert type coercion nodes where needed"""
        new_statements = []
        
        for statement in ast.statements:
            analyzed_stmt = self.analyze_statement(statement)
            new_statements.append(analyzed_stmt)
        
        return ProgramNode(new_statements)

    def analyze_statement(self, node: ASTNode) -> ASTNode:
        """Analyze a statement node"""
        if isinstance(node, AssignmentNode):
            return self.analyze_assignment(node)
        elif isinstance(node, IfNode):
            return self.analyze_if(node)
        elif isinstance(node, RepeatUntilNode):
            return self.analyze_repeat(node)
        elif isinstance(node, ReadNode):
            return self.analyze_read(node)
        elif isinstance(node, WriteNode):
            return self.analyze_write(node)
        elif isinstance(node, BlockNode):
            return self.analyze_block(node)
        else:
            return self.analyze_expression(node)

    def analyze_assignment(self, node: AssignmentNode) -> AssignmentNode:
        """Analyze assignment and update symbol table"""
        analyzed_value = self.analyze_expression(node.value)
        value_type = self.get_expression_type(analyzed_value)
        
        self.symbol_table[node.identifier] = value_type
        
        return AssignmentNode(node.identifier, analyzed_value)

    def analyze_expression(self, node: ASTNode) -> ASTNode:
        """Analyze an expression and insert coercions if needed"""
        if isinstance(node, BinaryOpNode):
            return self.analyze_binary_op(node)
        elif isinstance(node, (NumberNode, FloatNode, IdentifierNode)):
            return node
        elif isinstance(node, AssignmentNode):
            return self.analyze_assignment(node)
        else:
            return node

    def analyze_binary_op(self, node: BinaryOpNode) -> BinaryOpNode:
        """Analyze binary operation and coerce operands if needed"""
        left = self.analyze_expression(node.left)
        right = self.analyze_expression(node.right)
        
        left_type = self.get_expression_type(left)
        right_type = self.get_expression_type(right)
        
        if left_type == "float" and right_type == "int":
            right = Int2FloatNode(right)
        elif left_type == "int" and right_type == "float":
            left = Int2FloatNode(left)
        
        return BinaryOpNode(node.operator, left, right)

    def get_expression_type(self, node: ASTNode) -> NodeType:
        """Determine the type of an expression"""
        if isinstance(node, NumberNode):
            return "int"
        elif isinstance(node, FloatNode):
            return "float"
        elif isinstance(node, Int2FloatNode):
            return "float"
        elif isinstance(node, IdentifierNode):
            return self.symbol_table.get(node.name, "unknown")
        elif isinstance(node, BinaryOpNode):
            left_type = self.get_expression_type(node.left)
            right_type = self.get_expression_type(node.right)
            
            if left_type == "float" or right_type == "float":
                return "float"
            elif left_type == "int" and right_type == "int":
                return "int"
            else:
                return "unknown"
        elif isinstance(node, AssignmentNode):
            return self.get_expression_type(node.value)
        else:
            return "unknown"

    def analyze_block(self, node: BlockNode) -> BlockNode:
        """Analyze a block of statements"""
        analyzed_statements = []
        for stmt in node.statements:
            analyzed_statements.append(self.analyze_statement(stmt))
        return BlockNode(analyzed_statements)

    def analyze_if(self, node: IfNode) -> IfNode:
        """Analyze if statement"""
        analyzed_condition = self.analyze_expression(node.condition)
        analyzed_then = self.analyze_statement(node.then_branch)
        analyzed_else = None
        if node.else_branch:
            analyzed_else = self.analyze_statement(node.else_branch)
        return IfNode(analyzed_condition, analyzed_then, analyzed_else)

    def analyze_repeat(self, node: RepeatUntilNode) -> RepeatUntilNode:
        """Analyze repeat-until loop"""
        analyzed_body = self.analyze_statement(node.body)
        analyzed_condition = self.analyze_expression(node.condition)
        return RepeatUntilNode(analyzed_body, analyzed_condition)

    def analyze_read(self, node: ReadNode) -> ReadNode:
        """Analyze read statement - marks variable as initialized with unknown type"""
        self.symbol_table[node.identifier] = "unknown"
        return node

    def analyze_write(self, node: WriteNode) -> WriteNode:
        """Analyze write statement"""
        analyzed_expression = self.analyze_expression(node.expression)
        return WriteNode(analyzed_expression)
