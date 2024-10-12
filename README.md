# DBLab_1_BookstoreSystem

## 通过requirements安装环境

```shell
cd bookstore
pip install -r requirements.txt
```

## bookstore目录结构
```
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```

## 执行测试
```bash
bash script/test.sh
```

（注意：如果提示`"RuntimeError: Not running with the Werkzeug Server"`，请输入下述命令，将 flask 和 Werkzeug 的版本均降低为2.0.0。）

```powershell
 pip install flask==2.0.0  

 pip install Werkzeug==2.0.0
```

## 数据形式
bookstore/fe/data/book.db中包含测试的数据，从豆瓣网抓取的图书信息，
 其DDL为：

    create table book
    (
        id TEXT primary key,
        title TEXT,
        author TEXT,
        publisher TEXT,
        original_title TEXT,
        translator TEXT,
        pub_year TEXT,
        pages INTEGER,
        price INTEGER,
        currency_unit TEXT,
        binding TEXT,
        isbn TEXT,
        author_intro TEXT,
        book_intro text,
        content TEXT,
        tags TEXT,
        picture BLOB
    );