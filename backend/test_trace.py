from toyc.tracer import trace_compilation

code = """x = 5
y = 10"""

result = trace_compilation(code)

print("=== PARSING PHASE TRACE (AST Nodes) ===")
for step in result['steps']:
    if step['phase'] == 'parsing' and step['state'].get('action') == 'create_ast_node':
        ast_node = step['state'].get('ast_node', {})
        print(f"Step {step['step_id']}: Created {ast_node.get('type')} node")
        if ast_node.get('type') == 'Program':
            print(f"  Program has {len(ast_node.get('statements', []))} statements")
        elif ast_node.get('type') == 'Assignment':
            print(f"  Assignment to {ast_node.get('identifier')}")
