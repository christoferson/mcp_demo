# mcp_server_strands.py
import sys
import boto3
from typing import Annotated
from mcp.server.fastmcp import FastMCP

# Add logging to stderr (stdout is used for MCP protocol)
def log(message):
    print(f"[SERVER] {message}", file=sys.stderr, flush=True)

log("Starting AWS MCP Server with FastMCP...")

# Create FastMCP server
mcp = FastMCP("aws-mcp-server")

# Initialize AWS clients with error handling
try:
    log("Initializing AWS clients...")
    s3_client = boto3.client('s3', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    log("AWS clients initialized successfully")
except Exception as e:
    log(f"ERROR initializing AWS clients: {e}")
    sys.exit(1)


@mcp.tool()
def list_s3_buckets() -> str:
    """List all S3 buckets in your AWS account.

    Returns:
        A formatted string containing the count and names of all S3 buckets.
    """
    log("list_s3_buckets called")
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        result = f"S3 Buckets ({len(buckets)}): {', '.join(buckets)}"
        log(f"Successfully listed {len(buckets)} buckets")
        return result
    except Exception as e:
        error_msg = f"Error listing S3 buckets: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


@mcp.tool()
def get_s3_object(
    bucket: Annotated[str, "The name of the S3 bucket"],
    key: Annotated[str, "The key (path) of the object in the bucket"]
) -> str:
    """Get an object from an S3 bucket.

    Args:
        bucket: The name of the S3 bucket
        key: The key (path) of the object in the bucket

    Returns:
        The content of the S3 object as a string, or an error message.
    """
    log(f"get_s3_object called: bucket={bucket}, key={key}")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        log(f"Successfully retrieved object {key} from bucket {bucket}")
        return content
    except Exception as e:
        error_msg = f"Error getting S3 object: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


@mcp.tool()
def put_s3_object(
    bucket: Annotated[str, "The name of the S3 bucket"],
    key: Annotated[str, "The key (path) where the object will be stored"],
    content: Annotated[str, "The content to upload"]
) -> str:
    """Upload content to an S3 bucket.

    Args:
        bucket: The name of the S3 bucket
        key: The key (path) where the object will be stored
        content: The content to upload

    Returns:
        Success message with the S3 URI, or an error message.
    """
    log(f"put_s3_object called: bucket={bucket}, key={key}")
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=content.encode('utf-8'))
        result = f"Successfully uploaded object to s3://{bucket}/{key}"
        log(result)
        return result
    except Exception as e:
        error_msg = f"Error uploading to S3: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


@mcp.tool()
def list_dynamodb_tables() -> str:
    """List all DynamoDB tables in your AWS account.

    Returns:
        A formatted string containing the count and names of all DynamoDB tables.
    """
    log("list_dynamodb_tables called")
    try:
        response = dynamodb_client.list_tables()
        tables = response.get('TableNames', [])
        result = f"DynamoDB Tables ({len(tables)}): {', '.join(tables)}"
        log(f"Successfully listed {len(tables)} tables")
        return result
    except Exception as e:
        error_msg = f"Error listing DynamoDB tables: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


@mcp.tool()
def query_dynamodb(
    table_name: Annotated[str, "The name of the DynamoDB table"],
    key: Annotated[str, "The partition key name"],
    value: Annotated[str, "The partition key value to query"]
) -> str:
    """Query a DynamoDB table by partition key.

    Args:
        table_name: The name of the DynamoDB table
        key: The partition key name
        value: The partition key value to query

    Returns:
        The item found, or a message indicating no item was found, or an error message.
    """
    log(f"query_dynamodb called: table={table_name}, key={key}, value={value}")
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={key: value})
        item = response.get('Item', {})

        if item:
            result = f"Found item: {str(item)}"
            log("Successfully retrieved item")
        else:
            result = f"No item found with {key}={value}"
            log("No item found")

        return result
    except Exception as e:
        error_msg = f"Error querying DynamoDB: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


@mcp.tool()
def put_dynamodb_item(
    table_name: Annotated[str, "The name of the DynamoDB table"],
    item_json: Annotated[str, "JSON string representing the item to put"]
) -> str:
    """Put an item into a DynamoDB table.

    Args:
        table_name: The name of the DynamoDB table
        item_json: JSON string representing the item to put

    Returns:
        Success message, or an error message.
    """
    log(f"put_dynamodb_item called: table={table_name}")
    try:
        import json
        item = json.loads(item_json)
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
        result = f"Successfully put item into {table_name}"
        log(result)
        return result
    except Exception as e:
        error_msg = f"Error putting item to DynamoDB: {str(e)}"
        log(f"ERROR: {error_msg}")
        return error_msg


def main() -> None:
    """Main entry point for the AWS MCP server.

    Initializes AWS clients and starts the FastMCP server with stdio transport.
    """
    log("Starting FastMCP server with stdio transport...")
    try:
        # Run with stdio transport (default for FastMCP)
        mcp.run()
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()