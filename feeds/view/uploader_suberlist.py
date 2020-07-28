#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
import re
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from config.variable import UPLOADER_SUBSCRIBE_LIST_PAGE_SIZE
from ..forms import UploaderSuberlistForm
from ..models import *
from ._utils import *


# 查询当前用户的订阅者列表（只有 up 主自己可以看到）
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_suberlist(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = UploaderSuberlistForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 每页显示数量
    PAGE_SIZE = UPLOADER_SUBSCRIBE_LIST_PAGE_SIZE

    owner = request.session.get('id', '')  # 当前用户
    upid = uf.cleaned_data['upid']  # up 主 id
    page = uf.cleaned_data['page']  # 第几页

    mp_info = MsgPuber.objects.filter(id=upid,
                                      user_id=owner)
    # 找不到该用户
    if len(mp_info) == 0:
        return get_res_json(code=0, msg='该用户信息不存在')

    # 找该用户的订阅者（只能找到当前订阅中的）
    query_result = SubscribeFeeds.objects.filter(uploader_id=upid,
                                                 is_active=True).order_by('-id')

    total = len(query_result)
    # 如果查不到数据
    if total == 0:
        return get_res_json(code=200, data={
            'page': {
                'total': 0,  # 总数
                'total_page': 0,  # 一共多少页
                'current_page': page,  # 当前第几页
                'page_size': PAGE_SIZE,  # 每页多少个
            },
            'list': []
        })

    # 分页
    begin_index = (page - 1) * PAGE_SIZE
    end_index = page * PAGE_SIZE
    query_result = query_result[begin_index:end_index]

    page_info = {
        'total': total,  # 总数
        'total_page': math.ceil(total / PAGE_SIZE),  # 一共多少页
        'current_page': page,  # 当前第几页
        'page_size': PAGE_SIZE,  # 每页多少个
    }

    # 拼装数据
    suber_list = [
        {
            'uploader_id': item.uploader_id,
            'user_id': item.user_id,
            'email': '',  # 用户邮箱，要去查 User 表
            'user_name': '',  # 用户名，要去查 User 表
            'sub_type': get_sub_type_cn(item.sub_type),
            'sub_time': item.sub_time.strftime('%Y-%m-%d %H:%M:%S'),
            'puber_allow_rec': item.puber_allow_rec
        } for item in query_result
    ]

    for suber in suber_list:
        user_id = suber['user_id']
        user_info = UserModel.objects.filter(id=user_id)[0]
        # 给 email 打码（@后全部打码）
        email = user_info.email
        email_sign_index = re.search('@', email).span()[0]
        email = email[:email_sign_index] + '@xxx.xxx'
        suber['email'] = email
        # 给用户名打码（最后 6 位打码）
        username = user_info.username
        username = username[:-6] + 'xxxxxx'
        suber['user_name'] = username

    # 返回
    return get_res_json(code=200, data={
        'page': page_info,
        'list': suber_list
    })
