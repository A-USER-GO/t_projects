from flask import Flask
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError
import grpc
from elasticsearch5 import Elasticsearch
# import socketio

# 导入定时任务模块
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

def create_flask_app(config):
    """
    创建Flask应用
    :param config: 配置信息对象
    :return: Flask应用
    """
    app = Flask(__name__)
    app.config.from_object(config)

    return app


def create_app(config):
    """
    创建应用
    :param config: 配置信息对象
    :return: 应用
    """
    app = create_flask_app(config)


    # 限流器
    from utils.limiter import limiter as lmt
    lmt.init_app(app)

    # 配置日志
    from common.utils.logging import create_logger
    create_logger(app)


    # MySQL数据库连接初始化
    # from models import db
    #
    # db.init_app(app)



    # # 添加请求钩子
    # from utils.middlewares import jwt_authentication
    # app.before_request(jwt_authentication)


    # 搜索
    from .apps.search_result_cache import search_bp
    app.register_blueprint(search_bp)

    return app

