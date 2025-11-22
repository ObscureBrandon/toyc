# ToyC Compiler Visualization

A monorepo containing a toy compiler implementation with an educational visualization interface.

## Project Structure

```
toyc/
├── backend/          # Python FastAPI backend
├── frontend/         # Next.js frontend
└── main.py          # Original REPL (for reference)
```

## ToyC Language Syntax

ToyC is a simple imperative programming language with the following features:

### Data Types
- **Integer**: `42`, `-15`, `0`
- **Float**: `3.14`, `-0.5`, `2.0`
- **Identifier**: Variable names like `x`, `count`, `total_sum`

### Operators

**Arithmetic:**
- `+` - Addition
- `-` - Subtraction
- `*` - Multiplication
- `/` - Division
- `%` - Modulo

**Comparison:**
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal
- `>=` - Greater than or equal
- `==` - Equal to
- `!=` - Not equal to

**Logical:**
- `&&` - Logical AND
- `||` - Logical OR

**Assignment:**
- `:=` - Assignment operator (not `=`)

### Keywords

- `if` - Conditional statement
- `then` - Required after if condition
- `else` - Alternative branch
- `end` - Block terminator (not `{}`)
- `repeat` - Start of repeat-until loop
- `until` - End condition for repeat loop
- `read` - Input statement
- `write` - Output statement

### Statements

**Assignment:**
```
x := 5;
total := x + 10;
```

**Conditional (if-else):**
```
if (x >= 3) then read y; else write x % 2; end
```

**Repeat-Until Loop:**
```
repeat
  z := z + 1;
until z != 10;
```

**Input/Output:**
```
read x;
write x * 2;
```

### Syntax Rules

1. **Semicolons (`;`)**: Required to terminate statements
2. **Block Delimiters**: Use `end` keyword (NOT curly braces)
3. **Comments**: 
   - **Single-line**: `%% comment text` (skips rest of line)
   - **Multi-line**: `{ comment text }` (can span multiple lines)
   ```
   %% This is a single-line comment
   x := 10 % 3;  { inline multi-line comment }
   { 
     Multi-line comment
     spanning multiple lines
   }
   ```
4. **Parentheses**: Required around conditions in `if` statements
5. **Assignment**: Always use `:=` (not `=`)

### Example Program

```
%% Initialize variable
x := 5;
{ Check if x is greater than or equal to 3 }
if (x >= 3) then
  read y;
else
  write x % 2;  %% Output modulo result
end
repeat
  z := z + 1;
until z != 10;
```

## Backend (Python + FastAPI)

Located in `backend/` directory.

**Technology Stack:**
- Python 3.12+
- FastAPI for web API
- uv for package management
- Deployed on Render

**Key Components:**
- `toyc/` - Compiler package with lexer, parser, semantic analyzer, and ICG generator
- `toyc/lexer.py` - Lexical analyzer
- `toyc/parser.py` - Syntax analyzer (AST generation)
- `toyc/semantic_analyzer.py` - Semantic analysis and type checking
- `toyc/icg.py` - Intermediate code generator (three-address code)
- `api.py` - FastAPI application with CORS support
- `models.py` - Pydantic request/response schemas
- `render.yaml` - Render deployment configuration

**Development:**
```bash
cd backend
uv sync
uv run uvicorn api:app --reload
```

**API Endpoints:**
- `GET /` - API status
- `GET /health` - Health check
- `POST /api/lex` - Tokenize source code
- `POST /api/parse` - Parse source code into AST
- `POST /api/analyze` - Perform semantic analysis
- `POST /api/icg` - Generate intermediate code (three-address code)

## Frontend (Next.js + TypeScript)

Located in `frontend/` directory.

**Technology Stack:**
- Next.js 15 with App Router
- TypeScript
- Tailwind CSS
- Bun for package management
- Deployed on Vercel

