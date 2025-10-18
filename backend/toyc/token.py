from enum import Enum


class TokenType(str, Enum):
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"
    LPAREN = "("
    RPAREN = ")"
    EQUAL = "="
    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, literal: str):
        self.type: TokenType = type
        self.literal: str = literal

    def __repr__(self):
        return f"Token(type={self.type}, literal='{self.literal}')"

