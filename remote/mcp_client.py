# client_aws_docs_fixed.py
"""
AWS Documentation MCP Client - DIRECT SERVER TESTING

This script demonstrates DIRECT communication with the AWS Documentation MCP server
without using an LLM as an intermediary.

Architecture:
    Python Client → MCP Server (AWS Documentation)

    This is a direct client-to-server connection where:
    - The client explicitly calls specific MCP tools
    - No LLM is involved in decision-making
    - Useful for testing, debugging, and understanding available tools

Contrast with LLM Integration:
    In a typical MCP workflow, the architecture would be:
    Python Client → LLM (Claude, GPT, etc.) → MCP Server

    Where:
    - User asks natural language questions
    - LLM decides which MCP tools to call
    - LLM interprets results and responds to user
    - This script skips the LLM layer entirely

Use Cases for Direct MCP Testing:
    1. Testing MCP server functionality
    2. Debugging tool parameters and responses
    3. Understanding available tools and their capabilities
    4. Building automation scripts that don't need LLM reasoning
    5. Performance testing and benchmarking

Available Tools in AWS Documentation MCP Server:
    - aws___list_regions: Get all AWS regions
    - aws___search_documentation: Search AWS docs with keywords
    - aws___read_documentation: Fetch and convert doc pages to markdown
    - aws___recommend: Get related documentation recommendations
    - aws___get_regional_availability: Check service availability by region

Requirements:
    - Python 3.10+
    - mcp package: pip install mcp
    - Network access to https://knowledge-mcp.global.api.aws

Usage:
    python client_aws_docs_fixed.py

Author: MCP Testing Suite
Date: 2024
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def print_json_pretty(data: str, max_items: int = None):
    """
    Pretty print JSON data with optional item limiting.

    Args:
        data: JSON string to parse and print
        max_items: Maximum number of items to display (for lists)
    """
    try:
        parsed = json.loads(data)

        # Handle nested content structure
        if isinstance(parsed, dict) and "content" in parsed:
            parsed = parsed["content"]

        if isinstance(parsed, dict) and "result" in parsed:
            result = parsed["result"]

            # If result is a list, optionally limit items
            if isinstance(result, list) and max_items:
                total = len(result)
                result = result[:max_items]
                print(json.dumps(result, indent=2))
                if total > max_items:
                    print(f"\n... (showing {max_items} of {total} items)")
            else:
                print(json.dumps(result, indent=2))
        else:
            print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        # If not JSON, print as-is
        print(data)


async def main():
    """
    Main test function that directly calls AWS Documentation MCP server tools.

    This function:
    1. Establishes connection to the remote MCP server
    2. Initializes a client session
    3. Executes a series of test calls to different MCP tools
    4. Displays results for each tool

    No LLM is involved - all tool calls are explicitly programmed.
    """

    print("=" * 70)
    print("AWS Documentation MCP Client - DIRECT SERVER TESTING")
    print("(No LLM involved - Direct MCP tool calls)")
    print("=" * 70)

    try:
        # Connect to remote AWS Documentation MCP server
        remote_url = "https://knowledge-mcp.global.api.aws"
        print(f"\n1. Connecting to {remote_url}...")

        async with streamablehttp_client(remote_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:

                # Initialize the MCP session
                print("2. Initializing session...")
                init_result = await session.initialize()
                print(f"   ✓ Connected to: {init_result.serverInfo.name}")
                print(f"   ✓ Version: {init_result.serverInfo.version}")

                # List available tools
                print("\n3. Listing available tools...")
                tools_result = await session.list_tools()
                print(f"   ✓ Available tools ({len(tools_result.tools)}):")
                for tool in tools_result.tools:
                    print(f"      • {tool.name}")

                # ============================================================
                # TEST 1: List AWS Regions
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 1: List AWS Regions")
                print("Tool: aws___list_regions")
                print("=" * 70)
                try:
                    result = await session.call_tool("aws___list_regions", {})
                    content = result.content[0].text
                    print("✓ Success - Sample regions:")
                    print_json_pretty(content, max_items=5)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 2: Search Documentation
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 2: Search Documentation")
                print("Tool: aws___search_documentation")
                print("Query: 'S3 bucket naming rules'")
                print("=" * 70)
                try:
                    result = await session.call_tool(
                        "aws___search_documentation",
                        {
                            "search_phrase": "S3 bucket naming rules",
                            "limit": 3
                        }
                    )
                    content = result.content[0].text
                    print("✓ Success - Top 3 results:")
                    print_json_pretty(content)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 3: Read Documentation
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 3: Read Documentation")
                print("Tool: aws___read_documentation")
                print("URL: S3 Bucket Naming Rules")
                print("=" * 70)
                try:
                    result = await session.call_tool(
                        "aws___read_documentation",
                        {
                            "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html",
                            "start_index": 0
                        }
                    )
                    content = result.content[0].text

                    # Parse JSON and extract the actual documentation
                    parsed = json.loads(content)
                    doc_text = parsed.get("content", {}).get("result", "")

                    print(f"✓ Success - Retrieved {len(doc_text)} characters")
                    print("\nFirst 600 characters of documentation:")
                    print("-" * 70)
                    print(doc_text[:600])
                    print("...")
                    print("-" * 70)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 4: Get Recommendations
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 4: Get Recommendations")
                print("Tool: aws___recommend")
                print("URL: S3 Bucket Naming Rules page")
                print("=" * 70)
                try:
                    result = await session.call_tool(
                        "aws___recommend",
                        {
                            "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
                        }
                    )
                    content = result.content[0].text
                    print("✓ Success - Recommended pages:")
                    print_json_pretty(content, max_items=3)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 5: Regional Availability - CloudFormation Resources
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 5: Regional Availability - CloudFormation Resources")
                print("Tool: aws___get_regional_availability")
                print("Resources: Lambda Function, EC2 Instance")
                print("Region: us-east-1")
                print("=" * 70)
                try:
                    result = await session.call_tool(
                        "aws___get_regional_availability",
                        {
                            "resource_type": "cfn",
                            "filters": ["AWS::Lambda::Function", "AWS::EC2::Instance"],
                            "region": "us-east-1"
                        }
                    )
                    content = result.content[0].text
                    print("✓ Success - Availability status:")
                    print_json_pretty(content)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 6: Regional Availability - API Operations (FIXED)
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 6: Regional Availability - API Operations")
                print("Tool: aws___get_regional_availability")
                print("APIs: Lambda CreateFunction, S3 PutObject")
                print("Region: us-west-2")
                print("=" * 70)
                try:
                    # Fixed: Use correct API operation names
                    result = await session.call_tool(
                        "aws___get_regional_availability",
                        {
                            "resource_type": "api",
                            "filters": [
                                "Lambda+CreateFunction",
                                "S3+PutObject"  # Changed from Lambda+InvokeFunction
                            ],
                            "region": "us-west-2"
                        }
                    )
                    content = result.content[0].text
                    print("✓ Success - API availability:")
                    print_json_pretty(content)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 7: Search for Lambda Documentation
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 7: Search for Lambda Function URLs")
                print("Tool: aws___search_documentation")
                print("Query: 'Lambda function URLs'")
                print("=" * 70)
                try:
                    result = await session.call_tool(
                        "aws___search_documentation",
                        {
                            "search_phrase": "Lambda function URLs",
                            "limit": 5
                        }
                    )
                    content = result.content[0].text
                    print("✓ Success - Top 5 results:")
                    print_json_pretty(content)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # ============================================================
                # TEST 8: Multi-Region Availability Check
                # ============================================================
                print("\n" + "=" * 70)
                print("TEST 8: Multi-Region Availability Check")
                print("Tool: aws___get_regional_availability (multiple calls)")
                print("Checking DynamoDB availability across regions")
                print("=" * 70)

                regions_to_check = ["us-east-1", "eu-west-1", "ap-southeast-1"]
                for region in regions_to_check:
                    try:
                        result = await session.call_tool(
                            "aws___get_regional_availability",
                            {
                                "resource_type": "cfn",
                                "filters": ["AWS::DynamoDB::Table"],
                                "region": region
                            }
                        )
                        content = result.content[0].text
                        parsed = json.loads(content)
                        status = parsed.get("content", {}).get("result", {}).get("cfn_resources", {})
                        print(f"   {region}: {status.get('AWS::DynamoDB::Table', 'Unknown')}")
                    except Exception as e:
                        print(f"   {region}: Error - {e}")

                # ============================================================
                # Summary
                # ============================================================
                print("\n" + "=" * 70)
                print("✓ All Tests Complete!")
                print("=" * 70)
                print("\n📊 Summary:")
                print("   • Successfully tested all 5 MCP tools")
                print("   • Demonstrated direct MCP server communication")
                print("   • No LLM was used - all calls were explicit")
                print("\n💡 Next Steps:")
                print("   • Try client_with_llm.py to see LLM-powered interaction")
                print("   • Modify test parameters to explore different queries")
                print("   • Build your own automation using these MCP tools")

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())