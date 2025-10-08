# client_aws_docs_strands.py
"""
AWS Documentation MCP Client - WITH Strands Framework

This script demonstrates using the Strands framework to interact with the
AWS Documentation MCP server through an AI agent.

Architecture:
    User Question → Strands Agent → LLM → MCP Server → LLM → User Answer

    In this workflow:
    1. User asks a natural language question
    2. Strands Agent manages the conversation
    3. LLM (via Strands) decides which MCP tools to use
    4. MCP tools are called automatically
    5. LLM synthesizes a natural language answer

Key Benefits of Strands:
    - Simplified agent creation and management
    - Automatic tool discovery from MCP server
    - Built-in conversation handling
    - Easy integration with multiple LLM providers
    - Clean, Pythonic API

Available Tools from AWS Documentation MCP:
    - aws___list_regions: Get all AWS regions
    - aws___search_documentation: Search AWS docs with keywords
    - aws___read_documentation: Fetch and convert doc pages to markdown
    - aws___recommend: Get related documentation recommendations
    - aws___get_regional_availability: Check service availability by region

Requirements:
    - Python 3.10+
    - strands package: pip install strands
    - mcp package: pip install mcp
    - Anthropic API key (or other LLM provider)
    - Network access to https://knowledge-mcp.global.api.aws

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python client_aws_docs_strands.py

Author: MCP Testing Suite
Date: 2024
"""

import os
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient


def main():
    """
    Main function demonstrating Strands-powered MCP interaction.

    This creates an AI agent that can intelligently use AWS Documentation
    MCP tools to answer natural language questions.
    """

    print("=" * 70)
    print("AWS Documentation MCP Client - WITH Strands Framework")
    print("Natural Language Questions → Strands Agent → MCP Tools")
    print("=" * 70)

    # Configuration
    server_url = "https://knowledge-mcp.global.api.aws"
    print(f"Server URL: {server_url}")
    #print(f"LLM Model: Claude 3.5 Sonnet (via Anthropic)")

    try:
        # Create MCP client with HTTP transport
        print("\n1. Creating MCP client...")
        aws_docs_mcp = MCPClient(
            transport_callable=lambda: streamablehttp_client(url=server_url)
        )
        print("   ✓ MCP client created")

        # Use the MCP client within a context manager
        print("\n2. Connecting to AWS Documentation MCP server...")
        with aws_docs_mcp:
            print("   ✓ Connected successfully")

            # List available tools
            print("\n3. Discovering available AWS Documentation tools...")
            tools = aws_docs_mcp.list_tools_sync()

            print(f"   ✓ Found {len(tools)} tools:")
            for tool in tools:
                mcp_tool = tool.mcp_tool
                # Get first line of description
                desc_first_line = mcp_tool.description.split('\n')[0].strip()
                print(f"      • {mcp_tool.name}")
                print(f"        {desc_first_line[:80]}...")

            # Create an agent with the MCP tools
            print("\n4. Creating Strands agent with AWS Documentation tools...")
            agent = Agent(
                tools=tools,
                #model="claude-3-5-sonnet-20241022"  # Anthropic model
            )
            print("   ✓ Agent created successfully")

            # ============================================================
            # TEST 1: Simple Question - S3 Bucket Naming Rules
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 1: Ask about S3 bucket naming rules")
            print("=" * 70)
            try:
                question = "What are the S3 bucket naming rules? Give me a concise summary."
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 2: Regional Availability Check
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 2: Check if Lambda is available in a region")
            print("=" * 70)
            try:
                question = "Is AWS Lambda available in the eu-west-1 region?"
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 3: Search Documentation
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 3: Search for VPC documentation")
            print("=" * 70)
            try:
                question = (
                    "Search for documentation about VPC subnets and "
                    "tell me the top 3 most relevant results."
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 4: Get Recommendations
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 4: Get related documentation recommendations")
            print("=" * 70)
            try:
                question = (
                    "What related documentation would you recommend if I'm "
                    "reading about Lambda invocation at "
                    "https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html?"
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 5: List All Regions
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 5: List AWS regions")
            print("=" * 70)
            try:
                question = (
                    "Can you list all AWS regions? Just give me the first 5 "
                    "with their full names."
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 6: Complex Multi-Step Query
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 6: Complex multi-step query")
            print("=" * 70)
            try:
                question = (
                    "I want to deploy a Lambda function in multiple regions. "
                    "First, check if Lambda is available in us-east-1, eu-west-1, "
                    "and ap-southeast-1. Then, search for documentation about "
                    "Lambda deployment best practices."
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 7: Read Specific Documentation
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 7: Read and summarize specific documentation")
            print("=" * 70)
            try:
                question = (
                    "Can you read the S3 bucket naming rules documentation at "
                    "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html "
                    "and give me the 5 most important rules?"
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # TEST 8: Compare Services Across Regions
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST 8: Compare service availability across regions")
            print("=" * 70)
            try:
                question = (
                    "Compare the availability of DynamoDB and Lambda "
                    "in us-east-1 versus eu-central-1."
                )
                print(f"Question: {question}\n")

                response = agent(question)
                print(f"Agent Response:\n{response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            # ============================================================
            # Summary
            # ============================================================
            print("\n" + "=" * 70)
            print("✓ All Tests Complete!")
            print("=" * 70)
            print("\n📊 Summary:")
            print("   • Successfully tested Strands agent with AWS Docs MCP")
            print("   • Agent automatically selected appropriate tools")
            print("   • Natural language queries were converted to MCP calls")
            print("   • Results were synthesized into human-readable answers")
            print("\n💡 Key Takeaways:")
            print("   • Strands simplifies MCP integration")
            print("   • No manual tool calling required")
            print("   • Agent handles complex multi-step queries")
            print("   • Clean, Pythonic API for AI agents")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()