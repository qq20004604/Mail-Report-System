# 约定

请求方式统一为 ``post``

统一外包装是：

```
{
    'code': 200,    // 200成功，0失败，5未登录
    'msg': '',      // 成功或错误信息
    'data': {}      // 返回数据，都在data里
}
```


## 发送验证码邮件

> /user/send_email_regcode/

入参

```
{
    'username': '用户名',
    'email': '邮箱'
}
```

出参：

```
通用
```



## 注册

> /user/get_user_name/

入参

```
{
    'username': '用户名',
    'password': '密码',
    'email': '邮箱',
    'regcode': '验证码',   // 6位长度
}
```

出参：

```
通用
```
