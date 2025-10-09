# mcp_client_strands.py
import sys
import os
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

def main():
    """AWS MCP Client using Strands framework."""

    server_script = os.path.abspath("mcp_server_strands.py")

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

    # Create MCP client with stdio transport
    aws_mcp_client = MCPClient(
        transport_callable=lambda: stdio_client(
            StdioServerParameters(
                command=sys.executable,
                args=[server_script],
                env=env
            )
        )
    )

    print("\n" + "=" * 60)
    print("AWS MCP Client with Strands")
    print("=" * 60)

    try:
        # Use the MCP client within a context manager
        print("\n1. Connecting to AWS MCP server...")
        with aws_mcp_client:
            print("   ✓ Connected successfully")

            # List available tools
            print("\n2. Discovering available AWS tools...")
            tools = aws_mcp_client.list_tools_sync()

            print(f"   Available tools ({len(tools)}):")
            for tool in tools:
                # Access the mcp_tool attribute which contains the Tool object
                mcp_tool = tool.mcp_tool
                # Get first line of description
                desc_first_line = mcp_tool.description.split('\n')[0].strip()
                print(f"   - {mcp_tool.name}: {desc_first_line}")

            # Create an agent with the MCP tools
            print("\n3. Creating Strands agent with AWS tools...")
            agent = Agent(
                tools=tools,
                #model="anthropic.claude-3-5-sonnet-20241022-v2:0"  # Bedrock model
            )
            print("   ✓ Agent created successfully")

            # Test 1: List S3 buckets using natural language
            print("\n4. Testing: List S3 buckets via agent...")
            try:
                response = agent("Can you list all my S3 buckets?")
                print(f"   Agent response:\n   {response}\n")
            except Exception as e:
                print(f"   Error: {e}")

            # Test 2: List DynamoDB tables
            print("\n5. Testing: List DynamoDB tables via agent...")
            try:
                response = agent("Can you list all my DynamoDB tables?")
                print(f"   Agent response:\n   {response}\n")
            except Exception as e:
                print(f"   Error: {e}")

            # Test 3: Get S3 object (optional - update with your bucket/key)
            print("\n6. Testing: Get S3 object via agent (optional)...")
            try:
                # Uncomment and update with your actual bucket/key
                # response = agent(
                #     "Can you get the contents of the file 'your-file-key' "
                #     "from the bucket 'your-bucket-name'?"
                # )
                # print(f"   Agent response:\n   {response}\n")
                print("   Skipped (update bucket/key in code to test)")
            except Exception as e:
                print(f"   Error: {e}")

            # Test 4: Query DynamoDB (optional - update with your table)
            print("\n7. Testing: Query DynamoDB via agent (optional)...")
            try:
                # Uncomment and update with your actual table/key
                # response = agent(
                #     "Can you query the DynamoDB table 'your-table-name' "
                #     "for items where id equals '123'?"
                # )
                # print(f"   Agent response:\n   {response}\n")
                print("   Skipped (update table/key in code to test)")
            except Exception as e:
                print(f"   Error: {e}")

            # Test 5: Complex multi-step query
            print("\n8. Testing: Complex query...")
            try:
                response = agent(
                    "List my S3 buckets and tell me how many I have. "
                    "Also, what AWS services can you help me with?"
                )
                print(f"   Agent response:\n   {response}\n")
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
    main()