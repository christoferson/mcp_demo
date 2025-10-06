# mcp_server_http.py
from mcp.server.fastmcp import FastMCP
import boto3
import os
from typing import Annotated

mcp = FastMCP("AWS MCP Server", port=8000)

# Initialize AWS clients
aws_profile = os.getenv("AWS_PROFILE")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

if aws_profile:
    print(f"Using AWS profile: {aws_profile}")
    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
else:
    print("Using default AWS credentials")
    session = boto3.Session(region_name=aws_region)

s3_client = session.client('s3')
dynamodb = session.resource('dynamodb')
dynamodb_client = session.client('dynamodb')

# Verify credentials
sts = session.client('sts')
identity = sts.get_caller_identity()
print(f"AWS Account: {identity['Account']}")
print(f"AWS User/Role: {identity['Arn']}")


@mcp.tool()
def list_s3_buckets() -> str:
    """List all S3 buckets in your AWS account.

    Returns:
        A formatted string containing the count and names of all S3 buckets.
    """
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return f"S3 Buckets ({len(buckets)} total):\n" + "\n".join(f"  - {b}" for b in buckets)
    except Exception as e:
        return f"Error listing S3 buckets: {str(e)}"


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
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return content
    except Exception as e:
        return f"Error getting S3 object: {str(e)}"


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
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=content.encode('utf-8'))
        return f"Successfully uploaded object to s3://{bucket}/{key}"
    except Exception as e:
        return f"Error uploading to S3: {str(e)}"


@mcp.tool()
def list_dynamodb_tables() -> str:
    """List all DynamoDB tables in your AWS account.

    Returns:
        A formatted string containing the count and names of all DynamoDB tables.
    """
    try:
        response = dynamodb_client.list_tables()
        tables = response.get('TableNames', [])
        return f"DynamoDB Tables ({len(tables)} total):\n" + "\n".join(f"  - {t}" for t in tables)
    except Exception as e:
        return f"Error listing DynamoDB tables: {str(e)}"


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
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={key: value})
        item = response.get('Item', {})

        if item:
            return f"Found item: {str(item)}"
        else:
            return f"No item found with {key}={value}"
    except Exception as e:
        return f"Error querying DynamoDB: {str(e)}"


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
    try:
        import json
        item = json.loads(item_json)
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
        return f"Successfully put item into {table_name}"
    except Exception as e:
        return f"Error putting item to DynamoDB: {str(e)}"


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Starting AWS MCP Server (HTTP)")
    print("=" * 60)
    print(f"\nAWS Configuration:")
    print(f"  Profile: {aws_profile or 'default'}")
    print(f"  Region: {aws_region}")
    print(f"\nServer will be available at:")
    print("  - http://localhost:3000/mcp (default port)")
    print("\nPress Ctrl+C to stop\n")

    # Run as HTTP server with streamable-http transport
    mcp.run(transport="streamable-http")