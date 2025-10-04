# mcp_server_http.py
from mcp.server.fastmcp import FastMCP
import boto3
import os

mcp = FastMCP("AWS MCP Server")

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

# Verify credentials
sts = session.client('sts')
identity = sts.get_caller_identity()
print(f"AWS Account: {identity['Account']}")
print(f"AWS User/Role: {identity['Arn']}")

@mcp.tool()
def list_s3_buckets() -> str:
    """List all S3 buckets"""
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return f"S3 Buckets ({len(buckets)} total):\n" + "\n".join(f"  - {b}" for b in buckets)

@mcp.tool()
def get_s3_object(bucket: str, key: str) -> str:
    """Get an object from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return content
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def query_dynamodb(table_name: str, key: str, value: str) -> str:
    """Query a DynamoDB table"""
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={key: value})
        item = response.get('Item', {})
        return str(item)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Starting AWS MCP Server")
    print("=" * 60)
    print("\nServer will be available at:")
    print("  - http://localhost:3000/mcp (default port)")
    print("\nPress Ctrl+C to stop\n")

    # Run as HTTP server (uses default settings)
    mcp.run(transport="streamable-http")