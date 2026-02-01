import asyncio
import sqlite3
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


app = Server("demo-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file at the given path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="query_db",
            description="Run a read-only SQL query on the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute",
                    }
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    if name == "read_file":
        path = arguments["path"]
        with open(path, "r") as f:
            content = f.read()
        return [TextContent(type="text", text=content)]

    if name == "query_db":
        query = arguments["query"]

        if not query.strip().upper().startswith("SELECT"):
            return [
                TextContent(type="text", text="Error: Only SELECT queries are allowed")
            ]

        conn = sqlite3.connect(r"C:\\coding\\demo.db")
        cursor = conn.execute(query)
        columns = [description[0] for description in cursor.description]
        
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return [TextContent(type="text", text=json.dumps(rows, indent=2))]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())