**Key Components:**
- `src/components/LexerVisualizer.tsx` - Lexer visualization component
- `src/components/ASTVisualizer.tsx` - AST visualization component
- `src/components/ICGVisualizer.tsx` - Intermediate code generation visualizer (standalone)
- `src/components/ICGPhase.tsx` - ICG phase in step-by-step visualizer
- `src/components/StepByStepVisualizer.tsx` - Step-by-step compilation process
- `src/lib/api.ts` - API client for backend communication
- `src/app/page.tsx` - Homepage with step-by-step visualizer

**Development:**
```bash
cd frontend
bun install
bun dev
```

## Features

### Compiler Pipeline Visualization

#### 1. Lexical Analysis (Lexer)
- Interactive source code input
- Real-time tokenization
- Color-coded token display by type
- **Identifier mapping display** - shows how identifiers map to normalized forms (e.g., `x → id1`, `y → id2`)
- **Normalized representation** - identifiers replaced with `id1`, `id2`, `id3`, etc.
- Detailed token stream table
- Error handling and loading states

#### 2. Syntax Analysis (Parser)
- Abstract Syntax Tree (AST) visualization
- Tree structure display with parent-child relationships
- Node type identification
- Position tracking in source code

#### 3. Semantic Analysis
- Type checking and validation
- Annotated AST with type information
- Error detection and reporting

#### 4. Intermediate Code Generation (ICG)
- Three-address code (TAC) generation
- **Literal convention**: All literals prefixed with `#` (e.g., `#5`, `#3.14`)
- Operations supported:
  - Arithmetic: `+`, `-`, `*`, `/`, `%`
  - Comparisons: `<`, `>`, `<=`, `>=`, `==`, `!=`
  - Logical: `&&`, `||`
  - Type conversion: `int2float`
  - Control flow: `if_false`, `goto`, `label`
  - I/O: `read`, `write`
- Visualization features:
  - Identifier mapping display (e.g., `x → id1`, `y → id2`)
  - Table view with line numbers, operations, arguments, and results
  - Code listing view with syntax highlighting
  - Color-coded tokens:
    - Pink: Literals (`#5`, `#3.14`)
    - Green: Temp variables (`temp1`, `temp2`)
    - Blue: Normalized identifiers (`id1`, `id2`)
    - Orange: Labels (`L1`, `L2`)
  - Statistics: instruction count, temp count, label count
  - Interactive legend

#### Example ICG Output

**Input:**
```
x := 5 + 3 * 2;
```

**Three-Address Code:**
```
1. temp1 = #3 * #2
2. temp2 = #5 + temp1
3. id1 = temp2
```

**Identifier Mapping:** `x → id1`

---

**Input:**
```
x := 5;
if (x >= 3) then
  read y;
else
  write x % 2;
end
```

**Three-Address Code:**
```
1. id1 = #5
2. temp1 = id1 >= #3
3. if_false temp1 goto L1
4. read id2
5. goto L2
6. label L1:
7. temp2 = id1 % #2
8. write temp2
9. label L2:
```

**Identifier Mapping:** `x → id1`, `y → id2`

### Step-by-Step Visualization
- Animated compilation process through all phases
- Phase-by-phase breakdown:
  - Lexing with token stream
  - Parsing with AST generation
  - Semantic analysis with type annotations
  - Intermediate code generation (ICG) with three-address code
- Interactive phase tabs to switch between compiler stages
- Playback controls with speed adjustment
- Progress tracking for each phase

## Deployment

**Backend (Render):**
- Configure with `backend/render.yaml`
- Automatic deployment from git push
- Environment variables for CORS configuration

**Frontend (Vercel):**
- Deploy from `frontend/` directory
- Set `NEXT_PUBLIC_API_URL` environment variable
- Automatic deployment from git push

## Contributing

1. Backend changes: Work in `backend/` directory
2. Frontend changes: Work in `frontend/` directory  
3. Keep both services in sync for API contract changes
4. Test locally before deploying

## License

Educational project - see course materials for licensing.
