import os

from mcp.server.fastmcp import FastMCP


def create_mcp_app(config):
    print("服务器启动中...")  # 添加日志
    # Create an MCP server
    mcp = FastMCP("mcp")
    print("MCP 实例创建完毕")
    os.environ['OPENAI_API_KEY'] = config.open_api_key

    return mcp