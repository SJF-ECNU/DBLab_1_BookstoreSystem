import pytest
from be.model.search import BookStoreSearcher

class TestSearchBooks:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化 bookstore_searcher 和相关数据
        self.store_id = "test_add_books_store_id_848aa78c-887a-11ef-89e5-2e81db39535e"
        self.keyword = "美丽心灵"
        self.searcher = BookStoreSearcher()
        yield

    def test_non_exist_book_id_in_the_store(self):
        # 测试不存在的书籍，搜索是在book数据库中进行，搜索范围是全局，期望返回 523 错误码
        code, message = self.searcher.search_books(
            keyword="nonexistent_book",
            search_scope="all",
            search_in_store=False,
            store_id=self.store_id
        )
        assert code == 523
        # assert "Book with ID" in message

    def test_non_exist_store_id(self):
        # 测试不存在的store_id，期望返回 524 错误码
        code, message = self.searcher.search_books(
            keyword=self.keyword,
            search_scope="all",
            search_in_store=True,
            store_id="non_existent_store_id"
        )
        assert code == 524
        # assert "Store with ID" in message

    def test_non_exist_book_id_in_the_store(self):
        # 测试书籍不存在store_id对应的store中，期望返回 525 错误码
        code, message = self.searcher.search_books(
            keyword="nonexistent_book",
            search_scope="all",
            search_in_store=True,
            store_id=self.store_id
        )
        assert code == 525
        # assert "Book with ID" in message

    def test_partial_scope_search(self):
        # 测试部分匹配 scope 搜索
        code, results = self.searcher.search_books(
            keyword=self.keyword,
            search_scope="title tags",
            search_in_store=False
        )
        assert code == 200
        # assert isinstance(results, list)
        # for result in results:
        #     assert "title" in result or "tags" in result

    def test_full_scope_search(self):
        # 测试全范围搜索
        code, results = self.searcher.search_books(
            keyword=self.keyword,
            search_scope="all",
            search_in_store=False
        )
        assert code == 200
        # assert isinstance(results, list)
        # for result in results:
        #     assert any(field in result for field in ["title", "tags", "content", "book_intro"])

    def test_search_books_in_existing_store(self):
        # 测试在存在的store_id中搜索书籍
        code, results = self.searcher.search_books(
            keyword=self.keyword,
            search_scope="all",
            search_in_store=True,
            store_id=self.store_id
        )
        assert code == 200
        # assert isinstance(results, list)
