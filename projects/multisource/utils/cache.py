

class MergeCache(object):

    key = "m_c_{keyword}_{optioons}_{num}"

    @classmethod
    async def get(cls, r, k, ps, num):
        return await r.get(cls.key.format(keyword=k, optioons=ps, num=num))

    @classmethod
    async def set(cls, r, k, ps, num, result):
        return await r.set(cls.key.format(keyword=k, optioons=ps, num=num), result, ex=5 * 60)