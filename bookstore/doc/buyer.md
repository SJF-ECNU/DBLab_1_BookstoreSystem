## 买家下单

#### URL：
POST http://[address]/buyer/new_order

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:
```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
store_id | string | 商铺ID | N
books | class | 书籍购买列表 | N

books数组：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍的ID | N
count | string | 购买数量 | N


#### Response

Status Code:

码 | 描述
--- | ---
200 | 下单成功
5XX | 买家用户ID不存在
5XX | 商铺ID不存在
5XX | 购买的图书不存在
5XX | 商品库存不足

##### Body:
```json
{
  "order_id": "uuid"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
order_id | string | 订单号，只有返回200时才有效 | N


## 买家付款

#### URL：
POST http://[address]/buyer/payment

#### Request

##### Body:
```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 买家用户密码 | N 


#### Response

Status Code:

码 | 描述
--- | ---
200 | 付款成功
5XX | 账户余额不足
5XX | 无效参数
401 | 授权失败 


## 买家充值

#### URL：
POST http://[address]/buyer/add_funds

#### Request



##### Body:
```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N
add_value | int | 充值金额，以分为单位 | N


Status Code:

码 | 描述
--- | ---
200 | 充值成功
401 | 授权失败
5XX | 无效参数

## 买家查询订单状态

#### URL：
POST http://[address]/buyer/query_order_status

#### Request

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "$user id$",
  "order_id": "$order id$",
  "password": "$password$"
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 用户密码 | N

#### Response

- `Status Code`

码 | 描述
--- | ---
200 | 查询成功
401 | 授权失败
511 | 用户不存在
518 | 非法订单号
530 | 其它异常


- `message`

message | 描述
--- | ---
ok  | 查询成功
authorization fail | 授权失败
non exist user id {`user_id`} | 用户不存在
invalid order id {`order_id`} | 非法订单号
Exception e | 异常信息

- `order_status`


order_status | 描述
--- | ---
`pending`  | 待支付
`paid` | 已支付
`shipped` | 已发货
`received` | 已收货
`completed` | 已完成
`canceled` | 已取消
`None` | 异常状态


## 买家查询所有订单信息

#### URL：
POST http://[address]/buyer/query_buyer_all_orders

#### Request

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "$user id$",
  "password": "$password$"
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N

#### Response

- `Status Code`

码 | 描述
--- | ---
200 | 查询成功
401 | 授权失败
511 | 用户不存在
530 | 其它异常


- `message`

message | 描述
--- | ---
ok  | 查询成功
authorization fail | 授权失败
non exist user id {`user_id`} | 用户不存在
Exception e | 异常信息

- `orders`


orders | 描述
--- | ---
`orders`  | 订单详情
`None` | 异常状态


## 买家取消订单

#### URL：
POST http://[address]/buyer/cancel_order

#### Request

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:
```json
{
  "user_id": "$user id$",
  "order_id": "$order id$",
  "password": "$password$"
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 用户密码 | N

#### Response

- `Status Code`

码 | 描述
--- | ---
200 | 取消成功
401 | 授权失败
511 | 用户不存在
518 | 非法订单号
521 | 无法取消订单
530 | 其它异常


- `message`

message | 描述
--- | ---
ok  | 取消成功
authorization fail | 授权失败
non exist user id {`user_id`} | 用户不存在
invalid order id {`order_id`} | 非法订单号
cannot be canceled, order id {`order_id`} | 订单已支付，无法取消
Exception e | 异常信息


## 超时未支付，自动取消订单

#### URL：
POST http://[address]/buyer/auto_cancel_expired_orders

#### Request

定时自动发送 `request`

#### Response

- `Status Code`

码 | 描述
--- | ---
200 | 自动取消成功
530 | 其它异常


- `message`

message | 描述
--- | ---
ok  | 自动取消成功
not | 自动取消失败