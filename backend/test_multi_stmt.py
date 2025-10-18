from toyc.tracer import trace_compilation
import json

code = """x = 5
y = 10"""

result = trace_compilation(code)

# Find the Program node in the trace
program_step = None
for step in result['steps']:
    if step['phase'] == 'parsing' and step['state'].get('action') == 'create_ast_node':
        ast_node = step['state'].get('ast_node', {})
        if ast_node.get('type') == 'Program':
            program_step = step
            break

if program_step:
    print("✓ Program node found in trace")
    print(f"  Step ID: {program_step['step_id']}")
    print(f"  Statements: {len(program_step['state']['ast_node']['statements'])}")
    print()
    print("Statement types:")
    for stmt in program_step['state']['ast_node']['statements']:
        print(f"  - {stmt['type']}: {stmt.get('identifier', 'N/A')}")
else:
    print("✗ Program node NOT found in trace")
