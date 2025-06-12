# -*- coding: utf-8 -*-
import json
from typing import List
from modelcache.manager.scalar_data.base import ScalarStorage, CacheData
import sqlite3


class SQLStorage(ScalarStorage):
    def __init__(
        self,
        db_type: str = "mysql",
        config=None,
        url="./sqlite.db"
    ):
        self._url = url
        self.create()

    def create(self):
        # answer_table_sql = """CREATE TABLE IF NOT EXISTS modelcache_llm_answer (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         gmt_create TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #         gmt_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #         question TEXT NOT NULL,
        #         answer TEXT NOT NULL,
        #         answer_type INTEGER NOT NULL,
        #         hit_count INTEGER NOT NULL DEFAULT 0,
        #         model VARCHAR(1000) NOT NULL,
        #         embedding_data BLOB NOT NULL
        #         );
        #         """

        answer_table_sql = """CREATE TABLE IF NOT EXISTS `open_cache_mm_answer` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `gmt_create` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `gmt_modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `question_text` TEXT NOT NULL,
  `image_url` VARCHAR(2048) NOT NULL,
  `answer` TEXT NOT NULL,
  `answer_type` INTEGER NOT NULL,
  `hit_count` INTEGER NOT NULL DEFAULT 0,
  `model` VARCHAR(1000) NOT NULL,
  `image_raw` BLOB DEFAULT NULL,
  `image_id` VARCHAR(1000) DEFAULT NULL
);
 """

        log_table_sql = """CREATE TABLE IF NOT EXISTS modelcache_query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gmt_create TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                gmt_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_code INTEGER NOT NULL,
                error_desc VARCHAR(1000) NOT NULL,
                cache_hit VARCHAR(100) NOT NULL,
                delta_time REAL NOT NULL,
                model VARCHAR(1000) NOT NULL,
                query TEXT NOT NULL,
                hit_query TEXT NOT NULL,
                answer TEXT NOT NULL
                );
                """

        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            cursor.execute(answer_table_sql)
            cursor.execute(log_table_sql)
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            conn.close()

    def _insert(self, data: List):
        answer = data[0]
        text = data[1]
        image_url = data[2]
        image_id = data[3]
        model = data[4]
        answer_type = 0

        table_name = "open_cache_mm_answer"
        insert_sql = "INSERT INTO {} (question_text, image_url, image_id, answer, answer_type, model) VALUES (?, ?, ?, ?, ?, ?)".format(table_name)

        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            values = (text, image_url, image_id, answer, answer_type, model)
            cursor.execute(insert_sql, values)
            conn.commit()
            id = cursor.lastrowid
            cursor.close()
            conn.close()
        finally:
            conn.close()
        return id

    def batch_insert(self, all_data: List[CacheData]):
        ids = []
        for data in all_data:
            ids.append(self._insert(data))
        return ids

    def insert_query_resp(self, query_resp, **kwargs):
        error_code = query_resp.get('errorCode')
        error_desc = query_resp.get('errorDesc')
        cache_hit = query_resp.get('cacheHit')
        model = kwargs.get('model')
        query = kwargs.get('query')
        delta_time = kwargs.get('delta_time')
        hit_query = query_resp.get('hit_query')
        answer = query_resp.get('answer')

        if isinstance(hit_query, list):
            hit_query = json.dumps(hit_query, ensure_ascii=False)

        table_name = "modelcache_query_log"
        insert_sql = "INSERT INTO {} (error_code, error_desc, cache_hit, model, query, delta_time, hit_query, answer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(table_name)

        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            values = (error_code, error_desc, cache_hit, model, query, delta_time, hit_query, answer)
            cursor.execute(insert_sql, values)
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            conn.close()

    def get_data_by_id(self, key: int):
        table_name = "open_cache_mm_answer"
        query_sql = "select question, answer, embedding_data, model from {} where id={}".format(table_name, key)
        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            cursor.execute(query_sql)
            resp = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            conn.close()

        if resp is not None and len(resp) == 4:
            return resp
        else:
            return None

    def update_hit_count_by_id(self, primary_id: int):
        table_name = "open_cache_mm_answer"
        update_sql = "UPDATE {} SET hit_count = hit_count+1 WHERE id={}".format(table_name, primary_id)

        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            cursor.execute(update_sql)
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            # 关闭连接，将连接返回给连接池
            conn.close()

    def get_ids(self, deleted=True):
        pass

    def mark_deleted(self, keys):
        table_name = "open_cache_mm_answer"
        delete_sql = "Delete from {} WHERE id in ({})".format(table_name, ",".join([str(i) for i in keys]))
        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            cursor.execute(delete_sql)
            delete_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            conn.close()
        return delete_count

    def model_deleted(self, model_name):
        table_name = "open_cache_mm_answer"
        delete_sql = "Delete from {} WHERE model='{}'".format(table_name, model_name)
        conn = sqlite3.connect(self._url)
        try:
            cursor = conn.cursor()
            resp = cursor.execute(delete_sql)
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            conn.close()
        return resp

    def clear_deleted_data(self):
        pass

    def count(self, state: int = 0, is_all: bool = False):
        pass

    def close(self):
        pass

    def count_answers(self):
        pass
