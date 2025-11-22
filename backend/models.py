from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class LexerRequest(BaseModel):
    source_code: str


class TokenResponse(BaseModel):
    type: str
    literal: str
    position: int
    line: int
    column: int


class LexerResponse(BaseModel):
    tokens: list[TokenResponse]
    source_code: str
    normalized_code: str
    identifier_mapping: Dict[str, str]


class ParserRequest(BaseModel):
    source_code: str


class ASTNodeResponse(BaseModel):
    type: str
    data: Dict[str, Any]


class ParserResponse(BaseModel):
    ast: ASTNodeResponse
    source_code: str
    success: bool
    error: Optional[str] = None
    error_position: Optional[int] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None


class TraceRequest(BaseModel):
    source_code: str


class TraceStep(BaseModel):
    phase: str  # 'lexing', 'parsing', 'semantic-analysis'
    step_id: int
    position: Optional[int] = None
    description: str
    state: Dict[str, Any]


class TraceResponse(BaseModel):
    steps: List[TraceStep]
    source_code: str
    success: bool
    tokens: Optional[List[Dict[str, str]]] = None
    ast: Optional[Dict[str, Any]] = None
    analyzed_ast: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_phase: Optional[str] = None  # 'lexing', 'parsing', or 'semantic_analysis'
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_position: Optional[int] = None


class ICGInstruction(BaseModel):
    """Represents a single three-address code instruction."""

    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
    label: Optional[str] = None
    instruction: str  # String representation of the full instruction


class ICGRequest(BaseModel):
    """Request to generate intermediate code."""

    source_code: str


class ICGResponse(BaseModel):
    """Response containing generated intermediate code."""

    instructions: List[ICGInstruction]
    source_code: str
    success: bool
    error: Optional[str] = None
    temp_count: int
    label_count: int
    identifier_mapping: dict[str, str]  # Maps variable names to id1, id2, etc.