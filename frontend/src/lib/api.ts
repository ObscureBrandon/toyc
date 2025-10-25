const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Token {
  type: string;
  literal: string;
  position: number;
}

export interface LexerResponse {
  tokens: Token[];
  source_code: string;
}

export interface LexerRequest {
  source_code: string;
}

export interface ASTNode {
  type: string;
  value?: string | number;
  name?: string;
  operator?: string;
  identifier?: string;
  left?: ASTNode;
  right?: ASTNode;
  child?: ASTNode;
  statements?: ASTNode[];
  condition?: ASTNode;
  then_branch?: ASTNode;
  else_branch?: ASTNode;
  body?: ASTNode;
  expression?: ASTNode;
  data?: Record<string, string | number | boolean | null>;
}

export interface ParserResponse {
  ast: ASTNode;
  source_code: string;
  success: boolean;
  error?: string;
  error_position?: number;
}

export interface ParserRequest {
  source_code: string;
}

export interface TraceStep {
  phase: string; // 'lexing', 'parsing', 'semantic-analysis'
  step_id: number;
  position?: number;
  description: string;
  state: Record<string, string | number | boolean | ASTNode | null | undefined>;
}

export interface TraceResponse {
  steps: TraceStep[];
  source_code: string;
  success: boolean;
  tokens?: Array<{ type: string; literal: string }>;
  ast?: ASTNode;
  analyzed_ast?: ASTNode;
  error?: string;
}

export interface TraceRequest {
  source_code: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async lexCode(sourceCode: string): Promise<LexerResponse> {
    const response = await fetch(`${this.baseUrl}/api/lex`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as LexerRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to lex code: ${response.statusText}`);
    }

    return response.json() as Promise<LexerResponse>;
  }

  async parseCode(sourceCode: string): Promise<ParserResponse> {
    const response = await fetch(`${this.baseUrl}/api/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as ParserRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to parse code: ${response.statusText}`);
    }

    return response.json() as Promise<ParserResponse>;
  }

  async traceCode(sourceCode: string): Promise<TraceResponse> {
    const response = await fetch(`${this.baseUrl}/api/trace`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as TraceRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to trace code: ${response.statusText}`);
    }

    return response.json() as Promise<TraceResponse>;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();