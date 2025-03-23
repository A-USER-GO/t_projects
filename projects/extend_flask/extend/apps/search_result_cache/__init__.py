from flask import Blueprint

cache_blue = Blueprint("cache_blue", __name__, url_prefix=Config.URL_PREFIX + '/cache')
from . import views