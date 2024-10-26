import sqlite3
from pymongo import MongoClient
from bson.binary import Binary

# 连接到SQLite数据库
sqlite_conn = sqlite3.connect('bookstore/fe/data/book.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接到MongoDB数据库
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['bookstore']  # 替换为你的数据库名称
mongo_collection = mongo_db['books']

# 从SQLite中查询book表的所有记录
sqlite_cursor.execute("SELECT * FROM book")
rows = sqlite_cursor.fetchall()

# 遍历每一行并插入到MongoDB中
for row in rows:
    book_data = {
        'id': row[0],
        'title': row[1],
        'author': row[2],
        'publisher': row[3],
        'original_title': row[4],
        'translator': row[5],
        'pub_year': row[6],
        'pages': row[7],
        'price': row[8],
        'currency_unit': row[9],
        'binding': row[10],
        'isbn': row[11],
        'author_intro': row[12],
        'book_intro': row[13],
        'content': row[14],
        'tags': row[15],
        'picture': Binary(row[16])  # 将BLOB数据转为Binary
    }
    
    # 插入到MongoDB中
    mongo_collection.insert_one(book_data)

# 关闭数据库连接
sqlite_conn.close()
mongo_client.close()

print("数据迁移完成！")
