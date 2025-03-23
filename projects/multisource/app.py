import json
import os
import sys

from aioredis import Redis
from fastapi import Depends
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import asyncio
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR))

from multisource import create_app
from multisource.utils.Depends.redis import get_redis
from multisource.utils.cache import MergeCache


app = asyncio.run(create_app())


class Request(BaseModel):
    query: str
    focus_modes: List[str]
    max_results: int = 5


@app.post("/api/aggregate")
async def aggregate(request: Request, redis: Redis = Depends(get_redis)):
    # 验证模式可用性
    available_modes = app.loader.get_tool_names()
    invalid_modes = [m for m in request.focus_modes if m not in available_modes]
    if invalid_modes:
        return {"error": f"Invalid focus modes: {invalid_modes}"}
    result = await MergeCache.get(redis, request.query, ",".join(request.focus_modes), request.max_results)
    if result:
        return json.loads(result)

    # 并行调用所有工具
    tasks = []
    for tool in app.loader.tools:
        if tool.name in request.focus_modes:
            task = tool.arun(
                {"query": request.query, "max_results": request.max_results}
            )
            tasks.append(task)

    raw_results = await asyncio.gather(*tasks)
    result_dict = dict(zip(request.focus_modes, raw_results))

    # 生成摘要
    summary = app.aggregation_chain.invoke({"raw_results": result_dict})

    result = {
        "query": request.query,
        "sources": request.focus_modes,
        "raw_results": result_dict,
        "summary": summary
    }

    await MergeCache.set(redis, request.query, ",".join(request.focus_modes), request.max_results, json.dumps(result))

    return result


# @app.post("/api/aggregate")
# async def aggregate(query, max_results):
#
#     # 并行调用所有工具
#     tasks = []
#     for tool in loader.tools:
#         task = tool.arun({"query": query, "max_results": max_results})
#         tasks.append(task)
#
#     raw_results = await asyncio.gather(*tasks)
#     print("====================")
#     print(raw_results)
#     print("====================")
#     result_dict = dict(zip([i.name for i in loader.tools], raw_results))
#
#     # 生成摘要
#     summary = aggregation_chain.invoke({"raw_results": result_dict})
#
#     return {
#         "query": query,
#         "sources": loader.tools,
#         "raw_results": result_dict,
#         "summary": summary
#     }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
    # r = asyncio.run(aggregate("机器学习", 2))
    # print(r)