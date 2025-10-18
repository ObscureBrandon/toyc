# ToyC Backend

FastAPI backend for the ToyC compiler visualization.

## Development

Install dependencies:
```bash
uv sync
```

Run development server:
```bash
uv run uvicorn api:app --reload
```

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/lex` - Tokenize source code

## Deployment

This service is configured for Render deployment using `render.yaml`.