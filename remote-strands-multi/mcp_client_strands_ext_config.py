# client_multi_mcp_bedrock.py
"""
Multi-MCP Server Client with Strands Framework + AWS Bedrock
Using BedrockModel for proper parameter support
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient


# ============================================================
# Default Configuration (used if no config file found)
# ============================================================

DEFAULT_MCP_SERVERS = {
    "aws-knowledge": {
        "url": "https://knowledge-mcp.global.api.aws",
        "description": "AWS documentation, APIs, and best practices",
        "enabled": True
    },
}

DEFAULT_BEDROCK_CONFIG = {
    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "region_name": "us-east-1",
    "temperature": 0.7,
    "max_tokens": 4096,
}


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file. If None, looks for mcp_bedrock_config.json

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = "mcp_bedrock_config.json"

    config_file = Path(config_path)

    if not config_file.exists():
        print(f"⚠️  Config file not found: {config_path}")
        print(f"   Using default configuration")
        return {
            "mcp_servers": DEFAULT_MCP_SERVERS,
            "bedrock": DEFAULT_BEDROCK_CONFIG
        }

    try:
        print(f"📄 Loading configuration from: {config_path}")
        with open(config_file, 'r') as f:
            config = json.load(f)

        if "mcp_servers" not in config:
            raise ValueError("Config missing 'mcp_servers' key")
        if "bedrock" not in config:
            raise ValueError("Config missing 'bedrock' key")

        print(f"   ✓ Configuration loaded successfully")
        return config

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        print(f"   Using default configuration")
        return {
            "mcp_servers": DEFAULT_MCP_SERVERS,
            "bedrock": DEFAULT_BEDROCK_CONFIG
        }
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        print(f"   Using default configuration")
        return {
            "mcp_servers": DEFAULT_MCP_SERVERS,
            "bedrock": DEFAULT_BEDROCK_CONFIG
        }


def merge_config_with_env(config: Dict) -> Dict:
    """
    Merge configuration with environment variables.
    Environment variables take precedence.

    Args:
        config: Configuration dictionary

    Returns:
        Merged configuration
    """
    bedrock_config = config.get("bedrock", {})

    if os.getenv("AWS_REGION"):
        bedrock_config["region_name"] = os.getenv("AWS_REGION")

    if os.getenv("BEDROCK_MODEL"):
        bedrock_config["model_id"] = os.getenv("BEDROCK_MODEL")

    if os.getenv("AWS_PROFILE"):
        bedrock_config["profile_name"] = os.getenv("AWS_PROFILE")

    config["bedrock"] = bedrock_config
    return config


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

                mcp_client = MCPClient(
                    transport_callable=lambda url=config['url']: streamablehttp_client(url=url)
                )

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

        # Create BedrockModel with all parameters
        bedrock_model_kwargs = {
            #"model_id": self.bedrock_config["model_id"],
            "region_name": self.bedrock_config.get("region_name", "us-east-1"),
        }

        # Add optional parameters
        if "temperature" in self.bedrock_config:
            bedrock_model_kwargs["temperature"] = self.bedrock_config["temperature"]
        if "max_tokens" in self.bedrock_config:
            bedrock_model_kwargs["max_tokens"] = self.bedrock_config["max_tokens"]
        if "profile_name" in self.bedrock_config:
            bedrock_model_kwargs["profile_name"] = self.bedrock_config["profile_name"]

        print(f"🤖 LLM Provider: AWS Bedrock")
        #print(f"   Model ID: {bedrock_model_kwargs['model_id']}")
        print(f"   Region: {bedrock_model_kwargs['region_name']}")
        print(f"   Profile: {bedrock_model_kwargs.get('profile_name', 'default')}")
        print(f"   Temperature: {bedrock_model_kwargs.get('temperature', 'default')}")
        print(f"   Max Tokens: {bedrock_model_kwargs.get('max_tokens', 'default')}")

        # Create BedrockModel instance
        bedrock_model = BedrockModel(**bedrock_model_kwargs)

        # Create agent with BedrockModel and tools
        self.agent = Agent(
            model=bedrock_model,
            tools=self.all_tools,
            system_prompt="You are a helpful AWS expert assistant with access to AWS documentation and knowledge."
        )

        print(f"\n✓ Agent created with {len(self.all_tools)} tools from {len(self.mcp_clients)} servers")
        print(f"✓ Model configuration: {self.agent.model.config}")

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

        for server_name, client_info in self.mcp_clients.items():
            with client_info["client"]:
                return self.agent(question)


def print_config_summary(config: Dict):
    """Print configuration summary."""
    print("\n" + "=" * 70)
    print("CONFIGURATION SUMMARY")
    print("=" * 70)

    print("\n📡 MCP Servers:")
    for server_name, server_config in config["mcp_servers"].items():
        status = "✓ Enabled" if server_config.get("enabled", True) else "⊘ Disabled"
        print(f"   • {server_name}: {status}")
        print(f"     URL: {server_config['url']}")
        print(f"     Description: {server_config['description']}")

    print("\n🤖 AWS Bedrock Configuration:")
    bedrock = config["bedrock"]
    print(f"   • Model ID: {bedrock['model_id']}")
    print(f"   • Region: {bedrock.get('region_name', 'us-east-1')}")
    print(f"   • Profile: {bedrock.get('profile_name', 'default')}")
    print(f"   • Temperature: {bedrock.get('temperature', 0.7)}")
    print(f"   • Max Tokens: {bedrock.get('max_tokens', 4096)}")


def run_comprehensive_tests(config_path: Optional[str] = None):
    """Run comprehensive tests across multiple MCP servers with Bedrock."""

    print("=" * 70)
    print("MULTI-MCP SERVER CLIENT WITH AWS BEDROCK")
    print("Unified Agent → AWS Bedrock → Multiple Knowledge Sources")
    print("=" * 70)

    config = load_config(config_path)
    config = merge_config_with_env(config)

    print_config_summary(config)

    aws_profile = config["bedrock"].get("profile_name") or os.getenv("AWS_PROFILE")
    if not aws_profile:
        print("\n⚠️  WARNING: AWS_PROFILE not set. Using default AWS credentials.")
    else:
        print(f"\n✓ Using AWS Profile: {aws_profile}")

    multi_agent = MultiMCPAgent(
        config["mcp_servers"],
        config["bedrock"]
    )

    multi_agent.connect_servers()

    if not multi_agent.mcp_clients:
        print("\n❌ No servers connected. Exiting.")
        return

    multi_agent.discover_tools()
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
        # {
        #     "name": "AWS Lambda Regional Availability",
        #     "question": "Is AWS Lambda available in the eu-west-1 region? Provide details.",
        #     "category": "AWS Regional Services"
        # },
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
    ]

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
    print(f"   • Model: {config['bedrock']['model_id']}")
    print(f"   • Region: {config['bedrock'].get('region_name', 'us-east-1')}")
    print(f"   • Profile: {config['bedrock'].get('profile_name', 'default')}")


def main():
    """Main entry point."""
    import sys

    config_path = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config" and len(sys.argv) > 2:
            config_path = sys.argv[2]
        elif sys.argv[1] not in ["--help", "-h"]:
            config_path = sys.argv[1]

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python client_multi_mcp_bedrock.py [--config CONFIG_FILE]")
        print("\nOptions:")
        print("  --config FILE    Path to configuration file (default: mcp_bedrock_config.json)")
        print("\nEnvironment Variables:")
        print("  AWS_PROFILE      AWS profile to use")
        print("  AWS_REGION       AWS region (default: us-east-1)")
        print("  BEDROCK_MODEL    Bedrock model ID (overrides config)")
        return

    run_comprehensive_tests(config_path)


if __name__ == "__main__":
    main()