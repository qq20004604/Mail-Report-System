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

统一：

```
upid：UP主ID，统一采用 MsgPuber 的 id 属性
订阅者id：指User表里的id
owner：当取owner时，指的都是User表里的id（无论是订阅者还是UP主）
```


## 获取消息号名字

> /feeds/get_user_name/

入参

```
无
```

出参：

```
{
    'pub_name': ''      // 消息号的名字
}
```


## 推送一条消息

> /feeds/send/

入参

```
{
    'msg': '',      //  字符串，消息内容，最大长度150
    'sendtime': 'now',  // 字符串，发送时间，now 立刻（后端会变为 plan），delay 稍后（后端为 delay）
    'href': '',     // 字符串，外链，最大长度100
    // 'pub_name':'',      // 消息号名字，可选。默认为空或不传，如果填写，则修改消息号名字为该字段名字
}
```

出参：

标准出参内容


## 推送一条消息（密钥的形式）

> /feeds/send/key/

入参

```
{
    'msg': '',      //  字符串，消息内容，最大长度150
    'sendtime': 'now',  // 字符串，发送时间，now 立刻（后端会变为 plan），delay 稍后（后端为 delay）
    'href': '',     // 字符串，外链，最大长度100
    'secret_key': 'key',    // 密钥，长度20位，必填
}
```

出参：

```
{
    code: 200,      // 200 成功，0 失败， 100 第一次必须网页推送一条消息（内容任意），之后方能使用密钥推送
}
```


## 查看所有发布过消息的用户，以及他们最近发布的一条消息

> /feeds/user/all/

入参：

```
{
    page: 1,        // 分页查找，第1页。每页数量后端定。默认是20
}
```

出参：

```
{
    'page': {
        'total': 110,        // 总数
        'total_page': 6,        // 一共多少页
        'current_page': 1,      // 当前第几页
        'page_size': 20,        // 每页多少个
    },
    'list': [
        {
            id: 123,    // 用户id，这个是MsgPuber表的id
            last_pub_time: '2000-00-00 00:00:00',       // 最近推送时间
            good_praise: 0,     // 好评数
            pub_name: '',   // 消息号名字
            had_sub: false,    // 是否已订阅（true = 是）
            last_msg: {         // 最近推送的一条消息
                id: 12,     // 消息id
                pub_time: '2000-00-00 00:00:00',      // 消息推送时间
                content: '',        //  消息正文
                sendtime: '',       // 消息状态（后端手动转换后推送给前端）
                had_del: false,     // 该消息是否被删除
                href: '',       // 该消息外链
            }
        }
    ]
}
```

## 以时间为顺序排序，查看最近发布的消息

> /feeds/msg/all/

入参：

```
{
    page: 1,        // 分页查找，第1页。每页数量后端定
}
```

出参：

```
{
    'page': {
        'total': 110,        // 总数
        'total_page': 6,        // 一共多少页
        'current_page': 1,      // 当前第几页
        'page_size': 20,        // 每页多少个
    },
    'list': [
        {
            id: 12,     // 消息id
            pub_time: '2000-00-00 00:00:00',      // 消息推送时间
            content: '',        //  消息正文
            sendtime: '',       // 消息状态（后端手动转换后推送给前端）
            had_del: false,     // 该消息是否被删除
            href: '',       // 该消息外链
            puber_id: 30,     // MsgPuber表的puber_id
            upid: 30,     // 消息推送人的id，这个是MsgPuber表的id（方便反查推送人）
        }
    ]
}
```

## 修改当前用户的信息

> /feeds/user/pub/update/

入参：

```
{
    'pub_name': '',     // 修改姓名（非必填，不填则不会修改）
    'make_new_key': true,   // 生成新密钥，如果为 false 或者缺少这个字段，则不会生成
}
```



## 查看当前用户名下所有的消息

> /feeds/user/self/

入参

```
{
    page: 1
}
```

出参：

```
{
    code: 200,
    msg: '',
    data: {
        user_info: {
            id: 123,    // 用户id，这个是MsgPuber表的id
            last_pub_time: '2000-00-00 00:00:00',       // 最近推送时间
            good_praise: 0,     // 好评数
            pub_name: '',   // 消息号名字
            auth: '01',     // 01 标准订阅（用户定时收取，一天只能推送一次）。 02 订阅后需确认后才生效，不限制发布频率
            secret_key: '',     // 秘钥，默认为空，有秘钥的情况下才能通过调用接口提交数据（使用密钥推送消息不需要登录）
        },
        'page': {
            'total': 110,        // 总数
            'total_page': 2,        // 一共多少页
            'current_page': 1,      // 当前第几页
            'page_size': 100,        // 每页多少个
        },
        feeds: [        // 如果是当前用户自己推送，
            {
                id: 12,     // 消息id
                pub_time: '2000-00-00 00:00:00',      // 消息推送时间
                content: '',        //  消息正文
                sendtime: '',       // 消息状态（后端手动转换后推送给前端）
                had_del: false,     // 该消息是否被删除
                href: '',       // 该消息外链
            }
        ]
    }
}
```


## 查看某用户名下所有的消息

> /feeds/user/pub/detail/

只能查询已经推送成功的信息，并且不能是已删除的信息（虽然推送成功的不能被删除）


入参

```
{
    upid: 1,  //  查询的UP主id，MsgPuber的id
    page: 1,     // 第一页
}
```

出参：

