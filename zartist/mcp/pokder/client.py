import asyncio
from fastmcp import Client


def del_key_in_dict(d, key):
    """Return a new dict/list with all occurrences of `key` removed recursively. Remove empty dicts/lists and all None values."""
    if isinstance(d, dict):
        new_dict = {k: del_key_in_dict(v, key) for k, v in d.items() if k != key}
        # 过滤掉 value 为 None 的项
        new_dict = {k: v for k, v in new_dict.items() if v is not None}
        return new_dict or None
    elif isinstance(d, list):
        new_list = [del_key_in_dict(item, key) for item in d]
        # 过滤掉 None
        new_list = [item for item in new_list if item is not None]
        return new_list or None
    else:
        return d


async def prepare_tools():

    async with Client(r"C:\Users\admin\Desktop\projects\zartist\zartist\mcp\pokder\server.py") as client:
        # List available tools
        tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema
            }
        } for tool in await client.list_tools()]
        print(tools)
        return tools

        # # List available resources
        # resources = await client.list_resources()

        # # Call a tool with arguments
        result = await client.call_tool("generate_report", {"user_id": 123})

        # # Read a resource
        # user_data = await client.read_resource("db://users/123/profile")

        # # Get a prompt
        # greeting = await client.get_prompt("welcome", {"name": "Alice"})

        # # Send progress updates
        # await client.progress("task-123", 50, 100)  # 50% complete

        # # Basic connectivity testing
        # await client.ping()


if __name__ == "__main__":
    asyncio.run(prepare_tools())
