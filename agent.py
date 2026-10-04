from ollama import chat_with_ollama
from tools import available_functions, tools


async def run_agent(messages):

    max_steps = 5

    for _ in range(max_steps):

        response = await chat_with_ollama(
            messages,
            tools
        )

        message = response["message"]

        tool_calls = message.get(
            "tool_calls",
            []
        )

        # ---------------------------------------------
        # Final answer
        # ---------------------------------------------

        if not tool_calls:

            return message.get(
                "content",
                ""
            )


        # ---------------------------------------------
        # Save assistant tool-call message
        # ---------------------------------------------

        messages.append(message)


        # ---------------------------------------------
        # Execute tools
        # ---------------------------------------------

        for tool_call in tool_calls:

            function_name = (
                tool_call["function"]["name"]
            )

            arguments = (
                tool_call["function"]["arguments"]
            )

            function = available_functions.get(
                function_name
            )

            if function is None:

                raise ValueError(
                    f"Unknown tool: {function_name}"
                )

            result = function(
                **arguments
            )

            messages.append({
                "role": "tool",
                "content": str(result)
            })


    return "Maximum agent steps reached."