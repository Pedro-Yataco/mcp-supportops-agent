import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main() -> None:
    server_url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\nCalling whoami...")
            result = await session.call_tool("whoami", {})
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)

            print("\nCalling list_open_tickets...")
            result = await session.call_tool("list_open_tickets", {})
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())