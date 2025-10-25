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
)
from toyc.lexer import Lexer
from toyc.token import TokenType
from toyc.parser import parse_code
from toyc.ast import ParseError
from toyc.tracer import trace_compilation

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
            TokenResponse(type=tok.type.name, literal=tok.literal, position=position)
        )
        position += 1

        if tok.type == TokenType.EOF:
            break

    return LexerResponse(tokens=tokens, source_code=request.source_code)


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

        if not result["success"]:
            return TraceResponse(
                steps=[],
                source_code=request.source_code,
                success=False,
                error=result.get("error", "Unknown error"),
            )

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
            success=True,
            tokens=result.get("tokens"),
            ast=result.get("ast"),
            analyzed_ast=result.get("analyzed_ast"),
        )

    except Exception as e:
        return TraceResponse(
            steps=[],
            source_code=request.source_code,
            success=False,
            error=f"Unexpected error: {str(e)}",
        )
