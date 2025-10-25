import traceback

from .lexer import Lexer
from .token import Token, TokenType, lookup_identifier
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
    ErrorNode,
    ParseError,
)
from .semantic_analyzer import SemanticAnalyzer


class TracingLexer(Lexer):
    """Extended lexer that records step-by-step execution"""

    def __init__(self, input: str):
        self.steps = []
        self.step_id = 0
        super().__init__(input)

    def trace_step(self, description: str, state: dict, position: int | None = None):
        """Record a step in the lexing process"""
        self.steps.append(
            {
                "phase": "lexing",
                "step_id": self.step_id,
                "position": position if position is not None else self.position,
                "description": description,
                "state": state,
            }
        )
        self.step_id += 1

    def skip_single_line_comment(self):
        """Skip single-line comment with tracing"""
        comment_start = self.position - 2
        comment_content = ""
        while self.ch != "\n" and self.ch != "\0":
            comment_content += self.ch
            self.read_char()
        self.trace_step(
            f"Skipped single-line comment: '%%{comment_content}'",
            {
                "comment_type": "single_line",
                "comment_start": comment_start,
                "comment_content": comment_content,
                "action": "skip_comment",
            },
        )

    def skip_multi_line_comment(self):
        """Skip multi-line comment with tracing"""
        comment_start = self.position - 1
        comment_content = ""
        while self.ch != "}" and self.ch != "\0":
            comment_content += self.ch
            self.read_char()
        if self.ch == "}":
            self.read_char()
        self.trace_step(
            f"Skipped multi-line comment: '{{{comment_content}}}'",
            {
                "comment_type": "multi_line",
                "comment_start": comment_start,
                "comment_content": comment_content,
                "action": "skip_comment",
            },
        )

    def read_char(self):
        # Just read the character without verbose tracing
        super().read_char()

    def read_identifier(self) -> tuple[str, int, int]:
        """Read identifier with incremental tracing"""
        start_position = self.position
        start_line = self.line
        start_column = self.column
        current_lexeme = ""

        while self.ch.isalpha():
            current_lexeme += self.ch
            self.trace_step(
                f"Building IDENTIFIER: '{current_lexeme}'",
                {
                    "current_char": self.ch,
                    "current_lexeme": current_lexeme,
                    "action": "build_token",
                    "token_type": "IDENTIFIER",
                },
            )
            self.read_char()

        return self.input[start_position : self.position], start_line, start_column

    def read_number(self) -> tuple[str, int, int]:
        """Read number with incremental tracing"""
        start_position = self.position
        start_line = self.line
        start_column = self.column
        current_lexeme = ""

        while self.ch.isdigit():
            current_lexeme += self.ch
            self.trace_step(
                f"Building NUMBER: '{current_lexeme}'",
                {
                    "current_char": self.ch,
                    "current_lexeme": current_lexeme,
                    "action": "build_token",
                    "token_type": "NUMBER",
                },
            )
            self.read_char()

        return self.input[start_position : self.position], start_line, start_column

    def next_token(self) -> Token:
        """Create next token with tracing"""
        start_position = self.position

        # Skip whitespace without tracing
        if self.ch in " \t\n\r":
            self.skip_whitespace()

        token = None

        # Record what type of token we're creating with simplified tracing
        if self.ch == "+":
            self.trace_step(
                f"Creating PLUS token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "PLUS",
                },
            )
            token = self._new_token(TokenType.PLUS, self.ch)
        elif self.ch == "-":
            self.trace_step(
                f"Creating MINUS token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "MINUS",
                },
            )
            token = self._new_token(TokenType.MINUS, self.ch)
        elif self.ch == "*":
            self.trace_step(
                f"Creating ASTERISK token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "ASTERISK",
                },
            )
            token = self._new_token(TokenType.ASTERISK, self.ch)
        elif self.ch == "/":
            self.trace_step(
                f"Creating SLASH token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "SLASH",
                },
            )
            token = self._new_token(TokenType.SLASH, self.ch)
        elif self.ch == "(":
            self.trace_step(
                f"Creating LPAREN token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "LPAREN",
                },
            )
            token = self._new_token(TokenType.LPAREN, self.ch)
        elif self.ch == ")":
            self.trace_step(
                f"Creating RPAREN token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "RPAREN",
                },
            )
            token = self._new_token(TokenType.RPAREN, self.ch)
        elif self.ch == ":":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating ASSIGN token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "ASSIGN",
                    },
                )
                self.read_char()
                token = self._new_token(TokenType.ASSIGN, ":=")
                self.read_char()
                self.trace_step(
                    f"Created ASSIGN token: ':='",
                    {
                        "token_type": "ASSIGN",
                        "literal": ":=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == "<":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating LT_EQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "LT_EQ",
                    },
                )
                self.read_char()
                token = self._new_token(TokenType.LT_EQ, "<=")
                self.read_char()
                self.trace_step(
                    f"Created LT_EQ token: '<='",
                    {
                        "token_type": "LT_EQ",
                        "literal": "<=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                self.trace_step(
                    f"Creating LT token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "LT",
                    },
                )
                token = self._new_token(TokenType.LT, self.ch)
        elif self.ch == ">":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating GT_EQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "GT_EQ",
                    },
                )
                self.read_char()
                token = self._new_token(TokenType.GT_EQ, ">=")
                self.read_char()
                self.trace_step(
                    f"Created GT_EQ token: '>='",
                    {
                        "token_type": "GT_EQ",
                        "literal": ">=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                self.trace_step(
                    f"Creating GT token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "GT",
                    },
                )
                token = self._new_token(TokenType.GT, self.ch)
        elif self.ch == ":":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating ASSIGN token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "ASSIGN",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.ASSIGN, literal)
                self.read_char()
                self.trace_step(
                    f"Created ASSIGN token: ':='",
                    {
                        "token_type": "ASSIGN",
                        "literal": ":=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == "<":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating LT_EQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "LT_EQ",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.LT_EQ, literal)
                self.read_char()
                self.trace_step(
                    f"Created LT_EQ token: '<='",
                    {
                        "token_type": "LT_EQ",
                        "literal": "<=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                self.trace_step(
                    f"Creating LT token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "LT",
                    },
                )
                token = self._new_token(TokenType.LT, self.ch)
        elif self.ch == ">":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating GT_EQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "GT_EQ",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.GT_EQ, literal)
                self.read_char()
                self.trace_step(
                    f"Created GT_EQ token: '>='",
                    {
                        "token_type": "GT_EQ",
                        "literal": ">=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                self.trace_step(
                    f"Creating GT token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "GT",
                    },
                )
                token = self._new_token(TokenType.GT, self.ch)
        elif self.ch == "=":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating EQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "EQ",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.EQ, literal)
                self.read_char()
                self.trace_step(
                    f"Created EQ token: '=='",
                    {
                        "token_type": "EQ",
                        "literal": "==",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == "!":
            if self.peek_char() == "=":
                self.trace_step(
                    f"Creating NEQ token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "NEQ",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.NEQ, literal)
                self.read_char()
                self.trace_step(
                    f"Created NEQ token: '!='",
                    {
                        "token_type": "NEQ",
                        "literal": "!=",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == "&":
            if self.peek_char() == "&":
                self.trace_step(
                    f"Creating AND token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "AND",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.AND, literal)
                self.read_char()
                self.trace_step(
                    f"Created AND token: '&&'",
                    {
                        "token_type": "AND",
                        "literal": "&&",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == "|":
            if self.peek_char() == "|":
                self.trace_step(
                    f"Creating OR token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "OR",
                    },
                )
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                token = self._new_token(TokenType.OR, literal)
                self.read_char()
                self.trace_step(
                    f"Created OR token: '||'",
                    {
                        "token_type": "OR",
                        "literal": "||",
                        "action": "token_created",
                    },
                )
                return token
            else:
                token = self._new_token(TokenType.ILLEGAL, self.ch)
        elif self.ch == ";":
            self.trace_step(
                f"Creating SEMICOLON token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "SEMICOLON",
                },
            )
            token = self._new_token(TokenType.SEMICOLON, self.ch)
        elif self.ch == "%":
            if self.peek_char() == "%":
                self.trace_step(
                    f"Found single-line comment at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_comment",
                        "comment_type": "single_line",
                    },
                )
                self.read_char()
                self.read_char()
                self.skip_single_line_comment()
                return self.next_token()
            else:
                self.trace_step(
                    f"Creating PERCENT token at position {start_position}",
                    {
                        "current_char": self.ch,
                        "action": "identify_token",
                        "token_type": "PERCENT",
                    },
                )
                token = self._new_token(TokenType.PERCENT, self.ch)
        elif self.ch == "{":
            self.trace_step(
                f"Found multi-line comment at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_comment",
                    "comment_type": "multi_line",
                },
            )
            self.read_char()
            self.skip_multi_line_comment()
            return self.next_token()
        elif self.ch == "\0":
            self.trace_step(
                f"Creating EOF token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "EOF",
                },
            )
            token = self._new_token(TokenType.EOF, "")
        elif self.is_letter(self.ch):
            self.trace_step(
                f"Creating IDENTIFIER/KEYWORD token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "IDENTIFIER/KEYWORD",
                },
            )
            literal, start_line, start_column = self.read_identifier()
            token_type = lookup_identifier(literal)
            start_pos = self.position - len(literal)
            end_pos = self.position - 1
            token = Token(token_type, literal, start_line, start_column, start_pos, end_pos)
            self.trace_step(
                f"Created {token_type.name} token: '{literal}'",
                {
                    "token_type": token_type.name,
                    "literal": literal,
                    "action": "token_created",
                },
            )
            return token
        elif self.is_digit(self.ch):
            self.trace_step(
                f"Creating NUMBER token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "NUMBER",
                },
            )
            literal, start_line, start_column = self.read_number()
            start_pos = self.position - len(literal)

            if self.ch == ".":
                self.trace_step(
                    "Found decimal point, converting to FLOAT token",
                    {
                        "current_char": self.ch,
                        "action": "detect_decimal",
                        "current_lexeme": literal,
                    },
                )
                literal += "."
                self.read_char()

                fractional_start = len(literal)
                fractional, _, _ = self.read_number()
                literal += fractional

                end_pos = self.position - 1
                token = Token(TokenType.FLOAT, literal, start_line, start_column, start_pos, end_pos)
                token_type = "FLOAT"

                self.trace_step(
                    f"Built complete FLOAT: '{literal}'",
                    {
                        "current_lexeme": literal,
                        "action": "complete_float",
                        "token_type": "FLOAT",
                    },
                )

                if self.is_letter(self.ch):
                    while self.is_letter(self.ch) or self.is_digit(self.ch):
                        literal += self.ch
                        self.read_char()
                    end_pos = self.position - 1
                    token = Token(TokenType.ILLEGAL, literal, start_line, start_column, start_pos, end_pos)
                    token_type = "ILLEGAL"
                    self.trace_step(
                        f"Invalid identifier (starts with number): '{literal}'",
                        {
                            "literal": literal,
                            "action": "invalid_identifier",
                            "token_type": "ILLEGAL",
                        },
                    )

            else:
                if self.is_letter(self.ch):
                    while self.is_letter(self.ch) or self.is_digit(self.ch):
                        literal += self.ch
                        self.read_char()
                    end_pos = self.position - 1
                    token = Token(TokenType.ILLEGAL, literal, start_line, start_column, start_pos, end_pos)
                    token_type = "ILLEGAL"
                    self.trace_step(
                        f"Invalid identifier (starts with number): '{literal}'",
                        {
                            "literal": literal,
                            "action": "invalid_identifier",
                            "token_type": "ILLEGAL",
                        },
                    )
                else:
                    end_pos = self.position - 1
                    token = Token(TokenType.NUMBER, literal, start_line, start_column, start_pos, end_pos)
                    token_type = "NUMBER"

            self.trace_step(
                f"Created {token_type} token: '{literal}'",
                {
                    "token_type": token_type,
                    "literal": literal,
                    "action": "token_created",
                },
            )
            return token
        else:
            self.trace_step(
                f"Creating ILLEGAL token at position {start_position}",
                {
                    "current_char": self.ch,
                    "action": "identify_token",
                    "token_type": "ILLEGAL",
                },
            )
            token = self._new_token(TokenType.ILLEGAL, self.ch)

        self.read_char()

        # Record token creation
        self.trace_step(
            f"Created {token.type.name} token: '{token.literal}'",
            {
                "token_type": token.type.name,
                "literal": token.literal,
                "action": "token_created",
            },
        )

        return token


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


class TracingParser:
    """Extended parser that records step-by-step execution"""

    def __init__(self, lexer: TracingLexer):
        self.lexer = lexer
        self.current_token: Token | None = None
        self.peek_token: Token | None = None
        self.position = 0
        self.steps = []
        self.step_id = len(lexer.steps)  # Continue from lexer steps
        self.node_id_counter = 0  # For tracking node relationships
        self.node_stack = []  # Stack to track parent-child relationships
        self.parsed_statements = []  # Store successfully parsed statements

        # Load first two tokens
        self.advance()
        self.advance()

    def trace_step(self, description: str, state: dict):
        """Record a step in the parsing process"""
        self.steps.append(
            {
                "phase": "parsing",
                "step_id": self.step_id,
                "position": self.position,
                "description": description,
                "state": state,
            }
        )
        self.step_id += 1

    def get_next_node_id(self) -> str:
        """Generate a unique node ID for tracking relationships"""
        self.node_id_counter += 1
        return f"node_{self.node_id_counter}"

    def trace_ast_node_creation(
        self,
        description: str,
        node: ASTNode,
        node_id: str,
        parent_id: str | None = None,
    ):
        """Record AST node creation with full node data and relationships"""
        self.trace_step(
            description,
            {
                "action": "create_ast_node",
                "node_id": node_id,
                "parent_id": parent_id,
                "ast_node": node.to_dict(),
                "node_type": type(node).__name__,
            },
        )

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

    def advance(self):
        """Move to the next token"""
        self.trace_step(
            f"Advancing from {self.current_token.type.name if self.current_token else 'None'} to {self.peek_token.type.name if self.peek_token else 'next token'}",
            {
                "current_token": self.current_token.type.name
                if self.current_token
                else None,
                "peek_token": self.peek_token.type.name if self.peek_token else None,
                "action": "advance_token",
            },
        )

        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()
        self.position += 1

        self.trace_step(
            f"Now at token: {self.current_token.type.name if self.current_token else 'None'} '{self.current_token.literal if self.current_token else ''}'",
            {
                "current_token": self.current_token.type.name
                if self.current_token
                else None,
                "current_literal": self.current_token.literal
                if self.current_token
                else None,
                "peek_token": self.peek_token.type.name if self.peek_token else None,
                "action": "token_advanced",
            },
        )

    def parse_program(self) -> ProgramNode:
        """Parse the entire program"""
        self.trace_step(
            "Starting program parsing",
            {"action": "start_program", "grammar_rule": "Program → Statement*"},
        )

        statements = []

        while self.current_token and self.current_token.type != TokenType.EOF:
            self.trace_step(
                f"Parsing statement starting with {self.current_token.type.name}",
                {
                    "current_token": self.current_token.type.name,
                    "action": "start_statement",
                    "grammar_rule": "Statement → Assignment | Expression",
                },
            )

            try:
                stmt = self.parse_statement()
                statements.append(stmt)
                self.parsed_statements.append(stmt)  # Store for error recovery

                self.trace_step(
                    f"Completed statement of type {type(stmt).__name__}",
                    {
                        "statement_type": type(stmt).__name__,
                        "action": "complete_statement",
                    },
                )

            except ParseError as e:
                # Re-raise the error so it can be handled by trace_compilation
                raise

        program = ProgramNode(statements)
        program_node_id = self.get_next_node_id()

        self.trace_ast_node_creation(
            f"Created program node with {len(statements)} statements",
            program,
            program_node_id,
            None,
        )

        self.trace_step(
            f"Completed program with {len(statements)} statements",
            {"statement_count": len(statements), "action": "complete_program"},
        )

        return program

    def parse_statement(self) -> ASTNode:
        if not self.current_token:
            raise ParseError("Unexpected end of input", self.position, 0, 0)
        
        if self.current_token.type == TokenType.IF:
            self.trace_step(
                "Detected if statement",
                {
                    "action": "detect_if",
                    "grammar_rule": "IfStmt → IF LPAREN Expression RPAREN Block (ELSE Block)? END",
                },
            )
            return self.parse_if_statement()
        
        elif self.current_token.type == TokenType.REPEAT:
            self.trace_step(
                "Detected repeat statement",
                {
                    "action": "detect_repeat",
                    "grammar_rule": "RepeatStmt → REPEAT Block UNTIL Expression SEMICOLON",
                },
            )
            return self.parse_repeat_until()
        
        elif self.current_token.type == TokenType.READ:
            self.trace_step(
                "Detected read statement",
                {
                    "action": "detect_read",
                    "grammar_rule": "ReadStmt → READ IDENTIFIER SEMICOLON",
                },
            )
            return self.parse_read_statement()
        
        elif self.current_token.type == TokenType.WRITE:
            self.trace_step(
                "Detected write statement",
                {
                    "action": "detect_write",
                    "grammar_rule": "WriteStmt → WRITE Expression SEMICOLON",
                },
            )
            return self.parse_write_statement()
        
        elif (
            self.current_token.type == TokenType.IDENTIFIER
            and self.peek_token
            and self.peek_token.type == TokenType.ASSIGN
        ):
            self.trace_step(
                f"Detected assignment: {self.current_token.literal} :=",
                {
                    "identifier": self.current_token.literal,
                    "action": "detect_assignment",
                    "grammar_rule": "Assignment → IDENTIFIER ':=' Expression",
                },
            )
            return self.parse_assignment()
        else:
            self.trace_step(
                "Parsing as expression",
                {
                    "action": "parse_expression",
                    "grammar_rule": "Expression → Term ((PLUS | MINUS) Term)*",
                },
            )
            expr = self.parse_expression()
            
            self.trace_step("Expecting statement-terminating semicolon", {"action": "expect_semicolon"})
            if not self.current_token or self.current_token.type != TokenType.SEMICOLON:
                line = self.current_token.line if self.current_token else 1
                column = self.current_token.column if self.current_token else 1
                raise ParseError("Expected ';' after expression statement", self.position, line, column)
            self.advance()
            
            return expr

    def parse_assignment(self) -> AssignmentNode:
        """Parse assignment statement"""
        identifier_token = self.current_token

        if not identifier_token:
            raise ParseError("Expected identifier for assignment", self.position, 0, 0)

        self.trace_step(
            f"Parsing assignment to '{identifier_token.literal}'",
            {"identifier": identifier_token.literal, "action": "start_assignment"},
        )

        self.advance()  # consume identifier
        self.advance()  # consume ':='

        # Push assignment node context for tracking children
        assignment_node_id = self.get_next_node_id()
        self.node_stack.append(assignment_node_id)

        value = self.parse_expression()

        # Pop the assignment context
        self.node_stack.pop()

        assignment = AssignmentNode(identifier_token.literal, value)

        self.trace_ast_node_creation(
            f"Created assignment node: {identifier_token.literal} := ...",
            assignment,
            assignment_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )

        if not self.current_token or self.current_token.type != TokenType.SEMICOLON:
            line = self.current_token.line if self.current_token else 1
            column = self.current_token.column if self.current_token else 1
            self.parsed_statements.append(assignment)
            raise ParseError("Expected ';' after assignment", self.position, line, column)

        self.trace_step("Consuming assignment semicolon", {"action": "consume_semicolon"})
        self.advance()

        return assignment

    def parse_block(self, terminators: list[TokenType]) -> BlockNode:
        self.trace_step(
            f"Starting block parsing (terminators: {[t.name for t in terminators]})",
            {
                "action": "start_block",
                "terminators": [t.name for t in terminators],
                "grammar_rule": "Block → Statement+",
            },
        )
        
        statements = []
        block_node_id = self.get_next_node_id()
        self.node_stack.append(block_node_id)
        
        while (
            self.current_token
            and self.current_token.type != TokenType.EOF
            and self.current_token.type not in terminators
        ):
            self.trace_step(
                f"Parsing statement in block (token: {self.current_token.type.name})",
                {
                    "action": "parse_block_statement",
                    "current_token": self.current_token.type.name,
                    "statement_count": len(statements),
                },
            )
            
            stmt = self.parse_statement()
            statements.append(stmt)
            
            self.trace_step(
                f"Added statement {len(statements)} to block",
                {
                    "action": "add_block_statement",
                    "statement_type": type(stmt).__name__,
                    "statement_count": len(statements),
                },
            )
        
        self.node_stack.pop()
        
        block = BlockNode(statements)
        self.trace_ast_node_creation(
            f"Created block node with {len(statements)} statements",
            block,
            block_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return block

    def parse_if_statement(self) -> IfNode:
        self.trace_step(
            "Starting if statement parsing",
            {
                "action": "start_if",
                "grammar_rule": "IfStmt → IF LPAREN Expression RPAREN THEN Block (ELSE Block)? END",
            },
        )
        
        if_node_id = self.get_next_node_id()
        self.node_stack.append(if_node_id)
        
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.LPAREN:
            raise ParseError("Expected '(' after 'if'", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.trace_step(
            "Parsing if condition",
            {"action": "parse_if_condition", "current_token": self.current_token.type.name},
        )
        self.advance()
        
        condition = self.parse_expression()
        
        if not self.current_token or self.current_token.type != TokenType.RPAREN:
            raise ParseError("Expected ')' after if condition", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.THEN:
            raise ParseError("Expected 'then' after if condition", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.trace_step(
            "Found 'then' keyword",
            {"action": "expect_then", "current_token": self.current_token.type.name},
        )
        self.advance()
        
        self.trace_step(
            "Parsing if then-branch",
            {"action": "parse_then_branch"},
        )
        
        then_branch = self.parse_block([TokenType.ELSE, TokenType.END])
        
        else_branch = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.trace_step(
                "Found else clause, parsing else-branch",
                {"action": "parse_else_branch"},
            )
            self.advance()
            else_branch = self.parse_block([TokenType.END])
        
        if not self.current_token or self.current_token.type != TokenType.END:
            raise ParseError("Expected 'end' after if statement", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.advance()
        
        self.node_stack.pop()
        
        if_node = IfNode(condition, then_branch, else_branch)
        self.trace_ast_node_creation(
            f"Created if node (with{'out' if else_branch is None else ''} else)",
            if_node,
            if_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return if_node

    def parse_repeat_until(self) -> RepeatUntilNode:
        self.trace_step(
            "Starting repeat-until parsing",
            {
                "action": "start_repeat",
                "grammar_rule": "RepeatStmt → REPEAT Block UNTIL Expression SEMICOLON",
            },
        )
        
        repeat_node_id = self.get_next_node_id()
        self.node_stack.append(repeat_node_id)
        
        self.advance()
        
        self.trace_step(
            "Parsing repeat body",
            {"action": "parse_repeat_body"},
        )
        
        body = self.parse_block([TokenType.UNTIL])
        
        if not self.current_token or self.current_token.type != TokenType.UNTIL:
            raise ParseError("Expected 'until' after repeat body", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.trace_step(
            "Parsing until condition",
            {"action": "parse_until_condition"},
        )
        self.advance()
        
        condition = self.parse_expression()
        
        if not self.current_token or self.current_token.type != TokenType.SEMICOLON:
            raise ParseError("Expected ';' after until condition", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.advance()
        
        self.node_stack.pop()
        
        repeat_node = RepeatUntilNode(body, condition)
        self.trace_ast_node_creation(
            "Created repeat-until node",
            repeat_node,
            repeat_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return repeat_node

    def parse_read_statement(self) -> ReadNode:
        self.trace_step(
            "Starting read statement parsing",
            {
                "action": "start_read",
                "grammar_rule": "ReadStmt → READ IDENTIFIER SEMICOLON",
            },
        )
        
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            raise ParseError("Expected identifier after 'read'", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        identifier = self.current_token.literal
        
        self.trace_step(
            f"Reading into variable '{identifier}'",
            {"action": "parse_read_identifier", "identifier": identifier},
        )
        
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.SEMICOLON:
            raise ParseError("Expected ';' after read statement", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.advance()
        
        read_node = ReadNode(identifier)
        read_node_id = self.get_next_node_id()
        
        self.trace_ast_node_creation(
            f"Created read node for '{identifier}'",
            read_node,
            read_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return read_node

    def parse_write_statement(self) -> WriteNode:
        self.trace_step(
            "Starting write statement parsing",
            {
                "action": "start_write",
                "grammar_rule": "WriteStmt → WRITE Expression SEMICOLON",
            },
        )
        
        write_node_id = self.get_next_node_id()
        self.node_stack.append(write_node_id)
        
        self.advance()
        
        self.trace_step(
            "Parsing write expression",
            {"action": "parse_write_expression"},
        )
        
        expression = self.parse_expression()
        
        if not self.current_token or self.current_token.type != TokenType.SEMICOLON:
            raise ParseError("Expected ';' after write statement", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        self.advance()
        
        self.node_stack.pop()
        
        write_node = WriteNode(expression)
        self.trace_ast_node_creation(
            "Created write node",
            write_node,
            write_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return write_node

    def parse_expression(self, precedence: int = LOWEST) -> ASTNode:
        """
        Pratt parser for expressions with precedence climbing
        Expression → Prefix (Infix Prefix)*
        """
        self.trace_step(
            f"Starting expression parsing with precedence {precedence}",
            {
                "action": "start_expression",
                "precedence": precedence,
                "grammar_rule": "Expression → Prefix (Infix Prefix)*",
            },
        )

        left = self.parse_prefix()

        while self.current_token and self.current_precedence() > precedence:
            if self.current_token.type not in INFIX_OPERATORS:
                return left
            
            self.trace_step(
                f"Found infix operator with precedence {self.current_precedence()}",
                {
                    "operator": self.current_token.literal,
                    "operator_precedence": self.current_precedence(),
                    "current_precedence": precedence,
                    "action": "detect_infix",
                },
            )
            
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
                0,
                0,
            )

        self.trace_step(
            f"Parsing prefix: {token.type.name} '{token.literal}'",
            {
                "token_type": token.type.name,
                "literal": token.literal,
                "action": "start_prefix",
                "grammar_rule": "Prefix → NUMBER | FLOAT | IDENTIFIER | LPAREN Expression RPAREN",
            },
        )

        if token.type == TokenType.NUMBER:
            self.advance()
            node = NumberNode(int(token.literal))
            node_id = self.get_next_node_id()

            self.trace_ast_node_creation(
                f"Created number node: {token.literal}",
                node,
                node_id,
                self.node_stack[-1] if self.node_stack else None,
            )
            return node

        elif token.type == TokenType.FLOAT:
            self.advance()
            node = FloatNode(float(token.literal))
            node_id = self.get_next_node_id()

            self.trace_ast_node_creation(
                f"Created float node: {token.literal}",
                node,
                node_id,
                self.node_stack[-1] if self.node_stack else None,
            )
            return node

        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            node = IdentifierNode(token.literal)
            node_id = self.get_next_node_id()

            self.trace_ast_node_creation(
                f"Created identifier node: {token.literal}",
                node,
                node_id,
                self.node_stack[-1] if self.node_stack else None,
            )
            return node

        elif token.type == TokenType.LPAREN:
            self.trace_step(
                "Found parenthesized expression", {"action": "start_parentheses"}
            )

            self.advance()
            expr = self.parse_expression()

            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                current_type = self.current_token.type if self.current_token else "EOF"
                line = self.current_token.line if self.current_token else 1
                column = self.current_token.column if self.current_token else 1
                raise ParseError(f"Expected ')', got {current_type}", self.position, line, column)

            self.advance()

            self.trace_step(
                "Completed parenthesized expression", {"action": "complete_parentheses"}
            )

            return expr

        else:
            raise ParseError(
                f"Unexpected token in expression: {token.type} '{token.literal}'",
                self.position,
                token.line,
                token.column,
            )

    def parse_infix_expression(self, left: ASTNode) -> ASTNode:
        """
        Infix → left OPERATOR right
        Parses binary operations given left operand
        """
        if self.current_token is None:
            raise ParseError("Unexpected end of input in infix expression", self.position, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 1)
        
        operator = self.current_token.literal
        precedence = self.current_precedence()
        
        self.trace_step(
            f"Parsing infix operation: '{operator}'",
            {
                "operator": operator,
                "precedence": precedence,
                "left_type": type(left).__name__,
                "action": "parse_infix",
            },
        )
        
        self.advance()
        
        binary_node_id = self.get_next_node_id()
        self.node_stack.append(binary_node_id)
        
        right = self.parse_expression(precedence)
        
        self.node_stack.pop()
        
        node = BinaryOpNode(operator, left, right)
        
        self.trace_ast_node_creation(
            f"Created binary operation node: ... {operator} ...",
            node,
            binary_node_id,
            self.node_stack[-1] if self.node_stack else None,
        )
        
        return node


class TracingSemanticAnalyzer(SemanticAnalyzer):
    """Extended semantic analyzer that records step-by-step execution"""

    def __init__(self, step_id_start: int = 0):
        super().__init__()
        self.steps = []
        self.step_id = step_id_start
        self.node_id_counter = 0

    def trace_step(self, description: str, state: dict):
        """Record a step in the semantic analysis process"""
        self.steps.append(
            {
                "phase": "semantic-analysis",
                "step_id": self.step_id,
                "position": None,
                "description": description,
                "state": state,
            }
        )
        self.step_id += 1

    def get_next_node_id(self) -> str:
        """Generate a unique node ID for tracking"""
        self.node_id_counter += 1
        return f"sem_node_{self.node_id_counter}"

    def analyze(self, ast: ProgramNode) -> ProgramNode:
        """Analyze the AST with tracing"""
        self.trace_step(
            "Starting semantic analysis",
            {
                "action": "start_analysis",
                "statement_count": len(ast.statements),
            },
        )

        new_statements = []

        for i, statement in enumerate(ast.statements):
            self.trace_step(
                f"Analyzing statement {i + 1} of {len(ast.statements)}",
                {
                    "action": "analyze_statement",
                    "statement_index": i,
                    "statement_type": type(statement).__name__,
                },
            )
            analyzed_stmt = self.analyze_statement(statement)
            new_statements.append(analyzed_stmt)

        self.trace_step(
            "Completed semantic analysis",
            {
                "action": "complete_analysis",
                "symbol_table": dict(self.symbol_table),
            },
        )

        return ProgramNode(new_statements)

    def analyze_assignment(self, node: AssignmentNode) -> AssignmentNode:
        """Analyze assignment with tracing"""
        self.trace_step(
            f"Analyzing assignment to '{node.identifier}'",
            {
                "action": "start_assignment_analysis",
                "identifier": node.identifier,
            },
        )

        analyzed_value = self.analyze_expression(node.value)
        value_type = self.get_expression_type(analyzed_value)

        self.symbol_table[node.identifier] = value_type

        self.trace_step(
            f"Variable '{node.identifier}' assigned type: {value_type}",
            {
                "action": "update_symbol_table",
                "identifier": node.identifier,
                "type": value_type,
                "symbol_table": dict(self.symbol_table),
            },
        )

        return AssignmentNode(node.identifier, analyzed_value)

    def analyze_expression(self, node: ASTNode) -> ASTNode:
        """Analyze expression with tracing"""
        expr_type = self.get_expression_type(node)

        self.trace_step(
            f"Analyzing {type(node).__name__} expression (type: {expr_type})",
            {
                "action": "analyze_expression",
                "node_type": type(node).__name__,
                "expression_type": expr_type,
            },
        )

        if isinstance(node, BinaryOpNode):
            return self.analyze_binary_op(node)
        elif isinstance(node, (NumberNode, FloatNode, IdentifierNode)):
            return node
        elif isinstance(node, AssignmentNode):
            return self.analyze_assignment(node)
        else:
            return node

    def analyze_binary_op(self, node: BinaryOpNode) -> BinaryOpNode:
        """Analyze binary operation with tracing"""
        self.trace_step(
            f"Analyzing binary operation: '{node.operator}'",
            {
                "action": "start_binary_op_analysis",
                "operator": node.operator,
                "left_type": type(node.left).__name__,
                "right_type": type(node.right).__name__,
            },
        )

        left = self.analyze_expression(node.left)
        right = self.analyze_expression(node.right)

        left_type = self.get_expression_type(left)
        right_type = self.get_expression_type(right)

        self.trace_step(
            f"Operand types: left={left_type}, right={right_type}",
            {
                "action": "check_operand_types",
                "left_type": left_type,
                "right_type": right_type,
                "operator": node.operator,
            },
        )

        if left_type == "float" and right_type == "int":
            self.trace_step(
                "Type coercion needed: converting right operand (int) to float",
                {
                    "action": "coercion_needed",
                    "coercion_side": "right",
                    "from_type": "int",
                    "to_type": "float",
                },
            )

            node_id = self.get_next_node_id()
            right = Int2FloatNode(right)

            self.trace_step(
                "Created Int2Float wrapper for right operand",
                {
                    "action": "create_coercion_node",
                    "node_id": node_id,
                    "side": "right",
                    "wrapped_type": type(right.child).__name__,
                },
            )

        elif left_type == "int" and right_type == "float":
            self.trace_step(
                "Type coercion needed: converting left operand (int) to float",
                {
                    "action": "coercion_needed",
                    "coercion_side": "left",
                    "from_type": "int",
                    "to_type": "float",
                },
            )

            node_id = self.get_next_node_id()
            left = Int2FloatNode(left)

            self.trace_step(
                "Created Int2Float wrapper for left operand",
                {
                    "action": "create_coercion_node",
                    "node_id": node_id,
                    "side": "left",
                    "wrapped_type": type(left.child).__name__,
                },
            )
        else:
            self.trace_step(
                "No type coercion needed",
                {
                    "action": "no_coercion",
                    "left_type": left_type,
                    "right_type": right_type,
                },
            )

        return BinaryOpNode(node.operator, left, right)

    def analyze_block(self, node: BlockNode) -> BlockNode:
        """Analyze a block of statements with tracing"""
        self.trace_step(
            f"Analyzing block with {len(node.statements)} statements",
            {
                "action": "start_block_analysis",
                "statement_count": len(node.statements),
            },
        )

        analyzed_statements = []
        for i, stmt in enumerate(node.statements):
            self.trace_step(
                f"Analyzing block statement {i + 1} of {len(node.statements)}",
                {
                    "action": "analyze_block_statement",
                    "statement_index": i,
                    "statement_type": type(stmt).__name__,
                },
            )
            analyzed_statements.append(self.analyze_statement(stmt))

        self.trace_step(
            "Completed block analysis",
            {"action": "complete_block_analysis"},
        )

        return BlockNode(analyzed_statements)

    def analyze_if(self, node: IfNode) -> IfNode:
        """Analyze if statement with tracing"""
        self.trace_step(
            "Analyzing if statement",
            {
                "action": "start_if_analysis",
                "has_else": node.else_branch is not None,
            },
        )

        self.trace_step(
            "Analyzing if condition",
            {"action": "analyze_if_condition"},
        )
        analyzed_condition = self.analyze_expression(node.condition)

        self.trace_step(
            "Analyzing then branch",
            {"action": "analyze_then_branch"},
        )
        analyzed_then = self.analyze_statement(node.then_branch)

        analyzed_else = None
        if node.else_branch:
            self.trace_step(
                "Analyzing else branch",
                {"action": "analyze_else_branch"},
            )
            analyzed_else = self.analyze_statement(node.else_branch)

        self.trace_step(
            "Completed if statement analysis",
            {"action": "complete_if_analysis"},
        )

        return IfNode(analyzed_condition, analyzed_then, analyzed_else)

    def analyze_repeat(self, node: RepeatUntilNode) -> RepeatUntilNode:
        """Analyze repeat-until loop with tracing"""
        self.trace_step(
            "Analyzing repeat-until loop",
            {"action": "start_repeat_analysis"},
        )

        self.trace_step(
            "Analyzing loop body",
            {"action": "analyze_repeat_body"},
        )
        analyzed_body = self.analyze_statement(node.body)

        self.trace_step(
            "Analyzing until condition",
            {"action": "analyze_until_condition"},
        )
        analyzed_condition = self.analyze_expression(node.condition)

        self.trace_step(
            "Completed repeat-until analysis",
            {"action": "complete_repeat_analysis"},
        )

        return RepeatUntilNode(analyzed_body, analyzed_condition)

    def analyze_read(self, node: ReadNode) -> ReadNode:
        """Analyze read statement with tracing"""
        self.trace_step(
            f"Analyzing read statement for variable '{node.identifier}'",
            {
                "action": "start_read_analysis",
                "identifier": node.identifier,
            },
        )

        self.symbol_table[node.identifier] = "unknown"

        self.trace_step(
            f"Variable '{node.identifier}' marked as initialized (type: unknown)",
            {
                "action": "update_symbol_table",
                "identifier": node.identifier,
                "type": "unknown",
                "symbol_table": dict(self.symbol_table),
            },
        )

        return node

    def analyze_write(self, node: WriteNode) -> WriteNode:
        """Analyze write statement with tracing"""
        self.trace_step(
            "Analyzing write statement",
            {"action": "start_write_analysis"},
        )

        analyzed_expression = self.analyze_expression(node.expression)

        expr_type = self.get_expression_type(analyzed_expression)
        self.trace_step(
            f"Write expression has type: {expr_type}",
            {
                "action": "complete_write_analysis",
                "expression_type": expr_type,
            },
        )

        return WriteNode(analyzed_expression)


def trace_compilation(source_code: str) -> dict:
    """
    Trace the complete compilation process step by step
    """
    # Phase 1: Lexing (always attempt)
    lexer = TracingLexer(source_code)
    tokens = []
    
    try:
        # Collect all tokens to get lexing steps
        while True:
            token = lexer.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
    except Exception as e:
        # Lexing error - return what we have so far
        error_step = {
            "phase": "lexing",
            "step_id": lexer.step_id,
            "position": lexer.position,
            "description": f"Lexing error: {str(e)}",
            "state": {
                "action": "error",
                "error_type": type(e).__name__,
                "message": str(e),
            },
        }
        lexer.steps.append(error_step)
        
        return {
            "steps": lexer.steps,
            "tokens": [{"type": t.type.name, "literal": t.literal} for t in tokens],
            "ast": None,
            "analyzed_ast": None,
            "success": False,
            "error": str(e),
            "error_phase": "lexing",
        }

    # Phase 2: Parsing
    parse_lexer = TracingLexer(source_code)
    parser = TracingParser(parse_lexer)
    ast = None
    partial_ast = None
    
    try:
        ast = parser.parse_program()
    except ParseError as e:
        # Create an error node for the failed parse
        
        # Determine what was found at the error position
        if parser.current_token:
            if parser.current_token.literal:
                found = parser.current_token.literal
            else:
                found = parser.current_token.type.name
        else:
            found = "EOF"
        
        # Get context: show the line where the error occurred
        lines = source_code.split('\n')
        line_idx = e.line - 1
        if 0 <= line_idx < len(lines):
            context = lines[line_idx]
        else:
            # Fallback: use character position if line is out of bounds
            if parser.current_token:
                char_pos = parser.current_token.start_pos
            else:
                char_pos = len(source_code)
            context = source_code[max(0, char_pos - 30):min(len(source_code), char_pos + 30)]
        
        error_node = ErrorNode(
            message=e.message,
            expected=["expression", "statement", "identifier"],  # Generic for now
            found=found,
            line=e.line,
            col=e.column,
            context=context,
        )
        
        # Create a program node with successfully parsed statements + error node
        partial_ast = ProgramNode(parser.parsed_statements + [error_node])
        
        # Add Program node creation step
        parser.step_id += 1
        program_node_id = f"program_node_{parser.step_id}"
        program_step = {
            "phase": "parsing",
            "step_id": parser.step_id,
            "position": e.position,
            "description": f"Created partial program node with {len(parser.parsed_statements)} statements + error",
            "state": {
                "action": "create_ast_node",
                "node_type": "ProgramNode",
                "node_id": program_node_id,
                "parent_id": None,
                "statement_count": len(parser.parsed_statements) + 1,
                "ast_node": partial_ast.to_dict(),
            },
        }
        parser.steps.append(program_step)
        
        # Add error step to parser steps
        parser.step_id += 1
        error_step = {
            "phase": "parsing",
            "step_id": parser.step_id,
            "position": e.position,
            "description": f"Parse error: {e.message}",
            "state": {
                "action": "create_ast_node",
                "node_type": "ErrorNode",
                "node_id": f"error_node_{parser.step_id}",
                "parent_id": program_node_id,
                "error_type": "ParseError",
                "message": e.message,
                "ast_node": error_node.to_dict(),
            },
        }
        parser.steps.append(error_step)
        
        # Return partial results
        all_steps = lexer.steps + parser.steps
        return {
            "steps": all_steps,
            "tokens": [{"type": t.type.name, "literal": t.literal} for t in tokens],
            "ast": partial_ast.to_dict(),
            "analyzed_ast": None,
            "success": False,
            "error": e.message,
            "error_phase": "parsing",
            "error_line": e.line,
            "error_column": e.column,
            "error_position": e.position,
        }
    except Exception as e:
        # Other parsing error
        print(traceback.format_exc())
        error_step = {
            "phase": "parsing",
            "step_id": parser.step_id,
            "position": parser.position,
            "description": f"Parsing error: {str(e)}",
            "state": {
                "action": "error",
                "error_type": type(e).__name__,
                "message": str(e),
            },
        }
        parser.steps.append(error_step)
        
        all_steps = lexer.steps + parser.steps
        return {
            "steps": all_steps,
            "tokens": [{"type": t.type.name, "literal": t.literal} for t in tokens],
            "ast": None,
            "analyzed_ast": None,
            "success": False,
            "error": str(e),
            "error_phase": "parsing",
        }

    # Phase 3: Semantic Analysis
    semantic_analyzer = TracingSemanticAnalyzer(
        step_id_start=len(lexer.steps) + len(parser.steps)
    )
    
    try:
        analyzed_ast = semantic_analyzer.analyze(ast)
        
        # Combine all steps
        all_steps = lexer.steps + parser.steps + semantic_analyzer.steps

        return {
            "steps": all_steps,
            "tokens": [{"type": t.type.name, "literal": t.literal} for t in tokens],
            "ast": ast.to_dict(),
            "analyzed_ast": analyzed_ast.to_dict(),
            "success": True,
        }
    except Exception as e:
        # Semantic analysis error
        print(traceback.format_exc())
        error_step = {
            "phase": "semantic_analysis",
            "step_id": semantic_analyzer.step_id,
            "position": 0,
            "description": f"Semantic analysis error: {str(e)}",
            "state": {
                "action": "error",
                "error_type": type(e).__name__,
                "message": str(e),
            },
        }
        semantic_analyzer.steps.append(error_step)
        
        all_steps = lexer.steps + parser.steps + semantic_analyzer.steps
        return {
            "steps": all_steps,
            "tokens": [{"type": t.type.name, "literal": t.literal} for t in tokens],
            "ast": ast.to_dict(),
            "analyzed_ast": None,
            "success": False,
            "error": str(e),
            "error_phase": "semantic_analysis",
        }
