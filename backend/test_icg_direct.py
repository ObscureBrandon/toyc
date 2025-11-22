from toyc.parser import parse_code
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator

def test_if_statement():
    code = """
    x := 5;
    if (x >= 3) then
      read y;
    else
      write x % 2;
    end
    """
    
    print("Testing ICG with if-else statement")
    print(code)
    print()
    
    # Parse
    ast = parse_code(code)
    print(f"✓ Parsed")
    
    # Analyze
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    print(f"✓ Analyzed")
    
    # Generate ICG
    icg_gen = ICGGenerator()
    instructions = icg_gen.generate(analyzed_ast)
    
    print(f"✓ Generated ICG: {len(instructions)} instructions")
    print()
    print("Three-Address Code:")
    for i, inst in enumerate(instructions, 1):
        print(f"  {i}. {inst}")
    print()
    print(f"Temps used: {icg_gen.temp_counter}")
    print(f"Labels used: {icg_gen.label_counter}")

if __name__ == "__main__":
    test_if_statement()
