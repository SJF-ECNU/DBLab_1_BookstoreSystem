from pymongo import MongoClient
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            # 检查商店是否存在
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            # 检查书籍是否已经存在
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 将书籍插入到store集合中
            self.db["store"].insert_one({
                "store_id": store_id,
                "book_id": book_id,
                "book_info": book_json_str,
                "stock_level": stock_level
            })
        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, 
        user_id: str, 
        store_id: str, 
        book_id: str, 
        add_stock_level: int
    ):
        try:
            # 检查用户、商店和书籍是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 更新库存数量
            self.db["store"].update_one(
                {"store_id": store_id, "book_id": book_id},
                {"$inc": {"stock_level": add_stock_level}}
            )
        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str): # type: ignore
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            # 检查商店是否已经存在
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 创建商店，插入到user_store集合中
            self.db["user_store"].insert_one({
                "store_id": store_id,
                "user_id": user_id
            })
        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship(
            self,
            user_id: str,
            store_id: str,
            order_id: str,
            ):
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            # 检查商店是否存在
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            # 检查订单是否存在
            if not self.order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)
            # 检查订单是否已经支付
            if not self.order_is_paid(order_id):
                return error.error_not_be_paid(order_id)
            # 检查订单是否已经发货
            if self.order_is_shipped(order_id):
                return error.error_order_is_shipped(order_id)
            # 更新订单状态
            self.db["new_order"].update_one(
                {"order_id": order_id, "store_id": store_id},
                {"$set": {"is_shipped": True}}
            )
        
        except Exception as e:# pragma: no cover
            return 520, "{}".format(str(e))
        return 200, "ok"

    

    def query_one_store_orders(self, user_id: str, store_id: str, password) -> (int, str, list): # type: ignore
        try:
            # 检查用户与商店是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ("None",)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + ("None",)
            
            # 检查用户密码是否正确
            user = self.db.user.find_one({"user_id": user_id})
            if user['password'] != password:
                return error.error_authorization_fail() + ("None",)

            # 查找用户是否存在该商店
            user_store = self.db.user_store.find_one({"user_id": user_id, "store_id": store_id})
            
            if not user_store:
                return error.error_no_store_found(user_id) + ("None",)

            # 查找该商店的所有订单
            orders = list(self.db.new_order.find({"store_id": store_id}))

        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e)), "None"
        return 200, "ok", str(orders)

    def query_all_store_orders(self, user_id: str, password) -> (int, str, list): # type: ignore
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ("None",)

            # 检查用户密码是否正确
            user = self.db.user.find_one({"user_id": user_id})
            if user['password'] != password:
                return error.error_authorization_fail() + ("None",)

            # 查找用户的商店
            user_stores = self.db.user_store.find({"user_id": user_id})

            # 检查是否有商店
            if self.db.user_store.count_documents({"user_id": user_id}) == 0:
                return error.error_no_store_found(user_id) + ("None",)

            all_store_orders = {}
            for user_store in user_stores:
                store_id = user_store['store_id']
                # 查找该商店的所有订单
                orders = list(self.db.new_order.find({"store_id": store_id}))
                all_store_orders[store_id] = orders

        except Exception as e:# pragma: no cover
            return 530, "{}".format(str(e)), "None"
        return 200, "ok", str(all_store_orders)

        