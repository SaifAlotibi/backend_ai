# =========================
# Tool functions
# =========================

def calculate(
    a: float,
    b: float,
    operation: str
):
    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            return "Cannot divide by zero."

        return a / b

    return "Unknown operation."


# =========================
# Functions available
# to the agent
# =========================

available_functions = {
    "calculate": calculate
}


# =========================
# Tool schema
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",

            "description": (
                "Perform arithmetic operations "
                "between two numbers."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },

                    "b": {
                        "type": "number",
                        "description": "Second number"
                    },

                    "operation": {
                        "type": "string",

                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide"
                        ],

                        "description": (
                            "The arithmetic operation "
                            "to perform."
                        )
                    }
                },

                "required": [
                    "a",
                    "b",
                    "operation"
                ]
            }
        }
    }
]