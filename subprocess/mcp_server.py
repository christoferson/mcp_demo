# aws_mcp_server.py
import asyncio
import sys
import boto3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add logging to stderr (stdout is used for MCP protocol)
def log(message):
    print(f"[SERVER] {message}", file=sys.stderr, flush=True)

log("Starting AWS MCP Server...")

app = Server("aws-mcp-server")

# Initialize AWS clients with error handling
try:
    log("Initializing AWS clients...")
    s3_client = boto3.client('s3', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    log("AWS clients initialized successfully")
except Exception as e:
    log(f"ERROR initializing AWS clients: {e}")
    sys.exit(1)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available AWS tools."""
    log("list_tools called")
    return [
        Tool(
            name="list_s3_buckets",
            description="List all S3 buckets",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_s3_object",
            description="Get an object from S3",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string"},
                    "key": {"type": "string"}
                },
                "required": ["bucket", "key"]
            }
        ),
        Tool(
            name="query_dynamodb",
            description="Query a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["table_name", "key", "value"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle AWS tool calls."""
    log(f"call_tool: {name} with {arguments}")

    try:
        if name == "list_s3_buckets":
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            return [
                TextContent(
                    type="text",
                    text=f"S3 Buckets: {', '.join(buckets)}"
                )
            ]

        elif name == "get_s3_object":
            bucket = arguments["bucket"]
            key = arguments["key"]

            try:
                response = s3_client.get_object(Bucket=bucket, Key=key)
                content = response['Body'].read().decode('utf-8')
                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        elif name == "query_dynamodb":
            table_name = arguments["table_name"]
            key = arguments["key"]
            value = arguments["value"]

            try:
                table = dynamodb.Table(table_name)
                response = table.get_item(Key={key: value})
                item = response.get('Item', {})
                return [TextContent(type="text", text=str(item))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        log(f"ERROR in call_tool: {e}")
        raise

async def main():
    """Run the server."""
    try:
        log("Starting stdio server...")
        async with stdio_server() as (read_stream, write_stream):
            log("stdio server started, running app...")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        log(f"ERROR in main: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        log("Running asyncio.run(main())...")
        asyncio.run(main())
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)