from toyc.lexer import Lexer
from toyc.parser import parse_code
from toyc.ast import ParseError
import pytest


def test_token_position_single_line():
    """Test that tokens have correct line and column info on single line"""
    input_code = "x := 5 + 3;"
    lexer = Lexer(input_code)
    
    token = lexer.next_token()
    assert token.literal == "x"
    assert token.line == 1
    assert token.column == 1
    
    token = lexer.next_token()
    assert token.literal == ":="
    assert token.line == 1
    assert token.column == 3
    
    token = lexer.next_token()
    assert token.literal == "5"
    assert token.line == 1
    assert token.column == 6


def test_token_position_multiline():
    """Test that tokens have correct line and column info across lines"""
    input_code = """x := 5;
y := 10;"""
    lexer = Lexer(input_code)
    
    token = lexer.next_token()
    assert token.literal == "x"
    assert token.line == 1
    assert token.column == 1
    
    lexer.next_token()  # :=
    lexer.next_token()  # 5
    lexer.next_token()  # ;
    
    token = lexer.next_token()
    assert token.literal == "y"
    assert token.line == 2
    assert token.column == 1


def test_parse_error_with_line_column():
    """Test that ParseError includes line and column information"""
    from toyc.lexer import Lexer
    from toyc.parser import Parser
    
    input_code = "if (x) then y := 5;"
    
    lexer = Lexer(input_code)
    parser = Parser(lexer)
    
    with pytest.raises(ParseError) as excinfo:
        parser.parse_if_statement()
    
    error = excinfo.value
    assert error.line > 0
    assert error.column > 0
    assert "line" in str(error).lower()


def test_parse_error_multiline():
    """Test ParseError on multiline code points to correct line"""
    from toyc.lexer import Lexer
    from toyc.parser import Parser
    
    input_code = """if (x) then
    y := 5;
    z := 10;"""
    
    lexer = Lexer(input_code)
    parser = Parser(lexer)
    
    with pytest.raises(ParseError) as excinfo:
        parser.parse_if_statement()
    
    error = excinfo.value
    assert error.line == 3
    assert "line" in str(error)
