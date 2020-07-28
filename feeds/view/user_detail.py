#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 查看当前用户名下的 up 主账号
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from package.session_manage import clear_session
from user.models import UserModel
from ..models import *
from ._utils import *


# 查询指定用户的消息
@my_csrf_decorator()
@post_limit
@login_limit
def user_detail(request):
    # 先获取当前用户的id
    owner = request.session.get('id', '')  # 当前用户

    # 先获取当前用户的信息
    user_info = UserModel.objects.filter(id=owner)
    # 当前用户不存在？？
    if len(user_info) == 0:
        clear_session()
        return get_res_json(code=0, msg='当前用户不存在')

    user_info = user_info[0]
    user_info = {
        'username': user_info.username,
        'register_date': user_info.register_date.strftime("%Y-%m-%d %H:%M:%S"),
        'last_login': user_info.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        'user_permission_cn': get_user_permission_cn(user_info.user_permission),
        'create_uploader': can_create_uploader(user_info.user_permission)
    }

    # 先查询列表
    mp_list = MsgPuber.objects.filter(user_id=owner)
    # 没数据的话直接返回
    if len(mp_list) == 0:
        return get_res_json(code=200, data={
            'userinfo': user_info,
            'list': []
        })

    result = []
    for mp_info in mp_list:
        uploader_id = mp_info.id
        # 获取 UP主 信息
        d = get_msgpub_info(mp_info)

        # 拿取他推送的所有信息（倒叙排列）
        feed_list = Feeds.objects.filter(uploader_id=uploader_id).order_by('-id')

        if len(feed_list) == 0:
            d['last_msg'] = None
        else:
            # 将最近一条推送消息添加进去
            feed = feed_list[0]
            d['last_msg'] = {
                'id': feed.id,
                'uploader_id': feed.uploader_id,
                'pub_time': feed.pub_time.strftime("%Y-%m-%d %H:%M:%S"),
                'content': feed.content,
                'sendtime': get_sendtime_cn(feed.sendtime),
                'action_type': feed.action_type
            }
        result.append(d)

    # 然后返回给用户
    return get_res_json(code=200, data={
        'userinfo': user_info,
        'list': result
    })
