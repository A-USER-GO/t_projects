

class Config(object):
    REDIS_URL = "redis://localhost:6379/0"  # 默认配置
    # 这里我使用的是openai的key
    OPEN_API_KEY = ""
    # 这里是googleapis得key
    UOU_TO_BE_KEY = ""


config = Config()