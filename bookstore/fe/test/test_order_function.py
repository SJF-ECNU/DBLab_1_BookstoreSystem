import pytest
from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
import time

class TestOrderFunctions:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book] # type: ignore
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_functions_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_functions_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_functions_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_query_order_status_ok(self):
        code, message, order_status = self.buyer.query_order_status(self.order_id)
        assert code == 200
        assert order_status is not None

    def test_cancel_order_ok(self):
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

    def test_auto_cancel_expired_orders(self):
        # 循环调用自动取消接口，每隔10秒一次，执行5次
        for _ in range(5):  # 可以根据需要调整循环次数
            code, message = self.buyer.auto_cancel_expired_orders()
            assert code == 200
            print(f"Auto cancel expired orders call result: {message}")
            time.sleep(10)  # 等待10秒
