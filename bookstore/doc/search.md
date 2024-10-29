## 搜索书籍

#### URL：
POST http://[address]/search/search_books

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:
```json
{
  "keyword": "关键词",
  "search_scope": "搜索范围",
  "search_in_store": "True or False",
  "store_id": "商店ID"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
keyword | string | 搜索关键词 | N
search_scope | string | 搜索范围，可以是多个字段如'title tags'	也可以是全局搜索'all' | Y，默认为'all'
search_in_store | boolean | 是否只在指定店铺内搜索 | Y，默认为false
store_id | string | 店铺ID，仅当search_in_store为true时需要 | Y，默认为null


#### Response

Status Code:

码 | 描述
--- | ---
200 | 搜索成功
401 | 授权失败
523 | 书籍keyword不存在
524 | 店铺ID不存在
525 | 在指定店铺内未找到书籍keyword
530 | 数据库操作错误

##### Body:
```json
{
  "message": [搜索结果列表],
  "code": 状态码
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | array | 包含搜索结果的数组 | N
code    | integer | 响应状态码      | N