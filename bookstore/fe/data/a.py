import sqlite3
from pymongo import MongoClient
import base64

# 连接到 MongoDB
client = MongoClient('localhost', 27017)
db = client['bookstore']  # 创建数据库
collection = db['books']  # 创建集合

# 连接到 SQLite 数据库
conn = sqlite3.connect('book.db')
cursor = conn.cursor()

# 查询所有图书数据
cursor.execute("SELECT * FROM book")
rows = cursor.fetchall()

# 插入数据到 MongoDB
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
        'picture': base64.b64encode(row[16]).decode('utf-8') if row[16] else None  # 处理 BLOB 数据
    }
    collection.insert_one(book_data)

# 关闭数据库连接
conn.close()

# 测试读写操作
# for book in collection.find():
#     print(book)

print("数据导入完成！")
