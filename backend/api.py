from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import (
    LexerRequest,
    LexerResponse,
    TokenResponse,
    ParserRequest,
    ParserResponse,
    ASTNodeResponse,
    TraceRequest,
    TraceResponse,
    TraceStep,
    ICGRequest,
    ICGResponse,
    ICGInstruction,
    OptimizationRequest,
    OptimizationResponse,
    OptimizationStats,
)
from toyc.lexer import Lexer
from toyc.token import TokenType
from toyc.parser import parse_code
from toyc.ast import ParseError
from toyc.tracer import trace_compilation
from toyc.semantic_analyzer import SemanticAnalyzer
from toyc.icg import ICGGenerator
from toyc.optimizer import Optimizer

app = FastAPI(
    title="ToyC Compiler API",
    description="API for ToyC compiler visualization",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "ToyC Compiler API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/lex", response_model=LexerResponse)
async def lex_code(request: LexerRequest) -> LexerResponse:
    """Tokenize source code and return structured tokens."""
    lexer = Lexer(request.source_code)
    tokens = []
    position = 0

    while True:
        tok = lexer.next_token()
        tokens.append(
            TokenResponse(
                type=tok.type.name,
                literal=tok.literal,
                position=position,
                line=tok.line,
                column=tok.column,
            )
        )
        position += 1

        if tok.type == TokenType.EOF:
            break

    # Generate normalized representation
    identifier_map: dict[str, str] = {}
    identifier_counter = 1
    normalized_parts: list[str] = []

    for token in tokens:
        if token.type == "IDENTIFIER":
            if token.literal not in identifier_map:
                identifier_map[token.literal] = f"id{identifier_counter}"
                identifier_counter += 1
            normalized_parts.append(identifier_map[token.literal])
        elif token.type != "EOF":
            normalized_parts.append(token.literal)

    normalized_code = " ".join(normalized_parts)

    return LexerResponse(
        tokens=tokens,
        source_code=request.source_code,
        normalized_code=normalized_code,
        identifier_mapping=identifier_map,
    )


