"""Direct execution interpreter for the hybrid compiler mode."""

from typing import Dict, List, Union, Any
from .ast import (
    ASTNode,
    ProgramNode,
    BinaryOpNode,
    NumberNode,
    FloatNode,
    IdentifierNode,
    AssignmentNode,
    Int2FloatNode,
    BlockNode,
    IfNode,
    RepeatUntilNode,
    ReadNode,
    WriteNode,
)


class Interpreter:
    """Executes an analyzed AST and returns results at each node."""

    def __init__(self):
        self.variables: Dict[str, Union[int, float]] = {}
        self.output: List[Union[int, float, str]] = []
        self.execution_steps: List[dict] = []
        self.step_id = 0

    def execute(self, analyzed_ast: ProgramNode) -> dict:
        """Execute the AST and return execution results."""
        executed_ast = self._execute_node(analyzed_ast)

        return {
            "executed_ast": executed_ast,
            "variables": dict(self.variables),
            "output": self.output,
            "execution_steps": self.execution_steps,
        }

    def _trace_step(self, description: str, node_type: str, result: Any):
        """Record an execution step."""
        self.execution_steps.append(
            {
                "phase": "direct-execution",
                "step_id": self.step_id,
                "description": description,
                "position": None,  # No source position for execution steps
                "state": {
                    "node_type": node_type,
                    "result": result,
                    "action": "execute",
                },
            }
        )
        self.step_id += 1

    def _execute_node(self, node: ASTNode) -> dict:
        """Execute a node and return its dict with result attached."""
        # Dispatch based on node type
        if isinstance(node, ProgramNode):
            return self._execute_program(node)
        elif isinstance(node, AssignmentNode):
            return self._execute_assignment(node)
        elif isinstance(node, BinaryOpNode):
            return self._execute_binary_op(node)
        elif isinstance(node, NumberNode):
            return self._execute_number(node)
        elif isinstance(node, FloatNode):
            return self._execute_float(node)
        elif isinstance(node, IdentifierNode):
            return self._execute_identifier(node)
        elif isinstance(node, Int2FloatNode):
            return self._execute_int2float(node)
        elif isinstance(node, IfNode):
            return self._execute_if(node)
        elif isinstance(node, RepeatUntilNode):
            return self._execute_repeat(node)
        elif isinstance(node, ReadNode):
            return self._execute_read(node)
        elif isinstance(node, WriteNode):
            return self._execute_write(node)
        elif isinstance(node, BlockNode):
            return self._execute_block(node)
        else:
            return node.to_dict()

    def _execute_program(self, node: ProgramNode) -> dict:
        executed_statements = []
        for stmt in node.statements:
            executed_statements.append(self._execute_node(stmt))

        return {
            "type": "Program",
            "statements": executed_statements,
            "result": None,  # Program doesn't have a single result
        }

    def _execute_number(self, node: NumberNode) -> dict:
        result = node.value
        self._trace_step(f"Evaluated number: {result}", "Number", result)
        return {
            "type": "Number",
            "value": node.value,
            "result": result,
            "result_type": "int",
        }

    def _execute_float(self, node: FloatNode) -> dict:
        result = node.value
        self._trace_step(f"Evaluated float: {result}", "Float", result)
        return {
            "type": "Float",
            "value": node.value,
            "result": result,
            "result_type": "float",
        }

    def _execute_identifier(self, node: IdentifierNode) -> dict:
        result = self.variables.get(node.name, 0)  # Default to 0 if undefined
        self._trace_step(f"Looked up {node.name}: {result}", "Identifier", result)
        return {
            "type": "Identifier",
            "name": node.name,
            "result": result,
            "result_type": "float" if isinstance(result, float) else "int",
        }

    def _execute_int2float(self, node: Int2FloatNode) -> dict:
        child_result = self._execute_node(node.child)
        result = float(child_result["result"])
        self._trace_step(
            f"Converted {child_result['result']} to float: {result}", "Int2Float", result
        )
        return {
            "type": "Int2Float",
            "child": child_result,
            "result": result,
            "result_type": "float",
        }

    def _execute_binary_op(self, node: BinaryOpNode) -> dict:
        left_result = self._execute_node(node.left)
        right_result = self._execute_node(node.right)

        left_val = left_result["result"]
        right_val = right_result["result"]

        # Compute result based on operator
        op = node.operator
        error = None
        
        try:
            if op == "+":
                result = left_val + right_val
            elif op == "-":
                result = left_val - right_val
            elif op == "*":
                result = left_val * right_val
            elif op == "/":
                if right_val == 0:
                    result = float("inf")
                    error = "Division by zero"
                else:
                    result = left_val / right_val
            elif op == "%":
                if right_val == 0:
                    result = 0
                    error = "Modulo by zero"
                else:
                    result = left_val % right_val
            elif op == "==":
                result = left_val == right_val
            elif op == "!=":
                result = left_val != right_val
            elif op == "<":
                result = left_val < right_val
            elif op == ">":
                result = left_val > right_val
            elif op == "<=":
                result = left_val <= right_val
            elif op == ">=":
                result = left_val >= right_val
            elif op == "&&":
                result = bool(left_val) and bool(right_val)
            elif op == "||":
                result = bool(left_val) or bool(right_val)
            else:
                result = None
        except Exception as e:
            result = None
            error = str(e)

        result_type = (
            "bool"
            if isinstance(result, bool)
            else ("float" if isinstance(result, float) else "int")
        )
        self._trace_step(
            f"Computed {left_val} {op} {right_val} = {result}", "BinaryOp", result
        )

        node_dict = {
            "type": "BinaryOp",
            "operator": node.operator,
            "left": left_result,
            "right": right_result,
            "result": result,
            "result_type": result_type,
        }
        
        if error:
            node_dict["error"] = error
            
        return node_dict

    def _execute_assignment(self, node: AssignmentNode) -> dict:
        value_result = self._execute_node(node.value)
        result = value_result["result"]
        result_type = value_result.get("result_type", "unknown")
        self.variables[node.identifier] = result
        self._trace_step(
            f"Assigned {node.identifier} = {result}", "Assignment", result
        )

        return {
            "type": "Assignment",
            "left": {
                "type": "Identifier",
                "name": node.identifier,
                "result": result,
                "result_type": result_type,
            },
            "right": value_result,
            "result": result,
            "result_type": result_type,
        }

    def _execute_read(self, node: ReadNode) -> dict:
        # Use placeholder value of 0
        self.variables[node.identifier] = 0
        self._trace_step(f"Read {node.identifier} = 0 (placeholder)", "Read", 0)

        return {
            "type": "Read",
            "identifier": node.identifier,
            "result": 0,
            "result_type": "int",
        }

    def _execute_write(self, node: WriteNode) -> dict:
        expr_result = self._execute_node(node.expression)
        result = expr_result["result"]
        self.output.append(result)
        self._trace_step(f"Write output: {result}", "Write", result)

        return {
            "type": "Write",
            "expression": expr_result,
            "result": result,
            "result_type": expr_result.get("result_type", "unknown"),
        }

    def _execute_block(self, node: BlockNode) -> dict:
        executed_statements = []
        for stmt in node.statements:
            executed_statements.append(self._execute_node(stmt))

        return {
            "type": "Block",
            "statements": executed_statements,
            "result": None,
        }

    def _execute_if(self, node: IfNode) -> dict:
        condition_result = self._execute_node(node.condition)
        condition_value = bool(condition_result["result"])

        self._trace_step(
            f"If condition evaluated to {condition_value}", "If", condition_value
        )

        then_result = None
        else_result = None

        if condition_value:
            then_result = self._execute_node(node.then_branch)
        elif node.else_branch:
            else_result = self._execute_node(node.else_branch)

        return {
            "type": "If",
            "condition": condition_result,
            "then_branch": then_result
            or (node.then_branch.to_dict() if node.then_branch else None),
            "else_branch": else_result
            or (node.else_branch.to_dict() if node.else_branch else None),
            "result": condition_value,
            "result_type": "bool",
            "branch_taken": "then"
            if condition_value
            else ("else" if node.else_branch else "none"),
        }

    def _execute_repeat(self, node: RepeatUntilNode) -> dict:
        iteration_count = 0
        max_iterations = 1000  # Prevent infinite loops

        while iteration_count < max_iterations:
            self._execute_node(node.body)
            iteration_count += 1

            condition_result = self._execute_node(node.condition)
            if bool(condition_result["result"]):
                break

        self._trace_step(
            f"Repeat-until completed after {iteration_count} iterations",
            "RepeatUntil",
            iteration_count,
        )

        # Return final state (not all iterations)
        return {
            "type": "RepeatUntil",
            "body": node.body.to_dict(),
            "condition": node.condition.to_dict(),
            "result": iteration_count,
            "result_type": "int",
            "iterations": iteration_count,
        }
