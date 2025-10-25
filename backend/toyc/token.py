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
    THEN = "THEN"
    ELSE = "ELSE"
    END = "END"
    REPEAT = "REPEAT"
    UNTIL = "UNTIL"
    READ = "READ"
    WRITE = "WRITE"

    ILLEGAL = "ILLEGAL"
    EOF = "EOF"


class Token:
    def __init__(
        self, 
        type: TokenType, 
        literal: str,
        line: int = 1,
        column: int = 1,
        start_pos: int = 0,
        end_pos: int = 0
    ):
        self.type: TokenType = type
        self.literal: str = literal
        self.line: int = line
        self.column: int = column
        self.start_pos: int = start_pos
        self.end_pos: int = end_pos

    def __repr__(self):
        return f"Token(type={self.type}, literal='{self.literal}', line={self.line}, col={self.column})"


KEYWORDS = {
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "repeat": TokenType.REPEAT,
    "until": TokenType.UNTIL,
    "read": TokenType.READ,
    "write": TokenType.WRITE,
}


def lookup_identifier(identifier: str) -> TokenType:
    return KEYWORDS.get(identifier, TokenType.IDENTIFIER)
