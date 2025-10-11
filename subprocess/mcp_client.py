# aws_mcp_client.py
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Test the AWS MCP server."""

    server_script = os.path.abspath("mcp_server.py")

    if not os.path.exists(server_script):
        print(f"❌ ERROR: Server file not found: {server_script}")
        print(f"Current directory: {os.getcwd()}")
        return

    # Get current environment and pass it to server
    env = os.environ.copy()

    # Display AWS configuration being used
    aws_profile = env.get("AWS_PROFILE", "default")
    aws_region = env.get("AWS_DEFAULT_REGION", env.get("AWS_REGION", "us-east-1"))

    print("=" * 60)
    print("AWS Configuration")
    print("=" * 60)
    print(f"AWS Profile: {aws_profile}")
    print(f"AWS Region: {aws_region}")
    print(f"Python: {sys.executable}")
    print(f"Server: {server_script}")

    # Define server parameters with environment variables
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=env  # ← This passes all environment variables to the server
    )

    print("\n" + "=" * 60)
    print("AWS MCP Client Demo")
    print("=" * 60)

    try:
        # Connect to the server
        print("\n1. Connecting to AWS MCP server...")
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                # Initialize
                print("2. Initializing session...")
                init_result = await session.initialize()
                print(f"   ✓ Connected to: {init_result.serverInfo.name}")

                # List available tools
                print("\n3. Listing available AWS tools...")
                tools_result = await session.list_tools()
                print(f"   Available tools:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")

                # Test 1: List S3 buckets
                print("\n4. Testing: List S3 buckets...")
                result = await session.call_tool("list_s3_buckets", {})
                print(f"   Result: {result.content[0].text}")

                # Test 2: Get S3 object (optional - update with your bucket/key)
                print("\n5. Testing: Get S3 object (optional)...")
                try:
                    # Uncomment and update these lines with your actual bucket/key
                    # result = await session.call_tool(
                    #     "get_s3_object",
                    #     {
                    #         "bucket": "your-bucket-name",
                    #         "key": "your-file-key"
                    #     }
                    # )
                    # print(f"   Result: {result.content[0].text[:200]}...")
                    print("   Skipped (update bucket/key in code to test)")
                except Exception as e:
                    print(f"   Error: {e}")

                # Test 3: Query DynamoDB (optional - update with your table)
                print("\n6. Testing: Query DynamoDB (optional)...")
                try:
                    # Uncomment and update these lines with your actual table/key
                    # result = await session.call_tool(
                    #     "query_dynamodb",
                    #     {
                    #         "table_name": "your-table-name",
                    #         "key": "id",
                    #         "value": "123"
                    #     }
                    # )
                    # print(f"   Result: {result.content[0].text}")
                    print("   Skipped (update table/key in code to test)")
                except Exception as e:
                    print(f"   Error: {e}")

                print("\n" + "=" * 60)
                print("✓ Demo completed successfully!")
                print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())