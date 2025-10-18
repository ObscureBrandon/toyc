from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class ASTNode(ABC):
    """Base class for all AST nodes"""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize AST node to dictionary for JSON response"""
        pass


class ProgramNode(ASTNode):
    """Root node containing all statements"""

    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "statements": [stmt.to_dict() for stmt in self.statements],
        }


class BinaryOpNode(ASTNode):
    """Binary operation node (e.g., +, -, *, /)"""

    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.operator = operator
        self.left = left
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }


class NumberNode(ASTNode):
    """Integer literal node"""

    def __init__(self, value: int):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Number", "value": self.value}


class FloatNode(ASTNode):
    """Float literal node"""

    def __init__(self, value: float):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Float", "value": self.value}


class IdentifierNode(ASTNode):
    """Variable/identifier node"""

    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Identifier", "name": self.name}


class AssignmentNode(ASTNode):
    """Assignment statement node (e.g., x = 5)"""

    def __init__(self, identifier: str, value: ASTNode):
        self.identifier = identifier
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Assignment",
            "identifier": self.identifier,
            "value": self.value.to_dict(),
        }


class Int2FloatNode(ASTNode):
    """Type coercion node for converting int to float"""

    def __init__(self, child: ASTNode):
        self.child = child

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Int2Float",
            "child": self.child.to_dict(),
        }


class ParseError(Exception):
    """Parser error with position information"""

    def __init__(self, message: str, position: int = 0):
        self.message = message
        self.position = position
        super().__init__(f"{message} at position {position}")

