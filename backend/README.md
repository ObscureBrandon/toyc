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
- `POST /api/parse` - Parse source code to AST
- `POST /api/semantic` - Semantic analysis with type checking
- `POST /api/icg` - Generate three-address code (TAC)
- `POST /api/optimize` - Optimize TAC
- `POST /api/codegen` - Generate assembly from optimized TAC

## Compiler Pipeline

The ToyC compiler follows a multi-phase pipeline:

```
Source Code → Lexer → Parser → Semantic Analyzer → ICG → Optimizer → Code Generator
                ↓        ↓            ↓              ↓        ↓            ↓
             Tokens    AST     Analyzed AST        TAC   Optimized TAC  Assembly
```

### Code Generator

The code generator transforms optimized three-address code (TAC) into assembly-like instructions. It uses a simple register-based architecture with only 2 registers (R1 and R2).

#### Assembly Instructions

| Instruction | Description | Example |
|-------------|-------------|---------|
| `LOAD/LOADF` | Load integer/float into register | `LOAD R1, id1` |
| `STR/STRF` | Store integer/float from register | `STR id1, R1` or `STR id1, #5` |
| `ADD/ADDF` | Addition | `ADD R1, R1, #5` |
| `SUB/SUBF` | Subtraction | `SUB R1, R1, R2` |
| `MUL/MULF` | Multiplication | `MUL R1, R1, #2` |
| `DIV/DIVF` | Division | `DIV R1, R1, R2` |
| `MOD/MODF` | Modulo | `MOD R1, R1, #3` |

#### Example

Input: `x := y + 3.5;`

Optimized TAC:
```
id1 = id2 + #3.5
```

Generated Assembly:
```
LOADF R1, id2
ADDF R1, R1, #3.5
STRF id1, R1
```

#### Design Decisions

- **Commutative optimization**: For `+` and `*`, operands are swapped when the literal is first to avoid loading literals into registers unnecessarily
- **Direct store**: Literal assignments (e.g., `x := 5`) use direct store (`STR id1, #5`) without a register
- **Float handling**: Uses `(f)` annotation from optimizer and type inference from semantic analysis
- **Scope**: Control flow (`if`, `while`, `goto`), I/O (`read`, `write`), and comparison operators are not implemented

## Testing

Run all tests:
```bash
python3 -m pytest test_*.py
```

Run specific test file:
```bash
python3 test_codegen.py
python3 test_optimizer.py
python3 test_parser.py
```

## Deployment

This service is configured for Render deployment using `render.yaml`.