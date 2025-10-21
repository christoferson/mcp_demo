# client_multi_mcp_bedrock.py
"""
Multi-MCP Server Client with Strands Framework + AWS Bedrock

This script demonstrates using multiple remote MCP servers simultaneously
through the Strands framework with AWS Bedrock as the LLM provider.

Architecture:
    User Question → Strands Agent → AWS Bedrock → Multiple MCP Servers → Answer

Supported Remote MCP Servers:
    1. AWS Knowledge - AWS documentation and best practices
    2. Add more remote HTTP MCP servers as they become available

Key Features:
    - Multi-server agent with unified interface
    - AWS Bedrock integration (Claude via Bedrock)
    - Automatic tool discovery from all servers
    - Intelligent routing to appropriate server
    - Clean error handling per server

Requirements:
    - Python 3.10+
    - strands: pip install strands
    - mcp: pip install mcp
    - boto3: pip install boto3
    - AWS credentials configured (AWS_PROFILE environment variable)

Usage:
    export AWS_PROFILE=your_profile_name
    python client_multi_mcp_bedrock.py

Author: MCP Multi-Server Suite
Date: 2024
"""

import os
from typing import Dict, List
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient


# ============================================================
# MCP Server Configuration
# ============================================================

MCP_SERVERS = {
    "aws-knowledge": {
        "url": "https://knowledge-mcp.global.api.aws",
        "description": "AWS documentation, APIs, and best practices",
        "enabled": True
    },
    # Add more remote servers as they become available
    # "wikipedia": {
    #     "url": "https://mcp.wikipedia.org",
    #     "description": "Wikipedia encyclopedia knowledge",
    #     "enabled": False
    # },
    # "your-custom-server": {
    #     "url": "https://your-mcp-server.com",
    #     "description": "Your custom knowledge base",
    #     "enabled": False
    # },
}


# ============================================================
# AWS Bedrock Configuration
# ============================================================

BEDROCK_CONFIG = {
    # Claude 3.5 Sonnet via Bedrock
    "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",

    # Alternative Bedrock models:
    # "model": "anthropic.claude-3-sonnet-20240229-v1:0",
    # "model": "anthropic.claude-3-haiku-20240307-v1:0",
    # "model": "anthropic.claude-3-opus-20240229-v1:0",

    "region": os.getenv("AWS_REGION", "us-east-1"),
    "profile": os.getenv("AWS_PROFILE"),
}


