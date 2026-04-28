import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def print_tool_result(session: ClientSession, tool_name: str, arguments: dict) -> None:
    print(f"\nCalling {tool_name}...")
    try:
        result = await session.call_tool(tool_name, arguments)
        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)
    except Exception as exc:
        print(f"Tool call failed: {exc}")


async def main() -> None:
    server_url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            await print_tool_result(session, "whoami", {})
            await print_tool_result(session, "list_open_tickets", {})
            await print_tool_result(session, "detect_sla_risk", {})
            await print_tool_result(session, "get_customer_sla", {"customer_id": 1})


if __name__ == "__main__":
    asyncio.run(main())