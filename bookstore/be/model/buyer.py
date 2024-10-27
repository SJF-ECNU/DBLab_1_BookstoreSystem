from pymongo import MongoClient
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from datetime import datetime, timedelta
import schedule
import time

class Buyer(db_conn.DBConn):
    # 订单状态映射
    ORDER_STATUS = {
        "pending": "待支付",
        "paid": "已支付",
        "shipped": "已发货",
        "received": "已收货",
        "completed": "已完成",
        "canceled": "已取消"
    }
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
    
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str): # type: ignore
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            # 生成订单ID
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            
            # 遍历每本书籍及其数量
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
            
            # 插入订单，新增 is_shipped 和 is_received 初始为 False
            self.db.new_order.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "is_paid": False,  # 是否支付
                "is_shipped": False,  # 是否发货
                "is_received": False,  # 是否收货
                "order_completed": False,  # 订单是否完成
                "status": "pending",  # 订单状态
                "created_time": datetime.utcnow()  # 使用 UTC 时间，订单创建时间，用于订单超时处理
            })
            order_id = uid
        except Exception as e:# pragma: no cover
            logging.error(f"530, {str(e)}")
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def pay_to_platform(self, user_id: str, password: str, order_id: str) -> (int, str): # type: ignore
        try:
            # 查找订单
            order = self.db.new_order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order['user_id']

            # 检查用户身份
            if buyer_id != user_id:
                return error.error_authorization_fail()

            user = self.db.user.find_one({"user_id": buyer_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()
                

            # 检查是否已经付款
            if order.get('is_paid', False):
                return 400, "Order has already been paid."

            # 计算订单总价
            order_details = self.db.new_order_detail.find({"order_id": order_id})
            total_price = sum(detail['count'] * detail['price'] for detail in order_details)

            if user['balance'] < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 扣除买家的余额，平台收款
            self.db.user.update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )

            # 更新订单状态为已付款
            self.db.new_order.update_one(
                {"order_id": order_id},
                {"$set": {"is_paid": True}}
            )

        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))

        return 200, "ok"
   
    def confirm_receipt_and_pay_to_seller(self, user_id: str, password:str,order_id: str) -> (int, str): # type: ignore
        try:
            # 查找订单
            order = self.db.new_order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order['user_id']

            # 检查用户身份
            if buyer_id != user_id:
                return error.error_authorization_fail()
            user = self.db.user.find_one({"user_id": buyer_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()
            # 检查是否被取消
            if order['status'] == "canceled":
                return 400, "Order has been canceled."
            # 检查是否已经付款
            if not order.get('is_paid', False):
                return 400, "Order is not paid yet."

            # 检查是否已确认收货
            if order.get('is_received', False):
                return 400, "Order has already been received."

            buyer_id = order['user_id']
            store_id = order['store_id']

            seller = self.db.user_store.find_one({"store_id": store_id})
            seller_id = seller['user_id']

            # 计算订单总价
            order_details = self.db.new_order_detail.find({"order_id": order_id})
            total_price = sum(detail['count'] * detail['price'] for detail in order_details)

            # 平台将钱转给卖家
            self.db.user.update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )

            # 更新订单状态为已确认收货
            self.db.new_order.update_one(
                {"order_id": order_id},
                {"$set": {"is_received": True}}
            )

            # 更新订单状态为已完成
            self.db.new_order.update_one(
                {"order_id": order_id},
                {"$set": {"order_completed": True}}
            )
            # 删除订单和订单详情（可选，视业务逻辑而定）
            # self.db.new_order.delete_one({"order_id": order_id})
            # self.db.new_order_detail.delete_many({"order_id": order_id})

        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def add_funds(self, user_id, password, add_value) -> (int, str): # type: ignore
        try:
            user = self.db.user.find_one({"user_id": user_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()

            self.db.user.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))

        return 200, "ok"

    def query_order_status(self, user_id: str, order_id: str, password) -> (int, str, str): # type: ignore
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ("None",)

            user = self.db.user.find_one({"user_id": user_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail() + ("None",)

            # 查找订单
            order = self.db.new_order.find_one({"order_id": order_id, "user_id": user_id})
            if order is None:
                return error.error_invalid_order_id(order_id) + ("None",)

            # 返回订单状态
            order_status = self.ORDER_STATUS[order['status']]

            return 200, "ok", order_status
        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e)) + ("None",)

    # def query_user_orders(self, user_id: str) -> (int, str, list): # type: ignore
    #     try:
    #         # 检查用户是否存在
    #         if not self.user_id_exist(user_id):
                # return error.error_non_exist_user_id(user_id) + ("None",)
    #         # 查找用户的所有订单
    #         orders = list(self.db.new_order.find({"user_id": user_id}))

    #         return 200, "ok", orders
    #     except Exception as e:
    #         return 530, "{}".format(str(e)), None

    def cancel_order(self, user_id: str, order_id: str, password) -> (int, str): # type: ignore
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            
            user = self.db.user.find_one({"user_id": user_id})
            if user is None or user['password'] != password:
                return error.error_authorization_fail()

            # 查找订单
            order = self.db.new_order.find_one({"order_id": order_id, "user_id": user_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            # 检查订单是否已经支付
            if order.get('is_paid', False):
                return error.error_cannot_be_canceled(order_id)

            # 取消订单，更新订单信息
            self.db.new_order.update_one(
                {"order_id": order_id},
                {"$set": {"status": "canceled"}}
            )

            # 恢复库存
            order_details = self.db.new_order_detail.find({"order_id": order_id})
            for detail in order_details:
                self.db.store.update_one(
                    {"store_id": order['store_id'], "book_id": detail['book_id']},
                    {"$inc": {"stock_level": detail['count']}}
                )

            # 删除订单，根据业务逻辑自选
            # self.db.new_order.delete_one({"order_id": order_id})
            # self.db.new_order_detail.delete_many({"order_id": order_id})

        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))

        return 200, "ok"

    def auto_cancel_expired_orders(self):
        try:
            # 获取当前时间
            now = datetime.utcnow()

            # 设定超时时间为 10 s
            timeout_duration = timedelta(seconds=10)

            # 查找所有未支付的订单
            pending_orders = self.db.new_order.find({"is_paid": False})

            for order in pending_orders:
                created_time = order["created_time"]

                # 检查订单是否已经超时
                if now - created_time > timeout_duration:
                    # 取消订单
                    order_id = order["order_id"]
                    self.db.new_order.update_one(
                        {"order_id": order_id},
                        {"$set": {"status": "canceled"}}
                    )
                    # 恢复库存
                    order_details = self.db.new_order_detail.find({"order_id": order_id})
                    for detail in order_details:
                        self.db.store.update_one(
                            {"store_id": order['store_id'], "book_id": detail['book_id']},
                            {"$inc": {"stock_level": detail['count']}}
                        )
        except Exception as e:# pragma: no cover
            logging.error(f"Error cancelling expired orders: {str(e)}")
        return 200, "ok"



    def run_periodic_tasks(self):
        schedule.every(10).minutes.do(self.auto_cancel_expired_orders)  # 每 10 分钟检查一次超时订单

        while True:
            schedule.run_pending()
            time.sleep(1)

    # 在应用启动时运行
    # run_periodic_tasks()

