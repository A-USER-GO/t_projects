import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR))
from mcp_test import create_mcp_app
from config import config
from routes.tools import register_tools


mcp = create_mcp_app(config)
register_tools(mcp)


if __name__ == "__main__":
    mcp.run()  # 假设 FastMCP 有 run() 方法