class MultiMCPAgent:
    """
    Manages multiple MCP servers and creates a unified Strands agent.
    """

    def __init__(self, server_configs: Dict[str, Dict], bedrock_config: Dict):
        """
        Initialize multi-MCP agent with Bedrock.

        Args:
            server_configs: Dictionary of MCP server configurations
            bedrock_config: AWS Bedrock configuration
        """
        self.server_configs = server_configs
        self.bedrock_config = bedrock_config
        self.mcp_clients = {}
        self.all_tools = []
        self.agent = None

    def connect_servers(self):
        """Connect to all enabled MCP servers and collect tools."""
        print("\n" + "=" * 70)
        print("CONNECTING TO MCP SERVERS")
        print("=" * 70)

        for server_name, config in self.server_configs.items():
            if not config.get("enabled", True):
                print(f"\n⊘ Skipping {server_name} (disabled)")
                continue

            try:
                print(f"\n📡 Connecting to {server_name}...")
                print(f"   URL: {config['url']}")
                print(f"   Description: {config['description']}")

                # Create MCP client
                mcp_client = MCPClient(
                    transport_callable=lambda url=config['url']: streamablehttp_client(url=url)
                )

                # Store client
                self.mcp_clients[server_name] = {
                    "client": mcp_client,
                    "config": config
                }

                print(f"   ✓ Connected to {server_name}")

            except Exception as e:
                print(f"   ❌ Failed to connect to {server_name}: {e}")
                continue

    def discover_tools(self):
        """Discover tools from all connected servers."""
        print("\n" + "=" * 70)
        print("DISCOVERING TOOLS FROM ALL SERVERS")
        print("=" * 70)

        for server_name, client_info in self.mcp_clients.items():
            try:
                print(f"\n🔍 Discovering tools from {server_name}...")

                with client_info["client"] as mcp_client:
                    tools = mcp_client.list_tools_sync()

                    print(f"   ✓ Found {len(tools)} tools:")
                    for tool in tools:
                        mcp_tool = tool.mcp_tool
                        desc_first_line = mcp_tool.description.split('\n')[0].strip()
                        print(f"      • {mcp_tool.name}")
                        print(f"        {desc_first_line[:70]}...")

                    self.all_tools.extend(tools)

            except Exception as e:
                print(f"   ❌ Failed to discover tools from {server_name}: {e}")
                continue

        print(f"\n📊 Total tools available: {len(self.all_tools)}")

    def create_agent(self):
        """Create Strands agent with all discovered tools and Bedrock."""
        print("\n" + "=" * 70)
        print("CREATING UNIFIED STRANDS AGENT WITH AWS BEDROCK")
        print("=" * 70)

        if not self.all_tools:
            raise ValueError("No tools available. Connect to servers first.")

        print(f"🤖 LLM Provider: AWS Bedrock")
        print(f"   Model: {self.bedrock_config['model']}")
        print(f"   Region: {self.bedrock_config['region']}")
        print(f"   Profile: {self.bedrock_config['profile']}")

        # Create agent with Bedrock model
        self.agent = Agent(
            tools=self.all_tools,
            #model=self.bedrock_config['model'], #Use default Bedrock model 
        )

        print(f"\n✓ Agent created with {len(self.all_tools)} tools from {len(self.mcp_clients)} servers")

    def query(self, question: str) -> str:
        """
        Query the agent with a natural language question.

        Args:
            question: Natural language question

        Returns:
            Agent's response
        """
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")

        # Execute query with MCP clients in context
        for server_name, client_info in self.mcp_clients.items():
            with client_info["client"]:
                return self.agent(question)


