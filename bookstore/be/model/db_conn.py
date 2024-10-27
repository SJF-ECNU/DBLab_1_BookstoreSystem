from pymongo import MongoClient

class DBConn:
    def __init__(self):
        # 连接MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["bookstore"]  # 使用bookstore数据库

    def user_id_exist(self, user_id):
        # 查询user集合中是否存在给定user_id
        user = self.db["user"].find_one({"user_id": user_id})
        if user is None:
            return False
        return True

    def book_id_exist(self, store_id, book_id):
        # 查询store集合中是否存在对应的store_id和book_id
        store = self.db["store"].find_one({"store_id": store_id, "book_id": book_id})
        if store is None:
            return False
        return True

    def store_id_exist(self, store_id):
        # 查询user_store集合中是否存在给定store_id
        user_store = self.db["user_store"].find_one({"store_id": store_id})
        if user_store is None:
            return False
        return True
    
    def order_id_exist(self, order_id):
        # 查询order集合中是否存在给定order_id
        order = self.db["new_order"].find_one({"order_id": order_id})
        if order is None:
            return False
        return True
    
    def order_is_paid(self,order_id):
        # 查询order是否被支付
        order = self.db["new_order"].find_one({"order_id": order_id})
        if order is None:
            return False
        if order['is_paid']==False:
            return False
        return True
    
    def order_is_shipped(self,order_id):
        # 查询order是否被发货
        order = self.db["new_order"].find_one({"order_id": order_id})
        if order is None:
            return False
        if order['is_shipped']==False:
            return False
        return True