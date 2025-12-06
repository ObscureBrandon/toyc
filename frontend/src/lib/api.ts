const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Token {
  type: string;
  literal: string;
  position: number;
  line: number;
  column: number;
}

export interface LexerResponse {
  tokens: Token[];
  source_code: string;
  normalized_code: string;
  identifier_mapping: Record<string, string>;
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
  // Error node fields
  message?: string;
  expected?: string[];
  found?: string;
  position?: { line: number; col: number };
  context?: string;
}

export interface ParserResponse {
  ast: ASTNode;
  source_code: string;
  success: boolean;
  error?: string;
  error_position?: number;
  error_line?: number;
  error_column?: number;
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
  error_phase?: string; // 'lexing', 'parsing', 'semantic_analysis'
  error_line?: number;
  error_column?: number;
  error_position?: number;
  identifier_mapping?: Record<string, string>;  // Maps variable names to id1, id2, etc. (or V1, V2 in hybrid)
  // Hybrid mode execution results
  executed_ast?: ExecutedASTNode;  // AST with execution results on each node
  variables?: Record<string, number>;  // Final variable state after execution
  output?: (number | string)[];  // Write statement outputs
}

// Extended AST node with execution results (for hybrid mode)
export interface ExecutedASTNode extends ASTNode {
  result?: number | string | boolean;
  result_type?: 'int' | 'float' | 'bool';
  error?: string;  // Runtime error if any
  branch_taken?: 'then' | 'else' | 'none';  // For if statements
  iterations?: number;  // For repeat-until loops
}

export interface TraceRequest {
  source_code: string;
  mode?: 'standard' | 'hybrid';
}

export interface ICGInstruction {
  op: string;
  arg1?: string;
  arg2?: string;
  result?: string;
  label?: string;
  instruction: string;
}

export interface ICGResponse {
  instructions: ICGInstruction[];
  source_code: string;
  success: boolean;
  error?: string;
  temp_count: number;
  label_count: number;
  identifier_mapping: Record<string, string>;
}

export interface ICGRequest {
  source_code: string;
}

export interface OptimizationStats {
  original_instruction_count: number;
  optimized_instruction_count: number;
  instructions_saved: number;
  reduction_percentage: number;
  int2float_inlined: number;
  temps_eliminated: number;
  copies_propagated: number;
  algebraic_simplifications: number;
  dead_code_eliminated: number;
}

export interface OptimizationResponse {
  original_instructions: ICGInstruction[];
  optimized_instructions: ICGInstruction[];
  source_code: string;
  success: boolean;
  error?: string;
  stats?: OptimizationStats;
  temp_count: number;
  label_count: number;
  identifier_mapping: Record<string, string>;
}

export interface OptimizationRequest {
  source_code: string;
}

export interface AssemblyInstruction {
  op: string;
  operands: string[];
  instruction: string;
}

export interface CodeGenResponse {
  assembly_instructions: AssemblyInstruction[];
  optimized_instructions: ICGInstruction[];
  source_code: string;
  success: boolean;
  error?: string;
  identifier_mapping: Record<string, string>;
  type_map: Record<string, string>;
}

export interface CodeGenRequest {
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

  async traceCode(sourceCode: string, mode: 'standard' | 'hybrid' = 'standard'): Promise<TraceResponse> {
    const response = await fetch(`${this.baseUrl}/api/trace`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode, mode } as TraceRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to trace code: ${response.statusText}`);
    }

    return response.json() as Promise<TraceResponse>;
  }

  async generateICG(sourceCode: string): Promise<ICGResponse> {
    const response = await fetch(`${this.baseUrl}/api/icg`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as ICGRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate ICG: ${response.statusText}`);
    }

    return response.json() as Promise<ICGResponse>;
  }

  async optimizeCode(sourceCode: string): Promise<OptimizationResponse> {
    const response = await fetch(`${this.baseUrl}/api/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as OptimizationRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to optimize code: ${response.statusText}`);
    }

    return response.json() as Promise<OptimizationResponse>;
  }

  async generateCode(sourceCode: string): Promise<CodeGenResponse> {
    const response = await fetch(`${this.baseUrl}/api/codegen`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source_code: sourceCode } as CodeGenRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate code: ${response.statusText}`);
    }

    return response.json() as Promise<CodeGenResponse>;
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