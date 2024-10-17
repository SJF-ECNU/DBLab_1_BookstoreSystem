import sqlite3
from pymongo import MongoClient

# 连接SQLite数据库
sqlite_conn = sqlite3.connect('bookstore/be.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bookstore']  # 数据库名为 bookstore

# 迁移user表
def migrate_user():
    sqlite_cursor.execute("SELECT user_id, password, balance, token, terminal FROM user;")
    users = sqlite_cursor.fetchall()
    user_collection = db['user']  # MongoDB中的集合名为user

    for user in users:
        user_doc = {
            "user_id": user[0],
            "password": user[1],
            "balance": user[2],
            "token": user[3],
            "terminal": user[4]
        }
        user_collection.insert_one(user_doc)

# 迁移user_store表
def migrate_user_store():
    sqlite_cursor.execute("SELECT user_id, store_id FROM user_store;")
    user_stores = sqlite_cursor.fetchall()
    user_store_collection = db['user_store']

    for user_store in user_stores:
        user_store_doc = {
            "user_id": user_store[0],
            "store_id": user_store[1]
        }
        user_store_collection.insert_one(user_store_doc)

# 迁移store表
def migrate_store():
    sqlite_cursor.execute("SELECT store_id, book_id, book_info, stock_level FROM store;")
    stores = sqlite_cursor.fetchall()
    store_collection = db['store']

    for store in stores:
        store_doc = {
            "store_id": store[0],
            "book_id": store[1],
            "book_info": store[2],
            "stock_level": store[3]
        }
        store_collection.insert_one(store_doc)

# 迁移new_order表
def migrate_new_order():
    sqlite_cursor.execute("SELECT order_id, user_id, store_id FROM new_order;")
    orders = sqlite_cursor.fetchall()
    order_collection = db['new_order']

    for order in orders:
        order_doc = {
            "order_id": order[0],
            "user_id": order[1],
            "store_id": order[2]
        }
        order_collection.insert_one(order_doc)

# 迁移new_order_detail表
def migrate_new_order_detail():
    sqlite_cursor.execute("SELECT order_id, book_id, count, price FROM new_order_detail;")
    order_details = sqlite_cursor.fetchall()
    order_detail_collection = db['new_order_detail']

    for order_detail in order_details:
        order_detail_doc = {
            "order_id": order_detail[0],
            "book_id": order_detail[1],
            "count": order_detail[2],
            "price": order_detail[3]
        }
        order_detail_collection.insert_one(order_detail_doc)

# 执行迁移
migrate_user()
migrate_user_store()
migrate_store()
migrate_new_order()
migrate_new_order_detail()

# 关闭数据库连接
sqlite_conn.close()
client.close()