```
{
    code: 200,
    msg: '',
    data: {
        user_info: {
            id: 123,    // 用户id，这个是MsgPuber表的id
            puber_id: 132,      // up主的user表里的id，也是 MsgPuber 表的 puber_id
            last_pub_time: '2000-00-00 00:00:00',       // 最近推送时间
            good_praise: 0,     // 好评数
            pub_name: '',   // 消息号名字
            auth: '01',     // 01 标准订阅（用户定时收取，一天只能推送一次）。 02 订阅后需确认后才生效，不限制发布频率
        },
        'page': {
            'total': 110,        // 总数
            'total_page': 2,        // 一共多少页
            'current_page': 1,      // 当前第几页
            'page_size': 100,        // 每页多少个
        },
        feeds: [        // 如果是当前用户自己推送，
            {
                id: 12,     // 消息id
                pub_time: '2000-00-00 00:00:00',      // 消息推送时间
                content: '',        //  消息正文
                sendtime: '',       // 消息状态（后端手动转换后推送给前端）（备注：只能查询到已推送的消息即 done）
                had_del: false,     // 该消息是否被删除（备注：这里只能查询到未删除的）
                href: '',       // 该消息外链
            }
        ]
    }
}
```

## 订阅某个消息

> /feeds/subscribe/

入参：

```
{
    upid: 12,     // 被订阅者的id，这个是MsgPuber表的id
    sub_type: '01',     //   01：邮件订阅，02：QQ订阅
    qq: 12345,          // qq号，非必须，非QQ订阅时无视
}
```

出参：

```
{
    code: 200,
    msg: '订阅成功'
}
```

## 取消订阅某个信息

> /feeds/unsubscribe/

入参：

```
{
    upid: 12,     // 被订阅者的id，这个是MsgPuber表的id
    sub_type: '01',     //   01：邮件订阅，02：QQ订阅
    qq: 12345,          // qq号，非必须，非QQ订阅时无视
}
```

出参：

```
{
    code: 200,
    msg: '取消订阅成功'
}
```

## 查看某用户订阅了哪些up主

> /feeds/subscribe/list/

入参：

```
{
    sub_type: '01',     // 01表示查询当前登录用户订阅的信息，02表示查询某QQ订阅的信息
    qq: 12345,       // 非必须，当 type: '02' 时，必须的
    page: 1,        // 第几页。默认一页20个
}
```

出参：

```
{
    code: 200,
    msg: '',
    data: {
        'page': {
            'total': 110,        // 总数
            'total_page': 2,        // 一共多少页
            'current_page': 1,      // 当前第几页
            'page_size': 100,        // 每页多少个
        },
        suber_info: {       // 如果没有订阅数据，则 suber_info = null
            'user_id': 132,     // 当前用户的 id
            'qq': 213555,       // 订阅的 QQ（如果是邮件订阅，这里为空）
            'action': '01',     // 订阅类型，01：邮件，02：QQ
            'rec_time': '12:00',    // 接受邮件推送的时间
            'is_active': true,      // 邮件推送是否生效。false 表示当前不接受邮件推送
        }
        list: [
            {
                puber_id: 123,    // 用户id，这个是MsgPuber表的id
                last_pub_time: '2000-00-00 00:00:00',       // 最近推送时间
                good_praise: 0,     // 好评数
                pub_name: '',   // UP主名字
                sub_type: '01',   // 订阅类型，01：邮件，02：QQ
                action_time: '',    //  订阅时间
                is_active: false,   // 是否生效中（true为生效中，false为取消订阅）
                auth: '01',         // 01 标准订阅（用户定时收取，一天只能推送一次）。 02 订阅后需确认后才生效，不限制发布频率
                last_msg: {         // 最近推送的一条消息
                    id: 12,     // 消息id
                    pub_time: '2000-00-00 00:00:00',      // 消息推送时间
                    content: '',        //  消息正文
                    sendtime: '',       // 消息状态（后端手动转换后推送给前端）
                    had_del: false,     // 该消息是否被删除
                    href: '',       // 该消息外链
                }
            }
        ]
    }
}
```

## 修改用户订阅信息

> /feeds/subscribe/update/

入参：

```
{
    'rec_time': '1200',     // 接受推送时间，1200 表示 中午12点00分
    'is_active': true,      // 用户是否接受推送，true 表示接受推送
}
```

出参：

```
{
    code: 200,
    msg: '设置成功'
}
```

## 查看订阅自己的用户

> /feeds/user/self/suberlist/

入参：

无

出参：

```
{
    'page': {
        'total': 110,        // 总数
        'total_page': 2,        // 一共多少页
        'current_page': 1,      // 当前第几页
        'page_size': 100,        // 每页多少个
    },
    'list': [
        {
            'suber_id': 123,   // 订阅者 ID
            'email': '',        // 订阅者邮箱（注意，这里要混淆 @ 符号后面的内容）
            'suber_name': '订阅者的昵称', // User 表，打吗最后 6 位
            'sub_type': '01',     // 订阅类型 01 邮件 02 QQ订阅
            'qq': -1,       // 订阅者 QQ，不是 QQ 订阅时，这个值为 -1
            'sub_time': '2000-00-00 00:00:00',      //  订阅时间
            'is_active': true,      // 只返回为 true 的订阅者
            'puber_allow_rec': true,    // UP主 是否允许订阅者接受信息。
                                        // 只有当 UP主 MsgPuber.auth = '02'时，up 主才能修改
        }
    ]
}
```

## 允许指定用户接受当前 UP 主的邮件推送

> /feeds/user/self/suber/rec/

入参：

```
{
    suber_id: 12,   // 订阅者的 ID
}
```

出参：

标准出参