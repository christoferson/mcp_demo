# client_localhost.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    """Test the MCP server via HTTP localhost."""

    print("=" * 60)
    print("AWS MCP Client - Localhost HTTP")
    print("=" * 60)

    try:
        # Connect to localhost MCP server
        print("\n1. Connecting to http://localhost:8000/mcp...")

        # streamablehttp_client returns streams directly, not a tuple
        async with streamablehttp_client("http://localhost:8000/mcp") as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                # Initialize
                print("2. Initializing session...")
                init_result = await session.initialize()
                print(f"   ✓ Connected to: {init_result.serverInfo.name}")

                # List available tools
                print("\n3. Listing available tools...")
                tools_result = await session.list_tools()
                print(f"   Available tools:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")

                # Test: List S3 buckets
                print("\n4. Testing: List S3 buckets...")
                result = await session.call_tool("list_s3_buckets", {})
                print(f"   Result:\n{result.content[0].text}")

                print("\n" + "=" * 60)
                print("✓ Success!")
                print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())