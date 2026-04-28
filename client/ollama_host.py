import asyncio
import json
from typing import Any

import ollama
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.config import get_settings


def mcp_tool_to_ollama_tool(tool: Any) -> dict[str, Any]:
    input_schema = getattr(tool, "inputSchema", None) or {}

    if not isinstance(input_schema, dict):
        input_schema = {}

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or f"Execute MCP tool {tool.name}",
            "parameters": {
                "type": "object",
                "properties": input_schema.get("properties", {}),
                "required": input_schema.get("required", []),
            },
        },
    }


def extract_text_from_tool_result(result: Any) -> str:
    output_parts: list[str] = []

    for content in result.content:
        if hasattr(content, "text"):
            output_parts.append(content.text)
        else:
            output_parts.append(str(content))

    return "\n".join(output_parts) if output_parts else "No tool output."


async def call_mcp_tool(
    session: ClientSession,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    result = await session.call_tool(tool_name, arguments)
    return extract_text_from_tool_result(result)


async def chat_once(user_message: str) -> str:
    settings = get_settings()
    mcp_url = f"http://{settings.mcp_server_host}:{settings.mcp_server_port}/mcp"

    async with streamable_http_client(mcp_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            ollama_tools = [mcp_tool_to_ollama_tool(tool) for tool in mcp_tools]

            print("Available MCP tools:")
            for tool in mcp_tools:
                print(f"- {tool.name}")

            messages: list[dict[str, Any]] = [
                {
                    "role": "system",
                    "content": (
                        "You are SupportOps Agent, an enterprise support assistant. "
                        "You have access to MCP tools for support tickets, customers, SLA rules, "
                        "and current user context. "
                        "Use tools whenever the user asks about tickets, customers, SLA, permissions, "
                        "or operational data. "
                        "Do not invent ticket, customer, SLA, or user data. "
                        "If a tool returns an access denied error, explain that the current user "
                        "does not have permission to perform that action."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ]

            first_response = ollama.chat(
                model=settings.ollama_model,
                messages=messages,
                tools=ollama_tools,
            )

            assistant_message = first_response["message"]
            messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                return assistant_message.get("content", "")

            for tool_call in tool_calls:
                function_data = tool_call.get("function", {})
                tool_name = function_data.get("name")
                arguments = function_data.get("arguments", {}) or {}

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                if not tool_name:
                    continue

                print(f"[tool call] {tool_name}({arguments})")

                tool_output = await call_mcp_tool(
                    session=session,
                    tool_name=tool_name,
                    arguments=arguments,
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_output,
                    }
                )

            final_response = ollama.chat(
                model=settings.ollama_model,
                messages=messages,
            )

            return final_response["message"].get("content", "")


async def interactive_chat() -> None:
    settings = get_settings()

    print("SupportOps Ollama Host")
    print(f"Model: {settings.ollama_model}")
    print(f"MCP Server: http://{settings.mcp_server_host}:{settings.mcp_server_port}/mcp")
    print("Type 'exit' to quit.")
    print()

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in {"exit", "quit"}:
            break

        if not user_message:
            continue

        try:
            response = await chat_once(user_message)
            print(f"\nAgent: {response}\n")
        except Exception as exc:
            print(f"\nError: {exc}\n")


if __name__ == "__main__":
    asyncio.run(interactive_chat())