import traceback

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
    Int2FloatNode,
    ParseError,
)
from .semantic_analyzer import SemanticAnalyzer, NodeType


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

    def read_char(self):
        # Just read the character without verbose tracing
        super().read_char()
    
    def read_identifier(self) -> str:
        """Read identifier with incremental tracing"""
        start_position = self.position
        current_lexeme = ""
        
        while self.ch.isalpha():
            current_lexeme += self.ch
            self.trace_step(
                f"Building IDENTIFIER: '{current_lexeme}'",
                {
                    "current_char": self.ch,
                    "current_lexeme": current_lexeme,
                    "action": "build_token",
                    "token_type": "IDENTIFIER"
                }
            )
            self.read_char()
        
        return self.input[start_position : self.position]
    
    def read_number(self) -> str:
        """Read number with incremental tracing"""
        start_position = self.position
        current_lexeme = ""
        
        while self.ch.isdigit():
            current_lexeme += self.ch
            self.trace_step(
                f"Building NUMBER: '{current_lexeme}'",
                {
                    "current_char": self.ch,
                    "current_lexeme": current_lexeme,
                    "action": "build_token",
                    "token_type": "NUMBER"
                }
            )
            self.read_char()
        
        return self.input[start_position : self.position]

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
                {"current_char": self.ch, "action": "identify_token", "token_type": "PLUS"},
            )
            token = self._new_token(TokenType.PLUS, self.ch)
        elif self.ch == "-":
            self.trace_step(
                f"Creating MINUS token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "MINUS"},
            )
            token = self._new_token(TokenType.MINUS, self.ch)
        elif self.ch == "*":
            self.trace_step(
                f"Creating ASTERISK token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "ASTERISK"},
            )
            token = self._new_token(TokenType.ASTERISK, self.ch)
        elif self.ch == "/":
            self.trace_step(
                f"Creating SLASH token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "SLASH"},
            )
            token = self._new_token(TokenType.SLASH, self.ch)
        elif self.ch == "(":
            self.trace_step(
                f"Creating LPAREN token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "LPAREN"},
            )
            token = self._new_token(TokenType.LPAREN, self.ch)
        elif self.ch == ")":
            self.trace_step(
                f"Creating RPAREN token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "RPAREN"},
            )
            token = self._new_token(TokenType.RPAREN, self.ch)
        elif self.ch == "=":
            self.trace_step(
                f"Creating EQUAL token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "EQUAL"},
            )
            token = self._new_token(TokenType.EQUAL, self.ch)
        elif self.ch == "\0":
            self.trace_step(
                f"Creating EOF token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "EOF"},
            )
            token = self._new_token(TokenType.EOF, "")
        elif self.is_letter(self.ch):
            self.trace_step(
                f"Creating IDENTIFIER token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "IDENTIFIER"},
            )
            literal = self.read_identifier()
            token = self._new_token(TokenType.IDENTIFIER, literal)
            # Don't advance here since read_identifier already did
            self.trace_step(
                f"Created IDENTIFIER token: '{literal}'",
                {
                    "token_type": "IDENTIFIER",
                    "literal": literal,
                    "action": "token_created",
                },
            )
            return token
        elif self.is_digit(self.ch):
            self.trace_step(
                f"Creating NUMBER token at position {start_position}",
                {"current_char": self.ch, "action": "identify_token", "token_type": "NUMBER"},
            )
            literal = self.read_number()
            
            # Check for decimal point to create FLOAT token
            if self.ch == ".":
                self.trace_step(
                    f"Found decimal point, converting to FLOAT token",
                    {"current_char": self.ch, "action": "detect_decimal", "current_lexeme": literal},
                )
                literal += "."
                self.read_char()  # consume the '.'
                
                # Read fractional part
                fractional_start = len(literal)
                fractional = self.read_number()
                literal += fractional
                
                token = self._new_token(TokenType.FLOAT, literal)
                token_type = "FLOAT"
                
                self.trace_step(
                    f"Built complete FLOAT: '{literal}'",
                    {"current_lexeme": literal, "action": "complete_float", "token_type": "FLOAT"},
                )
            else:
                token = self._new_token(TokenType.NUMBER, literal)
                token_type = "NUMBER"
            
            # Don't advance here since read_number already did
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
                {"current_char": self.ch, "action": "identify_token", "token_type": "ILLEGAL"},
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

    def trace_ast_node_creation(self, description: str, node: ASTNode, node_id: str, parent_id: str | None = None):
        """Record AST node creation with full node data and relationships"""
        self.trace_step(
            description,
            {
                "action": "create_ast_node",
                "node_id": node_id,
                "parent_id": parent_id,
                "ast_node": node.to_dict(),
                "node_type": type(node).__name__,
            }
        )

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
                "current_token": self.current_token.type.name if self.current_token else None,
                "current_literal": self.current_token.literal if self.current_token else None,
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

                self.trace_step(
                    f"Completed statement of type {type(stmt).__name__}",
                    {
                        "statement_type": type(stmt).__name__,
                        "action": "complete_statement",
                    },
                )

            except ParseError as e:
                self.trace_step(
                    f"Parse error: {e.message}",
                    {"error": e.message, "action": "parse_error"},
                )
                self.advance()

        program = ProgramNode(statements)
        program_node_id = self.get_next_node_id()
        
        self.trace_ast_node_creation(
            f"Created program node with {len(statements)} statements",
            program,
            program_node_id,
            None
        )
        
        self.trace_step(
            f"Completed program with {len(statements)} statements",
            {"statement_count": len(statements), "action": "complete_program"},
        )

        return program

    def parse_statement(self) -> ASTNode:
        """Parse a statement (assignment or expression)"""
        # Check for assignment
        if (
            self.current_token and self.current_token.type == TokenType.IDENTIFIER
            and self.peek_token and self.peek_token.type == TokenType.EQUAL
        ):
            self.trace_step(
                f"Detected assignment: {self.current_token.literal} =",
                {
                    "identifier": self.current_token.literal,
                    "action": "detect_assignment",
                    "grammar_rule": "Assignment → IDENTIFIER '=' Expression",
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
            return self.parse_expression()

    def parse_assignment(self) -> AssignmentNode:
        """Parse assignment statement"""
        identifier_token = self.current_token
        
        if not identifier_token:
            raise ParseError("Expected identifier for assignment", self.position)

        self.trace_step(
            f"Parsing assignment to '{identifier_token.literal}'",
            {"identifier": identifier_token.literal, "action": "start_assignment"},
        )

        self.advance()  # consume identifier
        self.advance()  # consume '='

        # Push assignment node context for tracking children
        assignment_node_id = self.get_next_node_id()
        self.node_stack.append(assignment_node_id)

        value = self.parse_expression()

        # Pop the assignment context
        self.node_stack.pop()

        assignment = AssignmentNode(identifier_token.literal, value)

        self.trace_ast_node_creation(
            f"Created assignment node: {identifier_token.literal} = ...",
            assignment,
            assignment_node_id,
            self.node_stack[-1] if self.node_stack else None
        )

        return assignment

    def parse_expression(self) -> ASTNode:
        """Parse expression with addition/subtraction"""
        self.trace_step(
            "Starting expression parsing",
            {
                "action": "start_expression",
                "grammar_rule": "Expression → Term ((PLUS | MINUS) Term)*",
            },
        )

        left = self.parse_term()

        while (
            self.current_token 
            and self.current_token.type in [TokenType.PLUS, TokenType.MINUS]
        ):
            operator = self.current_token.literal

            self.trace_step(
                f"Found binary operator: '{operator}'",
                {
                    "operator": operator,
                    "action": "detect_binary_op",
                    "left_type": type(left).__name__,
                },
            )

            self.advance()
            
            # Push current node context for parent tracking
            binary_node_id = self.get_next_node_id()
            self.node_stack.append(binary_node_id)
            
            right = self.parse_term()
            
            # Pop the node context
            self.node_stack.pop()

            left = BinaryOpNode(operator, left, right)

            self.trace_ast_node_creation(
                f"Created binary operation node: ... {operator} ...",
                left,
                binary_node_id,
                self.node_stack[-1] if self.node_stack else None
            )

        return left

    def parse_term(self) -> ASTNode:
        """Parse term with multiplication/division"""
        self.trace_step(
            "Starting term parsing",
            {
                "action": "start_term",
                "grammar_rule": "Term → Factor ((ASTERISK | SLASH) Factor)*",
            },
        )

        left = self.parse_factor()

        while (
            self.current_token 
            and self.current_token.type in [TokenType.ASTERISK, TokenType.SLASH]
        ):
            operator = self.current_token.literal

            self.trace_step(
                f"Found term operator: '{operator}'",
                {
                    "operator": operator,
                    "action": "detect_term_op",
                    "left_type": type(left).__name__,
                },
            )

            self.advance()
            
            # Push current node context for parent tracking
            term_node_id = self.get_next_node_id()
            self.node_stack.append(term_node_id)
            
            right = self.parse_factor()
            
            # Pop the node context
            self.node_stack.pop()

            left = BinaryOpNode(operator, left, right)

            self.trace_ast_node_creation(
                f"Created term operation node: ... {operator} ...",
                left,
                term_node_id,
                self.node_stack[-1] if self.node_stack else None
            )

        return left

    def parse_factor(self) -> ASTNode:
        """Parse factor (number, float, identifier, or parenthesized expression)"""
        token = self.current_token
        
        if not token:
            raise ParseError("Unexpected end of input in factor", self.position)

        self.trace_step(
            f"Parsing factor: {token.type.name} '{token.literal}'",
            {
                "token_type": token.type.name,
                "literal": token.literal,
                "action": "start_factor",
                "grammar_rule": "Factor → NUMBER | FLOAT | IDENTIFIER | LPAREN Expression RPAREN",
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
                self.node_stack[-1] if self.node_stack else None
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
                self.node_stack[-1] if self.node_stack else None
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
                self.node_stack[-1] if self.node_stack else None
            )
            return node

        elif token.type == TokenType.LPAREN:
            self.trace_step(
                "Found parenthesized expression", {"action": "start_parentheses"}
            )

            self.advance()  # consume '('
            expr = self.parse_expression()

            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                current_type = self.current_token.type if self.current_token else "EOF"
                raise ParseError(
                    f"Expected ')', got {current_type}", self.position
                )

            self.advance()  # consume ')'

            self.trace_step(
                "Completed parenthesized expression", {"action": "complete_parentheses"}
            )

            return expr

        else:
            error_msg = f"Unexpected token in factor: {token.type.name} '{token.literal}'"
            self.trace_step(
                error_msg,
                {
                    "token_type": token.type.name,
                    "literal": token.literal,
                    "action": "parse_error",
                },
            )
            raise ParseError(error_msg, self.position)


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
                f"Type coercion needed: converting right operand (int) to float",
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
                f"Created Int2Float wrapper for right operand",
                {
                    "action": "create_coercion_node",
                    "node_id": node_id,
                    "side": "right",
                    "wrapped_type": type(right.child).__name__,
                },
            )
            
        elif left_type == "int" and right_type == "float":
            self.trace_step(
                f"Type coercion needed: converting left operand (int) to float",
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
                f"Created Int2Float wrapper for left operand",
                {
                    "action": "create_coercion_node",
                    "node_id": node_id,
                    "side": "left",
                    "wrapped_type": type(left.child).__name__,
                },
            )
        else:
            self.trace_step(
                f"No type coercion needed",
                {
                    "action": "no_coercion",
                    "left_type": left_type,
                    "right_type": right_type,
                },
            )
        
        return BinaryOpNode(node.operator, left, right)


def trace_compilation(source_code: str) -> dict:
    """
    Trace the complete compilation process step by step
    """
    try:
        # Phase 1: Lexing
        lexer = TracingLexer(source_code)

        # Collect all tokens to get lexing steps
        tokens = []
        while True:
            token = lexer.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break

        # Phase 2: Parsing
        # Create fresh lexer for parsing (since we consumed the first one)
        parse_lexer = TracingLexer(source_code)
        parser = TracingParser(parse_lexer)
        ast = parser.parse_program()

        # Phase 3: Semantic Analysis
        semantic_analyzer = TracingSemanticAnalyzer(step_id_start=len(lexer.steps) + len(parser.steps))
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
        print(traceback.format_exc())
        return {"steps": [], "success": False, "error": str(traceback.format_exc())}

