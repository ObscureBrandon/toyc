"""
Variable analyzer to detect undefined variables in ToyC source code.

This module walks the AST to find variables that are used before being assigned.
"""

from typing import List, Set
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


class VariableAnalyzer:
    """Analyzes AST to find variables used before definition."""

    def __init__(self):
        self.defined_vars: Set[str] = set()
        self.undefined_vars: List[str] = []  # Ordered list, no duplicates

    def analyze(self, ast: ProgramNode) -> List[str]:
        """
        Analyze the AST and return list of undefined variables.
        
        Variables are considered undefined if they are used (on RHS of assignment,
        in conditions, in expressions) before being assigned (on LHS of assignment)
        or read via a read statement.
        
        Returns:
            List of variable names in order of first use.
        """
        for stmt in ast.statements:
            self._analyze_node(stmt)
        return self.undefined_vars

    def _analyze_node(self, node: ASTNode) -> None:
        """Recursively analyze a node for variable usage."""
        if node is None:
            return

        if isinstance(node, AssignmentNode):
            # First analyze the RHS (value expression), then mark LHS as defined
            self._analyze_node(node.value)
            self.defined_vars.add(node.identifier)

        elif isinstance(node, IdentifierNode):
            # Variable usage - check if it's defined
            if node.name not in self.defined_vars and node.name not in self.undefined_vars:
                self.undefined_vars.append(node.name)

        elif isinstance(node, BinaryOpNode):
            self._analyze_node(node.left)
            self._analyze_node(node.right)

        elif isinstance(node, Int2FloatNode):
            self._analyze_node(node.child)

        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                self._analyze_node(stmt)

        elif isinstance(node, IfNode):
            # Analyze condition first
            self._analyze_node(node.condition)
            # Then analyze branches
            self._analyze_node(node.then_branch)
            if node.else_branch:
                self._analyze_node(node.else_branch)

        elif isinstance(node, RepeatUntilNode):
            # Analyze body first (it executes before condition is checked)
            self._analyze_node(node.body)
            self._analyze_node(node.condition)

        elif isinstance(node, ReadNode):
            # Read statement defines a variable
            self.defined_vars.add(node.identifier)

        elif isinstance(node, WriteNode):
            self._analyze_node(node.expression)

        elif isinstance(node, (NumberNode, FloatNode)):
            # Literals don't have variable references
            pass

        elif isinstance(node, ProgramNode):
            for stmt in node.statements:
                self._analyze_node(stmt)


def find_undefined_variables(ast: ProgramNode) -> List[str]:
    """
    Convenience function to find undefined variables in an AST.
    
    Args:
        ast: The parsed program AST
        
    Returns:
        List of undefined variable names in order of first use.
    """
    analyzer = VariableAnalyzer()
    return analyzer.analyze(ast)
