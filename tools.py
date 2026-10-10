import logging
import time
import ast
import math
import operator
from rag.knowledge import search_knowledge


logger = logging.getLogger(__name__)


# ==========================================
# 1. Calculate
# ==========================================

def calculate(expression: str) -> int | float:
    """Safely evaluate basic arithmetic without using eval()."""

    if not isinstance(expression, str):
        raise ValueError("Expression must be a string.")

    expression = expression.strip()

    if not expression or len(expression) > 200:
        raise ValueError("Expression is empty or too long.")

    allowed_characters = set("0123456789+-*/().% ")

    if any(char not in allowed_characters for char in expression):
        raise ValueError("Expression contains unsupported characters.")

    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
    }

    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError, MemoryError):
        raise ValueError("Invalid mathematical expression.") from None

    if sum(1 for _ in ast.walk(tree)) > 50:
        raise ValueError("Expression is too complex.")

    def bounded(value):
        if type(value) is int:
            if value.bit_length() > 256:
                raise ValueError("Result is too large.")
        elif type(value) is float:
            if not math.isfinite(value) or abs(value) > 1e100:
                raise ValueError("Result is too large or non-finite.")
        else:
            raise ValueError("Unsupported arithmetic value.")

        return value

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return bounded(node.value)

        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return bounded(unary_ops[type(node.op)](evaluate(node.operand)))

        if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
                raise ValueError("Division by zero.")

            try:
                result = binary_ops[type(node.op)](left, right)
            except (ArithmeticError, OverflowError):
                raise ValueError("Arithmetic operation failed.") from None

            return bounded(result)

        raise ValueError("Unsupported mathematical expression.")

    return evaluate(tree)

# ==========================================
# 2. Available Functions
# ==========================================

available_functions = {
    "calculate": calculate,
    "search_knowledge": search_knowledge,
}


# ==========================================
# 3. Tool Schemas
# ==========================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Calculate a mathematical expression. "
                "Use this tool for arithmetic calculations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression such as "
                            "'25 * 4' or '(100 / 5) + 7'."
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": (
                "Search the company's indexed documents "
                "for relevant information. "
                "Use this when the user asks about "
                "company policies, procedures, or information "
                "contained in the provided documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The question or information "
                            "to search for in the documents."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# ==========================================
# 4. Execute Tool
# ==========================================

def execute_tool(
    function_name: str,
    arguments: dict
):
    """
    Execute an agent tool and measure its latency.
    """

    if function_name not in available_functions:
        raise ValueError(
            f"Unknown tool: {function_name}"
        )

    function = available_functions[function_name]

    logger.info(
        "Tool started | tool=%s",
        function_name,
    )

    start_time = time.perf_counter()

    try:

        result = function(**arguments)

        elapsed = time.perf_counter() - start_time

        logger.info(
            "Tool completed | tool=%s | latency=%.3fs",
            function_name,
            elapsed,
        )

        return result

    except Exception:

        elapsed = time.perf_counter() - start_time

        logger.exception(
            "Tool failed | tool=%s | latency=%.3fs",
            function_name,
            elapsed,
        )

        raise
