from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class LexerRequest(BaseModel):
    source_code: str


class TokenResponse(BaseModel):
    type: str
    literal: str
    position: int


class LexerResponse(BaseModel):
    tokens: list[TokenResponse]
    source_code: str


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