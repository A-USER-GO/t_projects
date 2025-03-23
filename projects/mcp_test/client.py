# client.py
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from PIL import Image
from io import BytesIO

# 配置服务器启动参数（指向您的 server.py）
server_params = StdioServerParameters(
    command="python",
    args=["./server.py"],  # 确保路径正确
    env=None
)

async def run(text, save_path):
    print("正在启动客户端...")
    async with stdio_client(server_params) as (read, write):
        print("已连接到服务器")
        async with ClientSession(read, write) as session:
            print("会话已建立")
            # 初始化连接
            await session.initialize()
            print("会话初始化完成")

            # 2. 调用文字转换图片工具 text_convert_images
            result = await session.call_tool(
                "text_convert_images",
                arguments={"text": text}
            )
            r = result.content[0].text.encode('utf-8') if result.content else b''
            print(r)


if __name__ == "__main__":
    text = "一群青年人在爬山"
    save_path = "./output.png"
    asyncio.run(run(text, save_path))