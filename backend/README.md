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

## REPL Usage

The ToyC compiler includes a command-line REPL for interactive compilation and analysis.

### Basic Usage

Interactive REPL (default trace mode):
```bash
python3 repl.py
```

### Command-line Modes

Run with code string:
```bash
python3 repl.py --lex -c "x := 5 + 3.14"
python3 repl.py --parse -c "x := 5 + 3.14"
python3 repl.py --semantic -c "x := 5 + 3.14"
python3 repl.py --trace -c "x := 5 + 3.14"
```

Run with file:
```bash
python3 repl.py --semantic -f example.toyc
```

### Available Flags

- `--lex` - Lexer only, outputs tokens as JSON
- `--parse` - Lexer + Parser, outputs AST as JSON
- `--semantic` - Full semantic analysis with type coercion
- `--trace` - Step-by-step trace through all compilation phases
- `-c CODE` - Compile code from command line
- `-f FILE` - Compile code from file

### ToyC Language Features

- **Assignment**: `x := 5` (note: uses `:=`, not `=`)
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Comparison**: `<`, `>`, `<=`, `>=`, `==`, `!=`
- **Logical**: `&&`, `||`
- **Types**: integers (`42`), floats (`3.14`), identifiers
- **Keywords**: `if`, `else`, `end`, `repeat`, `until`, `read`, `write`

### Example

```bash
$ python3 repl.py --lex -c "if x >= 5 read y"
[
  {"type": "IF", "literal": "if"},
  {"type": "IDENTIFIER", "literal": "x"},
  {"type": "GT_EQ", "literal": ">="},
  {"type": "NUMBER", "literal": "5"},
  {"type": "READ", "literal": "read"},
  {"type": "IDENTIFIER", "literal": "y"},
  {"type": "EOF", "literal": ""}
]
```

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/lex` - Tokenize source code

## Deployment

This service is configured for Render deployment using `render.yaml`.