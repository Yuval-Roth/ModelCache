# -*- coding: utf-8 -*-
import asyncio

from flask import Flask, request
import json
from modelcache.cache import Cache
from modelcache.embedding import EmbeddingModel


async def main():

    # 创建一个Flask实例
    app = Flask(__name__)

    cache,loop = await Cache.init(
        sql_storage="mysql",
        vector_storage="milvus",
        embedding_model=EmbeddingModel.HUGGINGFACE_ALL_MPNET_BASE_V2,
        embedding_workers_num=1
    )

    @app.route('/welcome')
    def first_flask():  # 视图函数
        return 'hello, modelcache!'


    @app.route('/modelcache', methods=['GET', 'POST'])
    def user_backend():
        param_dict = {}
        try:
            if request.method == 'POST':
                param_dict = request.json
            elif request.method == 'GET':
                param_dict = request.args

            result = asyncio.run_coroutine_threadsafe(
                cache.handle_request(param_dict), loop
            ).result()
            return json.dumps(result)
        except Exception as e:
            result = {"errorCode": 101, "errorDesc": str(e), "cacheHit": False, "delta_time": 0, "hit_query": '',
                      "answer": ''}
            cache.save_query_resp(result, model='', query='', delta_time=0)
            return json.dumps(result)

    await asyncio.to_thread(app.run, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    asyncio.run(main())
