from flask import current_app


class ResultCache(object):

    key = "r_c_{key}"

    @classmethod
    def get(cls, question):
        return current_app.redis.get(cls.key.format(key=question))

    @classmethod
    def set(cls, question, result):
        return current_app.redis.set(cls.key.format(key=question), result, ex=5*60)


