from enum import Enum


class TokenType(str, Enum):
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"

    LPAREN = "("
    RPAREN = ")"

    SEMICOLON = ";"

    PERCENT = "%"

    ASSIGN = ":="

    LT = "<"
    GT = ">"
    EQ = "=="
    NEQ = "!="
    LT_EQ = "<="
    GT_EQ = ">="

    AND = "&&"
    OR = "||"

    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"

    IF = "IF"
    ELSE = "ELSE"
    END = "END"
    REPEAT = "REPEAT"
    UNTIL = "UNTIL"
    READ = "READ"
    WRITE = "WRITE"

    ILLEGAL = "ILLEGAL"
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, literal: str):
        self.type: TokenType = type
        self.literal: str = literal

    def __repr__(self):
        return f"Token(type={self.type}, literal='{self.literal}')"


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "repeat": TokenType.REPEAT,
    "until": TokenType.UNTIL,
    "read": TokenType.READ,
    "write": TokenType.WRITE,
}


def lookup_identifier(identifier: str) -> TokenType:
    return KEYWORDS.get(identifier, TokenType.IDENTIFIER)
