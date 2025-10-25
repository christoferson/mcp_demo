# test_server_direct.py
import sys
import os

# Add the server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from mcp_server_strands import mcp

if __name__ == "__main__":
    print("Testing server startup...", file=sys.stderr)
    mcp.run()