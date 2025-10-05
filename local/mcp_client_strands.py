# strands_localhost.py
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# Connect to localhost MCP server
mcp = MCPClient(
    lambda: streamablehttp_client("http://localhost:8000/mcp")
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-east-1",
    temperature=0.3,
)

print("Connecting to localhost MCP server...")

with mcp:
    agent = Agent(
        model=bedrock_model,
        system_prompt="You are a helpful AWS assistant with access to S3 and DynamoDB.",
        tools=mcp.list_tools_sync()
    )

    message = """
    Please help me with the following:

    1. List all my S3 buckets
    2. Tell me how many buckets I have

    Format your output clearly.
    """

    print("\nQuerying agent...\n")
    response = agent(message)
    print(response)