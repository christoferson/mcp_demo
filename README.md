# mcp_demo

A Model Context Protocol (MCP) server that exposes AWS services (S3, DynamoDB) as tools for AI agents.

## 🔄 Transport Types: subprocess vs HTTP

### subprocess (stdio Transport)

**How it works:**
- Client spawns server as a subprocess
- Communication via stdin/stdout pipes
- Server process dies when client exits
- No network ports used

**When to use:**
- Quick local testing
- IDE integrations (like Claude Desktop)
- Single client scenarios
- Development without network setup

**Example:**
```python
# Server: mcp_server_stdio.py
from mcp.server import Server
from mcp.server.stdio import stdio_server

async with stdio_server() as (read_stream, write_stream):
    await app.run(read_stream, write_stream, ...)

# Client: mcp_client_stdio.py
from mcp.client.stdio import stdio_client, StdioServerParameters

server_params = StdioServerParameters(
    command=sys.executable,
    args=["mcp_server_stdio.py"],
    env=os.environ.copy()  # Pass AWS credentials
)

async with stdio_client(server_params) as streams:
    async with ClientSession(*streams) as session:
        # Use session

Pros:

✅ Simple setup - no ports to manage
✅ Automatic process lifecycle
✅ Environment variables passed easily
Cons:

❌ Can't test production HTTP setup
❌ Server restarts with each client
❌ Only one client at a time
❌ Can't access from browser/curl
HTTP (localhost Transport)
How it works:

Server runs as independent HTTP process
Client connects via HTTP URL
Server keeps running after client disconnects
Listens on localhost port (e.g., 8000)
When to use:

Testing production deployment locally
Multiple clients connecting
Development with browser tools
Mimicking real-world architecture
Example:

# Server: mcp_server_http.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AWS MCP Server")

@mcp.tool()
def list_s3_buckets() -> str:
    # Implementation

if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # HTTP server on port 3000

# Client: client_localhost.py
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as streams:
    async with ClientSession(*streams) as session:
        # Use session

Pros:

✅ Tests real production setup
✅ Server runs independently
✅ Multiple clients can connect
✅ Can test with curl/browser
✅ Same code for production (just change URL)
Cons:

❌ Need to manage server process manually
❌ Port conflicts possible
❌ More setup steps
Comparison Table
Aspect	subprocess (stdio)	HTTP (localhost)
Server runs	Only when client runs	Independently
Communication	stdin/stdout pipes	HTTP requests
Port	None	3000, 8000, etc.
Multiple clients	No	Yes
Production-like	No	Yes
Setup complexity	Simple	Moderate
Best for	Quick testing, IDE	Production testing
Which Should You Use?
Use subprocess (stdio) when:

🚀 Getting started quickly
🔧 Developing/debugging tools
📝 Testing in IDEs
🎯 Single client use case
Use HTTP (localhost) when:

🌐 Preparing for production
🔄 Testing with multiple clients
🐛 Debugging HTTP issues
📊 Using browser dev tools
🚀 Before deploying to cloud
Typical workflow:

Start with subprocess for rapid development
Switch to HTTP localhost to test production setup
Deploy HTTP remote to cloud for production

----



Transport Types
Name	Transport	How it runs	Use case
stdio	stdin/stdout	Spawned as subprocess by client	Local development, IDE integration
HTTP (localhost)	HTTP on 127.0.0.1	Independent process, HTTP server	Testing production setup locally
HTTP (remote)	HTTP on public URL	Deployed to cloud/server	Production, sharing with others

🔧 Installation
pip install mcp boto3 strands strands-tools
aws configure  # Set up AWS credentials


🚀 Quick Start
Terminal 1 - Start Server:
cd mcp_demo/local
export AWS_PROFILE=your-profile-name  # Optional
python mcp_server_http.py
Server runs at http://localhost:8000/mcp

Terminal 2 - Run Client:
cd mcp_demo/local
python client_localhost.py


# Server Side (FastMCP)
```(python)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AWS MCP Server")

@mcp.tool()
def list_s3_buckets() -> str:
    """List all S3 buckets"""
    # Tool implementation
    return result

# Run as HTTP server
mcp.run(transport="streamable-http")
```

Key APIs:
FastMCP(name) - Create MCP server instance
@mcp.tool() - Decorator to register tools
mcp.run(transport="streamable-http") - Start HTTP server

----


# Client Side (Direct MCP Client)
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as streams:
    async with ClientSession(*streams) as session:
        # Initialize connection
        await session.initialize()

        # List available tools
        tools = await session.list_tools()

        # Call a tool
        result = await session.call_tool("list_s3_buckets", {})

Key APIs:

streamablehttp_client(url) - Connect to HTTP MCP server
ClientSession(*streams) - Create MCP session
session.initialize() - Initialize MCP connection
session.list_tools() - Get available tools
session.call_tool(name, args) - Execute a tool


---

# Client Side (Strands Integration)
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# Create MCP client
mcp = MCPClient(
    lambda: streamablehttp_client("http://localhost:8000/mcp")
)

# Use with Strands Agent
with mcp:
    agent = Agent(
        model=bedrock_model,
        tools=mcp.list_tools_sync()
    )
    response = agent("List my S3 buckets")

Key APIs:

MCPClient(connection_factory) - Strands MCP client wrapper
mcp.list_tools_sync() - Get tools for Strands agent
Use within with mcp: context manager

---

🔄 Transport Types
stdio (Development)
# Server spawned as subprocess
from mcp.client.stdio import stdio_client, StdioServerParameters

server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
    env=os.environ.copy()  # Pass environment variables
)

async with stdio_client(server_params) as streams:
    async with ClientSession(*streams) as session:
        # Use session

Use when: Local development, testing, single machine

streamable-http (Production)
# Server runs independently via HTTP
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as streams:
    async with ClientSession(*streams) as session:
        # Use session

Use when: Production, remote servers, multiple clients


---

🛠️ Available Tools
Tool	Parameters	Description
list_s3_buckets	None	List all S3 buckets
get_s3_object	bucket, key	Get S3 object content
query_dynamodb	table_name, key, value	Query DynamoDB by primary key
🔑 Key Concepts
Why Two Processes?
MCP uses a client-server architecture:

Server: Exposes tools via MCP protocol
Client: Connects and calls tools
Benefits:

Server runs independently
Multiple clients can connect
Same code for local/remote
Easy to deploy to production

Environment Variables
Server inherits environment from client when using stdio:

# Client passes environment to server
env = os.environ.copy()
env["AWS_PROFILE"] = "my-profile"

server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
    env=env  # ← Important: Pass environment
)

For HTTP servers, set environment before starting:

export AWS_PROFILE=my-profile
python mcp_server_http.py

🐛 Common Issues
Connection closed error:

Server crashed on startup
Check AWS credentials: aws sts get-caller-identity
Check server logs in stderr
Too many values to unpack:

# Wrong:
async with streamablehttp_client(url) as (read, write):

# Correct:
async with streamablehttp_client(url) as streams:
    async with ClientSession(*streams) as session:

Port already in use:

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows


--



https://modelcontextprotocol.io/
https://github.com/jlowin/fastmcp
https://github.com/modelcontextprotocol/python-sdk
https://github.com/modelcontextprotocol/python-sdk
https://www.youtube.com/watch?v=bHSbjCZZFjE&list=PL5bUlblGfe0K0uUGD3-AToBcOOLIqSWBs&index=3