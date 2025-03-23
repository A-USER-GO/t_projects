from mcp_test.utils.tools import text_convert_images_tool


def register_tools(mcp):
    # 这里应该有别的注册方式，暂未研究
    @mcp.tool()
    def text_convert_images(text: str) -> bytes:
        """Convert text into images"""
        return text_convert_images_tool(text)

    print("tools 注册完毕")