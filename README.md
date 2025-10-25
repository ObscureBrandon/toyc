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
- `toyc/` - Compiler package with lexer, token definitions
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

## Frontend (Next.js + TypeScript)

Located in `frontend/` directory.

**Technology Stack:**
- Next.js 15 with App Router
- TypeScript
- Tailwind CSS
- Bun for package management
- Deployed on Vercel

**Key Components:**
- `src/components/LexerVisualizer.tsx` - Main visualization component
- `src/lib/api.ts` - API client for backend communication
- `src/app/page.tsx` - Homepage

**Development:**
```bash
cd frontend
bun install
bun dev
```

## Features

### Current: Lexer Visualization
- Interactive source code input
- Real-time tokenization
- Color-coded token display by type
- Detailed token stream table
- Error handling and loading states

### Planned: Full Compiler Pipeline
- Parser visualization (AST generation)
- Semantic analysis display
- Code generation output
- Step-by-step compilation process

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
