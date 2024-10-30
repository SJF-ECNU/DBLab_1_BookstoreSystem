from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")  # 替换为你的 MongoDB URI
db = client["bookstore"]  # 替换为你的数据库名称

# 创建一个文本文件用于存储所有集合的索引信息
with open("mongo_indexes.txt", "w") as f:
    # 遍历所有集合
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        
        # 获取索引信息
        indexes = collection.list_indexes()
        
        # 写入集合名称
        f.write(f"Collection: {collection_name}\n")
        
        # 遍历每个索引并写入信息
        for index in indexes:
            f.write(f"  Index Name: {index['name']}\n")
            f.write(f"    Key: {index['key']}\n")
            f.write(f"    Unique: {index.get('unique', False)}\n")
            f.write(f"    Sparse: {index.get('sparse', False)}\n")
            f.write(f"    Background: {index.get('background', False)}\n")
            f.write("\n")  # 添加空行以分隔不同索引

        f.write("\n")  # 添加空行以分隔不同集合

print("所有集合的索引信息已导出为文本文件 mongo_indexes.txt。")
