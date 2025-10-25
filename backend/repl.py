#!/usr/bin/env python3

import sys
import argparse
import json
from toyc.lexer import Lexer
from toyc.parser import Parser
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.tracer import trace_compilation
from toyc.token import TokenType


def print_tokens(source_code: str):
    lexer = Lexer(source_code)
    tokens = []
    while True:
        token = lexer.next_token()
        tokens.append({"type": token.type.name, "literal": token.literal})
        if token.type == TokenType.EOF:
            break
    print(json.dumps(tokens, indent=2))


def print_ast(source_code: str):
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse_program()
    print(json.dumps(ast.to_dict(), indent=2))


def print_semantic_analysis(source_code: str):
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer()
    analyzed_ast = analyzer.analyze(ast)
    print(json.dumps(analyzed_ast.to_dict(), indent=2))


def print_trace(source_code: str):
    result = trace_compilation(source_code)
    print(json.dumps(result, indent=2))


def repl_mode(mode: str):
    print(f"ToyC REPL - {mode.upper()} mode")
    print("Type 'exit' or 'quit' to exit")
    print()
    
    while True:
        try:
            line = input("toyc> ").strip()
            if line.lower() in ["exit", "quit"]:
                break
            if not line:
                continue
            
            if mode == "lex":
                print_tokens(line)
            elif mode == "parse":
                print_ast(line)
            elif mode == "semantic":
                print_semantic_analysis(line)
            elif mode == "trace":
                print_trace(line)
            
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="ToyC - A toy compiler with lexer, parser, and semantic analyzer"
    )
    
    parser.add_argument(
        "--lex",
        action="store_true",
        help="Run lexer only and output tokens",
    )
    
    parser.add_argument(
        "--parse",
        action="store_true",
        help="Run lexer and parser, output AST",
    )
    
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Run full semantic analysis",
    )
    
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Trace step-by-step compilation",
    )
    
    parser.add_argument(
        "-c",
        "--code",
        type=str,
        help="Code to compile",
    )
    
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="File to compile",
    )
    
    args = parser.parse_args()
    
    mode_flags = [args.lex, args.parse, args.semantic, args.trace]
    mode_count = sum(mode_flags)
    
    if mode_count == 0:
        repl_mode("trace")
        return
    
    if mode_count > 1:
        print("Error: Only one mode flag (--lex, --parse, --semantic, --trace) can be specified")
        sys.exit(1)
    
    mode = "trace"
    if args.lex:
        mode = "lex"
    elif args.parse:
        mode = "parse"
    elif args.semantic:
        mode = "semantic"
    elif args.trace:
        mode = "trace"
    
    if args.code:
        source_code = args.code
    elif args.file:
        try:
            with open(args.file, "r") as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
    else:
        repl_mode(mode)
        return
    
    if mode == "lex":
        print_tokens(source_code)
    elif mode == "parse":
        print_ast(source_code)
    elif mode == "semantic":
        print_semantic_analysis(source_code)
    elif mode == "trace":
        print_trace(source_code)


if __name__ == "__main__":
    main()
