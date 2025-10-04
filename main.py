from enum import StrEnum
from typing import override


class TokenType(StrEnum):
    PLUS = "+"
    MINUS = "-"
    ASTRESIK = "*"
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

    @override
    def __repr__(self):
        return f"Token(type={self.type}, literal='{self.literal}')"


class Lexer:
    def __init__(self, input: str):
        self.input: str = input
        self.position: int = 0
        self.read_position: int = 0
        self.ch: str = ""
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = "\0"
        else:
            self.ch = self.input[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def skip_whitespace(self):
        while self.ch in " \t\n\r":
            self.read_char()

    def _new_token(self, type: TokenType, literal: str) -> Token:
        token = Token(type, literal)
        return token

    def read_identifier(self) -> str:
        start_position = self.position
        while self.ch.isalpha():
            self.read_char()
        return self.input[start_position : self.position]

    def read_number(self) -> str:
        start_position = self.position
        while self.ch.isdigit():
            self.read_char()
        return self.input[start_position : self.position]

    def next_token(self) -> Token:
        self.skip_whitespace()

        token: Token | None = None
        match self.ch:
            case "+":
                token = self._new_token(TokenType.PLUS, self.ch)
            case "-":
                token = self._new_token(TokenType.MINUS, self.ch)
            case "*":
                token = self._new_token(TokenType.ASTRESIK, self.ch)
            case "/":
                token = self._new_token(TokenType.SLASH, self.ch)
            case "(":
                token = self._new_token(TokenType.LPAREN, self.ch)
            case ")":
                token = self._new_token(TokenType.RPAREN, self.ch)
            case "=":
                token = self._new_token(TokenType.EQUAL, self.ch)
            case "\0":
                token = self._new_token(TokenType.EOF, "")
            case _:
                if self.ch.isascii():
                    literal = self.read_identifier()
                    token = self._new_token(TokenType.IDENTIFIER, literal)
                    return token
                elif self.ch.isdigit():
                    literal = self.read_number()
                    if self.ch == ".":
                        self.read_char()
                        fractional = self.read_number()
                        literal += "." + fractional
                        token = self._new_token(TokenType.FLOAT, literal)
                    else:
                        token = self._new_token(TokenType.NUMBER, literal)
                    return token
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)

        self.read_char()
        return token


def main():
    print("TinyCompiler REPL:")
    print("Type 'exit' to quit.")
    while True:
        try:
            line = input("\n>>> ")
            if line.strip().lower() == "exit":
                break

            lexer = Lexer(line)
            ident_count = 0
            while True:
                tok = lexer.next_token()
                if tok.type == TokenType.IDENTIFIER:
                    ident_count += 1
                    print(f"id{ident_count}", end=" ")
                elif tok.type == TokenType.ILLEGAL:
                    print("ILLEGAL", end=" ")
                else:
                    print(tok.literal, end=" ")

                if tok.type == TokenType.EOF:
                    break
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
