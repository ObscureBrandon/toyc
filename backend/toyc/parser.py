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
    BlockNode,
    IfNode,
    RepeatUntilNode,
    ReadNode,
    WriteNode,
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
        if self.current_token is None or self.current_token.type != expected_type:
            actual_type = self.current_token.type if self.current_token else "None"
            raise ParseError(
                f"Expected {expected_type}, got {actual_type}",
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

        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except ParseError:
                self.advance()

        return ProgramNode(statements)

    def parse_statement(self) -> ASTNode:
        """
        Statement → IfStmt | RepeatStmt | ReadStmt | WriteStmt | AssignStmt | ExprStmt
        """
        if not self.current_token:
            raise ParseError("Unexpected end of input", self.position)
        
        token_type = self.current_token.type

        if token_type == TokenType.IF:
            return self.parse_if_statement()
        elif token_type == TokenType.REPEAT:
            return self.parse_repeat_until()
        elif token_type == TokenType.READ:
            return self.parse_read_statement()
        elif token_type == TokenType.WRITE:
            return self.parse_write_statement()
        elif token_type == TokenType.IDENTIFIER and self.peek_token and self.peek_token.type == TokenType.ASSIGN:
            return self.parse_assignment()
        else:
            expr = self.parse_expression()
            if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                self.advance()
            return expr

    def parse_block(self, terminators: list[TokenType]) -> BlockNode:
        """
        Parse statements until hitting a terminator keyword
        Block → Statement+
        """
        statements = []
        while self.current_token and self.current_token.type not in terminators:
            if self.current_token.type == TokenType.EOF:
                terminator_names = ", ".join([str(t) for t in terminators])
                raise ParseError(f"Expected one of {terminator_names} before end of file", self.position)
            stmt = self.parse_statement()
            statements.append(stmt)
        return BlockNode(statements)

    def parse_if_statement(self) -> IfNode:
        """
        IfStmt → IF LPAREN Expression RPAREN THEN Block (ELSE Block)? END
        """
        self.expect_token(TokenType.IF)
        self.expect_token(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect_token(TokenType.RPAREN)
        self.expect_token(TokenType.THEN)
        
        then_branch = self.parse_block([TokenType.ELSE, TokenType.END])
        
        else_branch = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            else_branch = self.parse_block([TokenType.END])
        
        self.expect_token(TokenType.END)
        return IfNode(condition, then_branch, else_branch)

    def parse_repeat_until(self) -> RepeatUntilNode:
        """
        RepeatStmt → REPEAT Block UNTIL Expression SEMICOLON
        """
        self.expect_token(TokenType.REPEAT)
        
        body = self.parse_block([TokenType.UNTIL])
        
        self.expect_token(TokenType.UNTIL)
        condition = self.parse_expression()
        self.expect_token(TokenType.SEMICOLON)
        
        return RepeatUntilNode(body, condition)

    def parse_read_statement(self) -> ReadNode:
        """
        ReadStmt → READ IDENTIFIER SEMICOLON
        """
        self.expect_token(TokenType.READ)
        identifier_token = self.expect_token(TokenType.IDENTIFIER)
        self.expect_token(TokenType.SEMICOLON)
        return ReadNode(identifier_token.literal)

    def parse_write_statement(self) -> WriteNode:
        """
        WriteStmt → WRITE Expression SEMICOLON
        """
        self.expect_token(TokenType.WRITE)
        expression = self.parse_expression()
        self.expect_token(TokenType.SEMICOLON)
        return WriteNode(expression)

    def parse_assignment(self) -> AssignmentNode:
        """
        Assignment → IDENTIFIER ":=" Expression SEMICOLON
        """
        identifier_token = self.expect_token(TokenType.IDENTIFIER)
        self.expect_token(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect_token(TokenType.SEMICOLON)
        return AssignmentNode(identifier_token.literal, value)

    def parse_expression(self) -> ASTNode:
        """
        Expression → OrExpr
        """
        return self.parse_or_expression()

    def parse_or_expression(self) -> ASTNode:
        """
        OrExpr → AndExpr (OR AndExpr)*
        """
        left = self.parse_and_expression()

        while self.current_token and self.current_token.type == TokenType.OR:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_and_expression()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_and_expression(self) -> ASTNode:
        """
        AndExpr → CompExpr (AND CompExpr)*
        """
        left = self.parse_comparison()

        while self.current_token and self.current_token.type == TokenType.AND:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_comparison(self) -> ASTNode:
        """
        CompExpr → AddExpr ((LT | GT | LT_EQ | GT_EQ | EQ | NEQ) AddExpr)*
        """
        left = self.parse_additive()

        while self.current_token and self.current_token.type in [
            TokenType.LT, TokenType.GT, TokenType.LT_EQ, 
            TokenType.GT_EQ, TokenType.EQ, TokenType.NEQ
        ]:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_additive()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_additive(self) -> ASTNode:
        """
        AddExpr → Term ((PLUS | MINUS) Term)*
        """
        left = self.parse_term()

        while self.current_token and self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.current_token.literal
            self.advance()
            right = self.parse_term()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_term(self) -> ASTNode:
        """
        Term → Factor ((ASTERISK | SLASH | PERCENT) Factor)*
        """
        left = self.parse_factor()

        while self.current_token and self.current_token.type in [TokenType.ASTERISK, TokenType.SLASH, TokenType.PERCENT]:
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
