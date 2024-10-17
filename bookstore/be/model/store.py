import logging
import os
import pymongo
import threading
from pymongo import MongoClient
from pymongo import MongoClient
from pymongo.database import Database
class Store:
    database: str
    client: MongoClient
    db: Database

    def __init__(self, db_url="mongodb://localhost:27017/", db_name="bookstore"):
        # 连接 MongoDB 数据库
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.init_collections()

    def init_collections(self):
        try:
            # 初始化 MongoDB 集合
            self.db.create_collection("user")
            self.db.create_collection("user_store")
            self.db.create_collection("store")
            self.db.create_collection("new_order")
            self.db.create_collection("new_order_detail")
            
            # 为一些重要的字段创建索引（类似于 SQL 中的主键）
            self.db.user.create_index([("user_id", pymongo.ASCENDING)], unique=True)
            self.db.user_store.create_index([("user_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)], unique=True)
            self.db.store.create_index([("store_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)], unique=True)
            self.db.new_order.create_index([("order_id", pymongo.ASCENDING)], unique=True)
            self.db.new_order_detail.create_index([("order_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)], unique=True)

        except pymongo.errors.CollectionInvalid as e:
            logging.error(e)

    def get_db_conn(self):
        # 返回 MongoDB 数据库实例
        return self.db

# 全局数据库实例
database_instance: Store = None
# 数据库初始化同步的全局变量
init_completed_event = threading.Event()

def init_database(db_url, db_name):
    global database_instance
    database_instance = Store(db_url, db_name)
    init_completed_event.set()

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()