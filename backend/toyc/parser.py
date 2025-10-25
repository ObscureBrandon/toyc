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

# Operator precedence levels (higher = tighter binding)
LOWEST = 0
OR_PREC = 1
AND_PREC = 2
COMPARISON_PREC = 3
ADDITIVE_PREC = 4
MULTIPLICATIVE_PREC = 5

PRECEDENCES = {
    TokenType.OR: OR_PREC,
    TokenType.AND: AND_PREC,
    TokenType.EQ: COMPARISON_PREC,
    TokenType.NEQ: COMPARISON_PREC,
    TokenType.LT: COMPARISON_PREC,
    TokenType.GT: COMPARISON_PREC,
    TokenType.LT_EQ: COMPARISON_PREC,
    TokenType.GT_EQ: COMPARISON_PREC,
    TokenType.PLUS: ADDITIVE_PREC,
    TokenType.MINUS: ADDITIVE_PREC,
    TokenType.ASTERISK: MULTIPLICATIVE_PREC,
    TokenType.SLASH: MULTIPLICATIVE_PREC,
    TokenType.PERCENT: MULTIPLICATIVE_PREC,
}

INFIX_OPERATORS = {
    TokenType.OR, TokenType.AND,
    TokenType.EQ, TokenType.NEQ, 
    TokenType.LT, TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ,
    TokenType.PLUS, TokenType.MINUS,
    TokenType.ASTERISK, TokenType.SLASH, TokenType.PERCENT,
}


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

    def current_precedence(self) -> int:
        """Get precedence of current token"""
        if self.current_token:
            return PRECEDENCES.get(self.current_token.type, LOWEST)
        return LOWEST

    def peek_precedence(self) -> int:
        """Get precedence of peek token"""
        if self.peek_token:
            return PRECEDENCES.get(self.peek_token.type, LOWEST)
        return LOWEST

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
            self.expect_token(TokenType.SEMICOLON)
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

    def parse_expression(self, precedence: int = LOWEST) -> ASTNode:
        """
        Pratt parser for expressions with precedence climbing
        Expression → Prefix (Infix Prefix)*
        """
        left = self.parse_prefix()

        while self.current_token and self.current_precedence() > precedence:
            if self.current_token.type not in INFIX_OPERATORS:
                return left
            
            left = self.parse_infix_expression(left)

        return left

    def parse_prefix(self) -> ASTNode:
        """
        Prefix → NUMBER | FLOAT | IDENTIFIER | LPAREN Expression RPAREN
        """
        token = self.current_token
        if token is None:
            raise ParseError(
                "Unexpected end of input while parsing expression",
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
            self.advance()
            expr = self.parse_expression()
            self.expect_token(TokenType.RPAREN)
            return expr

        else:
            raise ParseError(
                f"Unexpected token in expression: {token.type} '{token.literal}'",
                self.position,
            )

    def parse_infix_expression(self, left: ASTNode) -> ASTNode:
        """
        Infix → left OPERATOR right
        Parses binary operations given left operand
        """
        if self.current_token is None:
            raise ParseError("Unexpected end of input in infix expression", self.position)
        
        operator = self.current_token.literal
        precedence = self.current_precedence()
        self.advance()
        right = self.parse_expression(precedence)
        return BinaryOpNode(operator, left, right)


def parse_code(source_code: str) -> ProgramNode:
    """
    Convenience function to parse source code string
    """
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    return parser.parse_program()
