# ToyC Compiler Visualization

A monorepo containing a toy compiler implementation with an educational visualization interface.

## Project Structure

```
toyc/
├── backend/          # Python FastAPI backend
├── frontend/         # Next.js frontend
└── main.py          # Original REPL (for reference)
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