def run_comprehensive_tests():
    """Run comprehensive tests across multiple MCP servers with Bedrock."""

    print("=" * 70)
    print("MULTI-MCP SERVER CLIENT WITH AWS BEDROCK")
    print("Unified Agent → AWS Bedrock → Multiple Knowledge Sources")
    print("=" * 70)

    # Verify AWS credentials
    aws_profile = os.getenv("AWS_PROFILE")
    if not aws_profile:
        print("\n⚠️  WARNING: AWS_PROFILE not set. Using default AWS credentials.")
    else:
        print(f"\n✓ Using AWS Profile: {aws_profile}")

    # Initialize multi-MCP agent with Bedrock
    multi_agent = MultiMCPAgent(MCP_SERVERS, BEDROCK_CONFIG)

    # Connect to all servers
    multi_agent.connect_servers()

    if not multi_agent.mcp_clients:
        print("\n❌ No servers connected. Exiting.")
        return

    # Discover tools from all servers
    multi_agent.discover_tools()

    # Create unified agent with Bedrock
    multi_agent.create_agent()

    # ============================================================
    # TEST SUITE
    # ============================================================

    tests = [
        {
            "name": "AWS S3 Bucket Naming Rules",
            "question": "What are the AWS S3 bucket naming rules? Give me the top 5 most important rules.",
            "category": "AWS Documentation"
        },
        {
            "name": "AWS Lambda Regional Availability",
            "question": "Is AWS Lambda available in the eu-west-1 region? Provide details.",
            "category": "AWS Regional Services"
        },
        # {
        #     "name": "AWS VPC Subnets Documentation",
        #     "question": "Search for AWS documentation about VPC subnets and summarize the key concepts.",
        #     "category": "AWS Networking"
        # },
        # {
        #     "name": "AWS Regions Overview",
        #     "question": "List the first 5 AWS regions with their full names and locations.",
        #     "category": "AWS Infrastructure"
        # },
        # {
        #     "name": "DynamoDB Best Practices",
        #     "question": "What are the best practices for AWS DynamoDB table design? Give me 5 key recommendations.",
        #     "category": "AWS Database"
        # },
        # {
        #     "name": "CloudFormation Regional Availability",
        #     "question": "Check if AWS CloudFormation is available in ap-southeast-1 region.",
        #     "category": "AWS Infrastructure as Code"
        # },
        # {
        #     "name": "Multi-Region Architecture",
        #     "question": "Search for AWS documentation about multi-region architecture patterns and summarize the main approaches.",
        #     "category": "AWS Architecture"
        # },
        # {
        #     "name": "IAM Policy Best Practices",
        #     "question": "Find documentation about AWS IAM policy best practices and give me 3 key security recommendations.",
        #     "category": "AWS Security"
        # },
        # {
        #     "name": "EC2 Instance Types",
        #     "question": "Search for documentation about EC2 instance types and explain the difference between T3 and M5 instances.",
        #     "category": "AWS Compute"
        # },
        # {
        #     "name": "RDS Multi-AZ Deployment",
        #     "question": "What is AWS RDS Multi-AZ deployment? Search the documentation and explain the benefits.",
        #     "category": "AWS Database"
        # },
        # {
        #     "name": "ECS vs EKS Comparison",
        #     "question": "Search for documentation comparing AWS ECS and EKS. What are the main differences?",
        #     "category": "AWS Containers"
        # },
        # {
        #     "name": "S3 Storage Classes",
        #     "question": "What are the different AWS S3 storage classes? Search documentation and list them with use cases.",
        #     "category": "AWS Storage"
        # },
        # {
        #     "name": "API Gateway Best Practices",
        #     "question": "Find AWS API Gateway best practices documentation and give me 5 key recommendations.",
        #     "category": "AWS API Management"
        # },
        # {
        #     "name": "CloudWatch Monitoring",
        #     "question": "Search for AWS CloudWatch monitoring best practices and summarize the key metrics to monitor.",
        #     "category": "AWS Monitoring"
        # },
        # {
        #     "name": "Step Functions Use Cases",
        #     "question": "What are common use cases for AWS Step Functions? Search the documentation.",
        #     "category": "AWS Orchestration"
        # },
    ]

    # Run all tests
    successful_tests = 0
    failed_tests = 0

    for i, test in enumerate(tests, 1):
        print("\n" + "=" * 70)
        print(f"TEST {i}/{len(tests)}: {test['name']}")
        print("=" * 70)
        print(f"Category: {test['category']}")
        print(f"Question: {test['question']}\n")

        try:
            response = multi_agent.query(test['question'])
            print(f"🤖 Bedrock Response:\n{response}\n")
            print("✓ Test completed successfully")
            successful_tests += 1

        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed_tests += 1
            import traceback
            traceback.print_exc()

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("✓ ALL TESTS COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   • Connected servers: {len(multi_agent.mcp_clients)}")
    print(f"   • Total tools available: {len(multi_agent.all_tools)}")
    print(f"   • Tests executed: {len(tests)}")
    print(f"   • Successful: {successful_tests}")
    print(f"   • Failed: {failed_tests}")
    print(f"   • Success rate: {(successful_tests/len(tests)*100):.1f}%")
    print(f"\n🤖 LLM Provider:")
    print(f"   • Provider: AWS Bedrock")
    print(f"   • Model: {BEDROCK_CONFIG['model']}")
    print(f"   • Region: {BEDROCK_CONFIG['region']}")
    print(f"   • Profile: {BEDROCK_CONFIG['profile']}")
    print("\n💡 Key Features Demonstrated:")
    print("   • Multi-server MCP integration")
    print("   • AWS Bedrock LLM integration")
    print("   • Unified agent interface")
    print("   • Automatic tool routing")
    print("   • Natural language queries")
    print("   • Robust error handling")


def main():
    """Main entry point."""
    run_comprehensive_tests()


if __name__ == "__main__":
    main()