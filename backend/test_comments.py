from toyc.lexer import Lexer
from toyc.token import TokenType


def test_single_line_comment():
    input_text = "%% This is a comment\nx := 5;"
    lexer = Lexer(input_text)
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    assert token.literal == "x"
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "5"
    
    token = lexer.next_token()
    assert token.type == TokenType.SEMICOLON
    
    token = lexer.next_token()
    assert token.type == TokenType.EOF


def test_multi_line_comment():
    input_text = "x := 5; { this is a\nmulti-line comment } y := 10;"
    lexer = Lexer(input_text)
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    assert token.literal == "x"
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "5"
    
    token = lexer.next_token()
    assert token.type == TokenType.SEMICOLON
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    assert token.literal == "y"
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "10"


def test_percent_operator_vs_comment():
    input_text = "x := 10 % 3;"
    lexer = Lexer(input_text)
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "10"
    
    token = lexer.next_token()
    assert token.type == TokenType.PERCENT
    assert token.literal == "%"
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "3"


def test_mixed_comments():
    input_text = "%% Single line\nx := 5; { multi } y := 10;"
    lexer = Lexer(input_text)
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    assert token.literal == "x"
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    assert token.literal == "5"
    
    token = lexer.next_token()
    assert token.type == TokenType.SEMICOLON
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    assert token.literal == "y"


def test_comment_at_end():
    input_text = "x := 5; %% comment at end"
    lexer = Lexer(input_text)
    
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER
    
    token = lexer.next_token()
    assert token.type == TokenType.ASSIGN
    
    token = lexer.next_token()
    assert token.type == TokenType.NUMBER
    
    token = lexer.next_token()
    assert token.type == TokenType.SEMICOLON
    
    token = lexer.next_token()
    assert token.type == TokenType.EOF
