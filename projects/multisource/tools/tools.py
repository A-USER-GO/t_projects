from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, List
import httpx, aiohttp, asyncio
from langchain.agents import initialize_agent, AgentType
import xml.etree.ElementTree as ET

from multisource.config import config


class FocusModeToolInput(BaseModel):
    query: str = Field(..., description="用户查询内容")
    max_results: Optional[int] = Field(5, description="最大返回结果数")


class AcademicSearchTool(BaseTool):
    name: str = Field(
        default="academic_search",  # 直接赋值默认值
        description="工具名称",  # 可选描述
        frozen=True  # 可选：禁止修改
    )  # ✅ 显式类型注解
    description: str = "Performs academic paper search via custom API"
    args_schema: Type[BaseModel] = FocusModeToolInput  # 类型注解必须保留

    def _run(self, query: str, max_results: int = 5) -> str:
        """同步调用（占位，实际不可用）"""
        raise NotImplementedError("此工具仅支持异步调用，请使用 _arun 方法")

    async def _arun(self, query: str, max_results: int = 5) -> str:
        """异步调用学术搜索 API"""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params
            )
            xml_data = response

            root = ET.fromstring(xml_data.content)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")

            results = []
            for entry in entries:
                title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
                summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()[:150] + "..."
                link = entry.find("{http://www.w3.org/2005/Atom}id").text
                results.append(f"标题: {title}\n摘要: {summary}\n链接: {link}\n")

            return "\n".join(results) if results else "无相关论文"
            papers = await response.json()["results"]
            return "\n".join([f"{p['title']}: {p['abstract']}" for p in papers])

proxy = "http://127.0.0.1:7897"
key = config.UOU_TO_BE_KEY
class YouTubeSearchTool(BaseTool):
    name: str = Field(
        default="youtube_search",  # 直接赋值默认值
        description="工具名称",  # 可选描述
        frozen=True  # 可选：禁止修改
    )  # ✅ 显式类型注解
    description: str = "Searches YouTube videos based on query"
    args_schema: Type[BaseModel] = FocusModeToolInput  # 类型注解必须保留

    def _run(self, query: str, max_results: int = 5) -> str:
        """同步调用（占位，实际不可用）"""
        raise NotImplementedError("此工具仅支持异步调用，请使用 _arun 方法")

    async def _arun(self, query: str, max_results: int = 5) -> str:
        """调用 YouTube API"""
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "key": key,
            "maxResults": max_results
        }

        # 配置代理和 SSL 设置
        connector = aiohttp.TCPConnector(ssl=False)  # 禁用 SSL 验证（测试用）

        async with aiohttp.ClientSession(
                connector=connector,
                trust_env=True  # 从环境变量读取代理（可选）
        ) as session:
            try:
                async with session.get(
                        url,
                        params=params,
                        proxy=proxy,  # 显式指定代理
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()  # 自动处理 4xx/5xx 错误
                    videos = await response.json()
                    print(videos)
                    videos = videos["items"]
                    for video in videos:
                        caption_text = ""
                        video_id = video.get("id").get("videoId")
                        if video_id:
                            caption_list_url = "https://www.googleapis.com/youtube/v3/captions"
                            caption_list_params = {
                                "part": "snippet",
                                "videoId": video_id,
                                "key": key
                            }

                            async with aiohttp.ClientSession(
                                    connector=aiohttp.TCPConnector(ssl=False),
                                    timeout=aiohttp.ClientTimeout(total=30)
                            ) as session:
                                # 获取字幕列表
                                async with session.get(
                                        caption_list_url,
                                        params=caption_list_params,
                                        proxy=proxy
                                ) as list_res:
                                    list_res.raise_for_status()
                                    caption_data = await list_res.json()

                                # Step 2: 检查目标语言字幕是否存在
                                target_captions = [
                                    c for c in caption_data.get("items", [])
                                ]
                                if target_captions:
                                    caption_id = target_captions[0]["id"]
                                    caption_download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}"
                                    download_params = {
                                        "key": key,
                                        "tfmt": "srt"  # 格式可选：srt, ttml, sbv
                                    }
                                    async with session.get(
                                            caption_download_url,
                                            params=download_params,
                                            proxy=proxy
                                    ) as download_res:
                                        download_res.raise_for_status()
                                        caption_text = await download_res.text()

                    return "\n".join([f"{v['snippet']['title']}: {v['snippet']['description']} : {caption_text}" for v in videos])

            except aiohttp.ClientError as e:
                print(f"网络请求失败: {str(e)}")
                return {"error": str(e)}
            except asyncio.TimeoutError:
                print("请求超时")
                return {"error": "Timeout"}


class FocusModeLoader:
    def __init__(self):
        self.tools = self._load_tools()

    def _load_tools(self) -> List[BaseTool]:
        """从配置文件加载工具（示例）"""
        return [
            AcademicSearchTool(),
            YouTubeSearchTool()
            # 可扩展其他工具...
        ]

    def get_tool_names(self) -> List[str]:
        return [tool.name for tool in self.tools]

    def create_agent(self, llm):
        """创建 LangChain Agent"""
        return initialize_agent(
            self.tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )


