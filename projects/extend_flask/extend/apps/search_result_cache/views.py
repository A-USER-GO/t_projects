import logging

from flask import jsonify,request

from extend.apps.search_result_cache import cache_blue

from common.cache.cache_result import ResultCache

log_flask_app = logging.getLogger('flask.app')


@cache_blue.route("/set", methods=["POST"])
def set_cache():
    question = request.get_json().get("question")
    result = request.get_json().get("result")
    if not ResultCache.set(question, result):
        return jsonify(errno=1000, errmsg='设置失败')

    return jsonify(errno=0, errmsg='success')


@cache_blue.route("/get", methods=["GET"])
def get_cache():
    question = request.get_json().get("question")
    result = ResultCache.get(question)
    if result:
        log_flask_app.debug(f"问题：{question} 命中缓存")
    else:
        log_flask_app.debug(f"问题：{question} 未命中缓存")
    return jsonify(errno=0, errmsg='OK', result=result)