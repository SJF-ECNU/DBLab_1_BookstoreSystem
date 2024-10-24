import time
import threading
import logging
from be.model import db_conn
import datetime
import schedule
import time



def cancel_expired_orders(self):
    try:
        # 获取当前时间
        now = datetime.utcnow()

        # 设定超时时间为 30 分钟
        timeout_duration = datetime.timedelta(minutes=30)

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
    except Exception as e:
        logging.error(f"Error cancelling expired orders: {str(e)}")

def run_periodic_tasks():
    schedule.every(10).minutes.do(cancel_expired_orders)  # 每 10 分钟检查一次超时订单

    while True:
        schedule.run_pending()
        time.sleep(1)

# 在应用启动时运行
run_periodic_tasks()