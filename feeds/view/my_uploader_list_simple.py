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


# 获取当前用户的up主列表（相当于 uploader_my_detail 比较详细信息来说，是简化版）
@my_csrf_decorator()
@post_limit
@login_limit
def my_uploader_list_simple(request):
    # 先获取当前用户的id
    owner = request.session.get('id', '')  # 当前用户

    # 先获取当前用户的信息
    user_info = UserModel.objects.filter(id=owner)
    # 当前用户不存在？？
    if len(user_info) == 0:
        clear_session()
        return get_res_json(code=0, msg='当前用户不存在')

    # 先查询列表
    mb_list = MsgPuber.objects.filter(user_id=owner)

    # 没数据的话直接返回空数组
    if len(mb_list) == 0:
        return get_res_json(code=200, data={
            'list': []
        })

    # 有数据的话再生成数据结构
    result = [
        {
            'id': item.id,
            'name': item.name
        } for item in mb_list
    ]

    # 然后返回给用户
    return get_res_json(code=200, data={
        'list': result
    })
