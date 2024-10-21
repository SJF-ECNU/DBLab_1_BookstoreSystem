import requests
import threading
from urllib.parse import urljoin
from be import serve
from be.model.store import init_completed_event
from fe import conf
# fe/conftest.py
import requests

# 其他配置代码
thread: threading.Thread = None


# 修改这里启动后端程序，如果不需要可删除这行代码
def run_backend():
    # rewrite this if rewrite backend
    serve.be_run()


def pytest_configure(config):
    global thread
    print("frontend begin test")
    thread = threading.Thread(target=run_backend)
    thread.start()
    init_completed_event.wait()


def pytest_unconfigure(config):
    url = urljoin(conf.URL, "shutdown")
    requests.get(url)
    thread.join()
    print("frontend end test")
