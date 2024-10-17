from pymongo import MongoClient

# 连接到 MongoDB，假设 MongoDB 运行在本地服务器
client = MongoClient('mongodb://localhost:27017/')

# 获取所有数据库名称
databases = client.list_database_names()
print("Databases:")
for db_name in databases:
    print(f"- {db_name}")

    # 选择数据库
    db = client[db_name]

    # 获取数据库中的集合（表）名称
    collections = db.list_collection_names()
    print("  Collections:")
    for coll_name in collections:
        print(f"  - {coll_name}")

        # 获取集合中的字段信息，使用 `find_one` 获取样本数据
        sample_document = db[coll_name].find_one()
        if sample_document:
            print("    Sample document structure:")
            for key, value in sample_document.items():
                print(f"      Field: {key}, Type: {type(value).__name__}")
        else:
            print("    (Empty Collection)")

    print()  # 分隔每个数据库的输出