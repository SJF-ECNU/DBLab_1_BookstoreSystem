import requests
from urllib.parse import urljoin
from fe.access.auth import Auth

class BookSearcher:
    def __init__(self, url_prefix, user_id: str, password: str):
        self.url_prefix = urljoin(url_prefix, "search/")
        self.user_id = user_id
        self.password = password
        self.terminal = "search_terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def search_books(self, keyword: str, search_scope: str = "all", store_id: str = None) -> (int, dict):
        """
        搜索书籍功能
        :param keyword: 搜索关键词
        :param search_scope: 搜索范围 (默认为 "all")
        :param store_id: 可选参数，指定商店 ID
        :return: 返回状态码和搜索结果
        """
        json_data = {
            "keyword": keyword,
            "search_scope": search_scope,
        }

        # 如果指定了 store_id，则加入到请求体中
        if store_id is not None:
            json_data["search_in_store"] = True
            json_data["store_id"] = store_id
        else:
            json_data["search_in_store"] = False

        url = urljoin(self.url_prefix, "books")
        headers = {"token": self.token}
        response = requests.post(url, headers=headers, json=json_data)
        return response.status_code, response.json()

