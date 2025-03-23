from contextlib import asynccontextmanager
import os

from aioredis import from_url
from fastapi import FastAPI
from langchain_openai import ChatOpenAI

from multisource.aggregation import create_aggregation_chain
from multisource.tools.tools import FocusModeLoader
from config import config
from multisource.utils.current_app import set_global_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建连接池
    app.redis = await from_url(config.REDIS_URL)
    yield
    # 关闭时清理连接
    await app.redis.close()


async def create_app():

    app = FastAPI(lifespan=lifespan)

    os.environ['OPENAI_API_KEY'] = config.OPEN_API_KEY
    os.environ['http_proxy'] = '127.0.0.1:7897'
    os.environ['https_proxy'] = '127.0.0.1:7897'

    app.loader = FocusModeLoader()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    app.aggregation_chain = create_aggregation_chain(llm)
    set_global_app(app)
    return app