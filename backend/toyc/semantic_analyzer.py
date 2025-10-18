from typing import Dict, Literal
from .ast import (
    ASTNode,
    ProgramNode,
    BinaryOpNode,
    NumberNode,
    FloatNode,
    IdentifierNode,
    AssignmentNode,
    Int2FloatNode,
)


NodeType = Literal["int", "float", "unknown"]


class SemanticAnalyzer:
    """Performs semantic analysis with type checking and coercion"""

    def __init__(self):
        self.symbol_table: Dict[str, NodeType] = {}

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
