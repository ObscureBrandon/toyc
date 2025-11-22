from .token import Token, TokenType, lookup_identifier


class Lexer:
    def __init__(self, input: str):
        self.input: str = input
        self.position: int = 0
        self.read_position: int = 0
        self.ch: str = ""
        self.line: int = 1
        self.column: int = 0
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = "\0"
        else:
            self.ch = self.input[self.read_position]

        self.position = self.read_position
        self.read_position += 1

        if self.ch == "\n":
            self.line += 1
            self.column = 0
        else:
            self.column += 1

    def _new_token(self, type: TokenType, literal: str) -> Token:
        token = Token(
            type,
            literal,
            self.line,
            self.column - len(literal) + 1,
            self.position - len(literal) + 1,
            self.position,
        )
        return token

    def is_whitespace(self, ch: str) -> bool:
        return ch in " \t\n\r"

    def skip_whitespace(self):
        while self.is_whitespace(self.ch):
            self.read_char()

    def skip_single_line_comment(self):
        while self.ch != "\n" and self.ch != "\0":
            self.read_char()

    def skip_multi_line_comment(self):
        while self.ch != "}" and self.ch != "\0":
            self.read_char()
        if self.ch == "}":
            self.read_char()

    def is_letter(self, ch: str) -> bool:
        return ("a" <= ch and ch <= "z") or ("A" <= ch and ch <= "Z") or ch == "_"

    def is_digit(self, ch: str) -> bool:
        return "0" <= ch and ch <= "9"

    def peek_char(self) -> str:
        if self.read_position >= len(self.input):
            return "\0"
        else:
            return self.input[self.read_position]

    def read_identifier(self) -> tuple[str, int, int]:
        start_position = self.position
        start_line = self.line
        start_column = self.column
        while self.ch.isalpha():
            self.read_char()
        return self.input[start_position : self.position], start_line, start_column

    def read_number(self) -> tuple[str, int, int]:
        start_position = self.position
        start_line = self.line
        start_column = self.column
        while self.ch.isdigit():
            self.read_char()
        return self.input[start_position : self.position], start_line, start_column

    def next_token(self) -> Token:
        self.skip_whitespace()

        token: Token | None = None
        match self.ch:
            case "+":
                token = self._new_token(TokenType.PLUS, self.ch)
            case "-":
                token = self._new_token(TokenType.MINUS, self.ch)
            case "*":
                token = self._new_token(TokenType.ASTERISK, self.ch)
            case "/":
                token = self._new_token(TokenType.SLASH, self.ch)
            case "(":
                token = self._new_token(TokenType.LPAREN, self.ch)
            case ")":
                token = self._new_token(TokenType.RPAREN, self.ch)
            case ";":
                token = self._new_token(TokenType.SEMICOLON, self.ch)
            case "%":
                if self.peek_char() == "%":
                    self.read_char()
                    self.read_char()
                    self.skip_single_line_comment()
                    return self.next_token()
                else:
                    token = self._new_token(TokenType.PERCENT, self.ch)
            case "{":
                self.read_char()
                self.skip_multi_line_comment()
                return self.next_token()
            case ":":
                if self.peek_char() == "=":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.ASSIGN, literal)
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)
            case "<":
                if self.peek_char() == "=":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.LT_EQ, literal)
                else:
                    token = self._new_token(TokenType.LT, self.ch)
            case ">":
                if self.peek_char() == "=":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.GT_EQ, literal)
                else:
                    token = self._new_token(TokenType.GT, self.ch)
            case "=":
                if self.peek_char() == "=":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.EQ, literal)
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)
            case "!":
                if self.peek_char() == "=":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.NEQ, literal)
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)
            case "&":
                if self.peek_char() == "&":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.AND, literal)
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)
            case "|":
                if self.peek_char() == "|":
                    ch = self.ch
                    self.read_char()
                    literal = ch + self.ch
                    token = self._new_token(TokenType.OR, literal)
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)
            case "\0":
                token = self._new_token(TokenType.EOF, "")
            case _:
                if self.is_letter(self.ch):
                    literal, start_line, start_column = self.read_identifier()
                    token_type = lookup_identifier(literal)
                    start_pos = self.position - len(literal)
                    end_pos = self.position - 1
                    token = Token(
                        token_type,
                        literal,
                        start_line,
                        start_column,
                        start_pos,
                        end_pos,
                    )
                    return token
                elif self.is_digit(self.ch):
                    literal, start_line, start_column = self.read_number()
                    start_pos = self.position - len(literal)
                    if self.ch == ".":
                        self.read_char()
                        fractional, _, _ = self.read_number()
                        literal += "." + fractional
                        if self.is_letter(self.ch):
                            while self.is_letter(self.ch) or self.is_digit(self.ch):
                                literal += self.ch
                                self.read_char()
                            end_pos = self.position - 1
                            token = Token(
                                TokenType.ILLEGAL,
                                literal,
                                start_line,
                                start_column,
                                start_pos,
                                end_pos,
                            )
                        else:
                            end_pos = self.position - 1
                            token = Token(
                                TokenType.FLOAT,
                                literal,
                                start_line,
                                start_column,
                                start_pos,
                                end_pos,
                            )
                    else:
                        if self.is_letter(self.ch):
                            while self.is_letter(self.ch) or self.is_digit(self.ch):
                                literal += self.ch
                                self.read_char()
                            end_pos = self.position - 1
                            token = Token(
                                TokenType.ILLEGAL,
                                literal,
                                start_line,
                                start_column,
                                start_pos,
                                end_pos,
                            )
                        else:
                            end_pos = self.position - 1
                            token = Token(
                                TokenType.NUMBER,
                                literal,
                                start_line,
                                start_column,
                                start_pos,
                                end_pos,
                            )
                    return token
                else:
                    token = self._new_token(TokenType.ILLEGAL, self.ch)

        self.read_char()
        return token
