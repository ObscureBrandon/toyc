from .lexer import Lexer
from .token import Token, TokenType
from .ast import (
    ASTNode,
    ProgramNode,
    BinaryOpNode,
    NumberNode,
    FloatNode,
    IdentifierNode,
    AssignmentNode,
    ParseError,
)


class Parser:
    """Recursive descent parser for ToyC language"""

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token: Token | None = None
        self.peek_token: Token | None = None
        self.position = 0

        # Load first two tokens
        self.advance()
        self.advance()

    def advance(self):
        """Move to the next token"""
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()
        self.position += 1

    def expect_token(self, expected_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        if self.current_token.type != expected_type:
            raise ParseError(
                f"Expected {expected_type}, got {self.current_token.type}",
                self.position,
            )
        token = self.current_token
        self.advance()
        return token

    def parse_program(self) -> ProgramNode:
        """
        Program → Statement*
        Entry point for parsing
        """
        statements = []

        while self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except ParseError:
                # Skip to next potential statement on error
                self.advance()

        return ProgramNode(statements)

    def parse_statement(self) -> ASTNode:
        """
        Statement → Assignment | Expression
        """
        # Look ahead for assignment: IDENTIFIER := ...
        if (
            self.current_token.type == TokenType.IDENTIFIER
            and self.peek_token.type == TokenType.ASSIGN
        ):
            return self.parse_assignment()
        else:
            return self.parse_expression()

    def parse_assignment(self) -> AssignmentNode:
        """
        Assignment → IDENTIFIER ":=" Expression
        """
        identifier_token = self.expect_token(TokenType.IDENTIFIER)
        self.expect_token(TokenType.ASSIGN)
        value = self.parse_expression()

        return AssignmentNode(identifier_token.literal, value)

    def parse_expression(self) -> ASTNode:
        """
        Expression → Term ((PLUS | MINUS) Term)*
        """
        left = self.parse_term()

        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_term()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_term(self) -> ASTNode:
        """
        Term → Factor ((ASTERISK | SLASH) Factor)*
        """
        left = self.parse_factor()

        while self.current_token.type in [TokenType.ASTERISK, TokenType.SLASH]:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_factor(self) -> ASTNode:
        """
        Factor → NUMBER | FLOAT | IDENTIFIER | LPAREN Expression RPAREN
        """
        token = self.current_token
        if token is None:
            raise ParseError(
                "Unexpected end of input while parsing factor",
                self.position,
            )

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(int(token.literal))

        elif token.type == TokenType.FLOAT:
            self.advance()
            return FloatNode(float(token.literal))

        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return IdentifierNode(token.literal)

        elif token.type == TokenType.LPAREN:
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.expect_token(TokenType.RPAREN)  # consume ')'
            return expr

        else:
            raise ParseError(
                f"Unexpected token in factor: {token.type} '{token.literal}'",
                self.position,
            )


def parse_code(source_code: str) -> ProgramNode:
    """
    Convenience function to parse source code string
    """
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    return parser.parse_program()
