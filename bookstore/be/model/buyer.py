from pymongo import MongoClient
import uuid
import json
import logging
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        # 连接 MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['bookstore']

    def user_id_exist(self, user_id):
        # 检查 user_id 是否存在
        user = self.db.user.find_one({"user_id": user_id})
        return user is not None

    def store_id_exist(self, store_id):
        # 检查 store_id 是否存在
        store = self.db.store.find_one({"store_id": store_id})
        return store is not None
    
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            
            for book_id, count in id_and_count:
                # 查找书籍库存
                store_item = self.db.store.find_one({"store_id": store_id, "book_id": book_id})
                if store_item is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                
                stock_level = store_item['stock_level']
                book_info = json.loads(store_item['book_info'])
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                # 更新库存
                update_result = self.db.store.update_one(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )
                if update_result.matched_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                # 插入订单详情
                self.db.new_order_detail.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })
            
            # 插入订单
            self.db.new_order.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            })
            order_id = uid
        except Exception as e:
            logging.error(f"530, {str(e)}")
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order = self.db.new_order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            
            buyer_id = order['user_id']
            store_id = order['store_id']

            if buyer_id != user_id:
                return error.error_authorization_fail()

            user = self.db.user.find_one({"user_id": buyer_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()

            seller = self.db.user_store.find_one({"store_id": store_id})
            if seller is None:
                return error.error_non_exist_store_id(store_id)
            
            seller_id = seller['user_id']

            # 计算总价
            order_details = self.db.new_order_detail.find({"order_id": order_id})
            total_price = sum(detail['count'] * detail['price'] for detail in order_details)

            if user['balance'] < total_price:
                return error.error_not_sufficient_funds(order_id)
            
            # 更新买家和卖家的余额
            self.db.user.update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            self.db.user.update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )

            # 删除订单
            self.db.new_order.delete_one({"order_id": order_id})
            self.db.new_order_detail.delete_many({"order_id": order_id})

        except Exception as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user = self.db.user.find_one({"user_id": user_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()

            self.db.user.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
        except Exception as e:
            return 530, "{}".format(str(e))

        return 200, "ok"