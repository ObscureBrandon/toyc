"""Test normalized lexer representation feature."""
from api import lex_code
from models import LexerRequest
import asyncio


async def test_simple_assignment():
    """Test: x := x + y + z;"""
    request = LexerRequest(source_code="x := x + y + z;")
    response = await lex_code(request)
    
    assert response.normalized_code == "id1 := id1 + id2 + id3 ;"
    assert response.identifier_mapping == {"x": "id1", "y": "id2", "z": "id3"}
    print("✓ Simple assignment test passed")


async def test_reused_identifiers():
    """Test that the same identifier gets the same id number."""
    request = LexerRequest(source_code="a := a + b + a;")
    response = await lex_code(request)
    
    assert response.normalized_code == "id1 := id1 + id2 + id1 ;"
    assert response.identifier_mapping == {"a": "id1", "b": "id2"}
    print("✓ Reused identifiers test passed")


async def test_keywords_preserved():
    """Test that keywords are not normalized."""
    request = LexerRequest(source_code="if (x > 0) then write x; end")
    response = await lex_code(request)
    
    # Keywords should be preserved, only 'x' should be normalized to id1
    assert "if" in response.normalized_code
    assert "then" in response.normalized_code
    assert "write" in response.normalized_code
    assert "end" in response.normalized_code
    assert "id1" in response.normalized_code
    assert response.normalized_code == "if ( id1 > 0 ) then write id1 ; end"
    assert response.identifier_mapping == {"x": "id1"}
    print("✓ Keywords preserved test passed")


async def test_numbers_preserved():
    """Test that numbers are not normalized."""
    request = LexerRequest(source_code="x := 42 + 3.14;")
    response = await lex_code(request)
    
    assert "42" in response.normalized_code
    assert "3.14" in response.normalized_code
    assert "id1" in response.normalized_code
    assert response.normalized_code == "id1 := 42 + 3.14 ;"
    assert response.identifier_mapping == {"x": "id1"}
    print("✓ Numbers preserved test passed")


async def test_complex_program():
    """Test with a more complex ToyC program."""
    request = LexerRequest(
        source_code="""x := 5;
if (x >= 3) then
    read y;
else
    write x % 2;
end"""
    )
    response = await lex_code(request)
    
    # x should be id1, y should be id2
    expected = "id1 := 5 ; if ( id1 >= 3 ) then read id2 ; else write id1 % 2 ; end"
    assert response.normalized_code == expected
    assert response.identifier_mapping == {"x": "id1", "y": "id2"}
    print("✓ Complex program test passed")


async def test_multiple_identifiers():
    """Test with many different identifiers."""
    request = LexerRequest(source_code="a := b + c + d + e;")
    response = await lex_code(request)
    
    assert response.normalized_code == "id1 := id2 + id3 + id4 + id5 ;"
    assert response.identifier_mapping == {
        "a": "id1",
        "b": "id2",
        "c": "id3",
        "d": "id4",
        "e": "id5",
    }
    print("✓ Multiple identifiers test passed")


async def main():
    print("Running normalized lexer representation tests...\n")
    await test_simple_assignment()
    await test_reused_identifiers()
    await test_keywords_preserved()
    await test_numbers_preserved()
    await test_complex_program()
    await test_multiple_identifiers()
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