@app.post("/api/parse", response_model=ParserResponse)
async def parse_source_code(request: ParserRequest) -> ParserResponse:
    """Parse source code and return AST structure."""
    try:
        ast = parse_code(request.source_code)
        ast_dict = ast.to_dict()

        return ParserResponse(
            ast=ASTNodeResponse(type=ast_dict["type"], data=ast_dict),
            source_code=request.source_code,
            success=True,
        )

    except ParseError as e:
        return ParserResponse(
            ast=ASTNodeResponse(type="Error", data={}),
            source_code=request.source_code,
            success=False,
            error=e.message,
            error_position=e.position,
            error_line=e.line,
            error_column=e.column,
        )

    except Exception as e:
        return ParserResponse(
            ast=ASTNodeResponse(type="Error", data={}),
            source_code=request.source_code,
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


@app.post("/api/trace", response_model=TraceResponse)
async def trace_code(request: TraceRequest) -> TraceResponse:
    """Trace step-by-step compilation process."""
    try:
        result = trace_compilation(request.source_code)

        # Convert steps to TraceStep objects
        trace_steps = []
        for step in result["steps"]:
            trace_steps.append(
                TraceStep(
                    phase=step["phase"],
                    step_id=step["step_id"],
                    position=step.get("position"),
                    description=step["description"],
                    state=step["state"],
                )
            )

        return TraceResponse(
            steps=trace_steps,
            source_code=request.source_code,
            success=result["success"],
            tokens=result.get("tokens"),
            ast=result.get("ast"),
            analyzed_ast=result.get("analyzed_ast"),
            error=result.get("error"),
            error_phase=result.get("error_phase"),
        )

    except Exception as e:
        return TraceResponse(
            steps=[],
            source_code=request.source_code,
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


@app.post("/api/icg", response_model=ICGResponse)
async def generate_icg(request: ICGRequest) -> ICGResponse:
    """Generate intermediate code (three-address code) from source code."""
    try:
        # Parse the source code
        ast = parse_code(request.source_code)

        # Perform semantic analysis
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)

        # Generate intermediate code
        icg_gen = ICGGenerator()
        instructions = icg_gen.generate(analyzed_ast)

        # Convert to response format
        icg_instructions = [
            ICGInstruction(
                op=instr.op,
                arg1=instr.arg1,
                arg2=instr.arg2,
                result=instr.result,
                label=instr.label,
                instruction=str(instr),  # Include string representation
            )
            for instr in instructions
        ]

        return ICGResponse(
            instructions=icg_instructions,
            source_code=request.source_code,
            success=True,
            temp_count=icg_gen.temp_counter,
            label_count=icg_gen.label_counter,
            identifier_mapping=icg_gen.identifier_map,
        )

    except ParseError as e:
        return ICGResponse(
            instructions=[],
            source_code=request.source_code,
            success=False,
            error=f"Parse error: {e.message}",
            temp_count=0,
            label_count=0,
            identifier_mapping={},
        )

    except Exception as e:
        return ICGResponse(
            instructions=[],
            source_code=request.source_code,
            success=False,
            error=f"Error: {str(e)}",
            temp_count=0,
            label_count=0,
            identifier_mapping={},
        )


@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_code(request: OptimizationRequest) -> OptimizationResponse:
    """Optimize intermediate code by eliminating unnecessary temps and simplifying expressions."""
    try:
        # Parse the source code
        ast = parse_code(request.source_code)

        # Perform semantic analysis
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)

        # Generate intermediate code
        icg_gen = ICGGenerator()
        instructions = icg_gen.generate(analyzed_ast)

        # Convert original instructions to response format
        original_icg = [
            ICGInstruction(
                op=instr.op,
                arg1=instr.arg1,
                arg2=instr.arg2,
                result=instr.result,
                label=instr.label,
                instruction=str(instr),
            )
            for instr in instructions
        ]

        # Optimize the code
        optimizer = Optimizer()
        optimized_instructions = optimizer.optimize(instructions)

        # Convert optimized instructions to response format
        optimized_icg = [
            ICGInstruction(
                op=instr.op,
                arg1=instr.arg1,
                arg2=instr.arg2,
                result=instr.result,
                label=instr.label,
                instruction=str(instr),
            )
            for instr in optimized_instructions
        ]

        # Build optimization stats
        stats = OptimizationStats(
            original_instruction_count=optimizer.stats.original_instruction_count,
            optimized_instruction_count=optimizer.stats.optimized_instruction_count,
            instructions_saved=optimizer.stats.instructions_saved,
            reduction_percentage=optimizer.stats.reduction_percentage,
            int2float_inlined=optimizer.stats.int2float_inlined,
            temps_eliminated=optimizer.stats.temps_eliminated,
            copies_propagated=optimizer.stats.copies_propagated,
            algebraic_simplifications=optimizer.stats.algebraic_simplifications,
            dead_code_eliminated=optimizer.stats.dead_code_eliminated,
        )

        return OptimizationResponse(
            original_instructions=original_icg,
            optimized_instructions=optimized_icg,
            source_code=request.source_code,
            success=True,
            stats=stats,
            temp_count=icg_gen.temp_counter,
            label_count=icg_gen.label_counter,
            identifier_mapping=icg_gen.identifier_map,
        )

    except ParseError as e:
        return OptimizationResponse(
            original_instructions=[],
            optimized_instructions=[],
            source_code=request.source_code,
            success=False,
            error=f"Parse error: {e.message}",
            temp_count=0,
            label_count=0,
            identifier_mapping={},
        )

    except Exception as e:
        return OptimizationResponse(
            original_instructions=[],
            optimized_instructions=[],
            source_code=request.source_code,
            success=False,
            error=f"Error: {str(e)}",
            temp_count=0,
            label_count=0,
            identifier_mapping={},
        )

