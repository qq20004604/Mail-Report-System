#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ._utils import *


# 查看当前用户订阅了哪些up主
@my_csrf_decorator()
@post_limit
@login_limit
def user_subscribe_list(request):
    """
    流程：
    1. 拿到当前查的订阅类型，是QQ订阅还是邮件订阅，记录下来；
    2. 先查 SubscribeFeeds 表，拿到所有订阅信息（包括当前生效和取消订阅的）；
    3. 查到订阅时间、是否生效，再拿字段 upid 去查 MsgPuber 表，拿到up主的详细信息；
    4. 再去拿到up主的最近一条消息；
    5. 组装数据，每条信息是：订阅时间+类型 + up主信息 + up主最近推送消息的信息
    """

    # 当前登录的用户id
    owner = request.session.get('id', None)
    # 拉取当前用户的所有订阅记录
    sf_list = SubscribeFeeds.objects.filter(user_id=owner).order_by('-sub_time')

    if len(sf_list) == 0:
        return get_res_json(code=200, data={
            'list': []
        })

    # 先做出订阅列表
    my_sub_list = [
        {
            'uploader_id': item.uploader_id,  # 被订阅者id
            'sub_type': item.sub_type,  # 订阅类型
            'sub_type_cn': get_sub_type_cn(item.sub_type),  # 订阅类型
            'sub_time': item.sub_time.strftime('%Y-%m-%d %H:%M:%S'),  # 订阅时间
            'is_active': item.is_active,  # 是否生效中
            'puber_allow_rec': item.puber_allow_rec,  # up主是否允许用户收取邮件
            'uploader': None
        } for item in sf_list
    ]

    # 再反查 MsgPuber 表
    for sub_info in my_sub_list:
        uploader_id = sub_info['uploader_id']
        mp_info = MsgPuber.objects.filter(id=uploader_id)[0]
        # 获取当前up主的信息
        sub_info['uploader_info'] = get_msgpub_info(mp_info)

    return get_res_json(code=200, data={
        'list': my_sub_list
    })
