import os
import random
import base64
import simplejson as json
from pymongo import MongoClient
from bson.binary import Binary

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: list
    pictures: list

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        self.client = MongoClient('mongodb://localhost:27017/')  # 连接到MongoDB
        self.db = self.client['bookstore']  # 数据库名称
        self.collection = self.db['books']  # 集合名称

    def get_book_count(self):
        return self.collection.count_documents({})

    def get_book_info(self, start, size) -> list[Book]:
        books = []
        cursor = self.collection.find().skip(start).limit(size)

        for row in cursor:
            book = Book()
            book.id = str(row.get('_id'))  # MongoDB的_id字段
            book.title = row.get('title')
            book.author = row.get('author')
            book.publisher = row.get('publisher')
            book.original_title = row.get('original_title')
            book.translator = row.get('translator')
            book.pub_year = row.get('pub_year')
            book.pages = row.get('pages')
            book.price = row.get('price')
            book.currency_unit = row.get('currency_unit')
            book.binding = row.get('binding')
            book.isbn = row.get('isbn')
            book.author_intro = row.get('author_intro')
            book.book_intro = row.get('book_intro')
            book.content = row.get('content')
            book.tags = row.get('tags', [])
            
            # 处理二进制图片数据
            picture_binary = row.get('picture')
            if isinstance(picture_binary, Binary):
                # 将二进制数据转换为Base64编码字符串
                picture_base64 = base64.b64encode(picture_binary).decode('utf-8')
                book.pictures.append(picture_base64)

            books.append(book)

        return books
