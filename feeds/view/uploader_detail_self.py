#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..forms import QueryUploaderSelfDetailForm
from ..models import *
from ._utils import *


# 查询当前用户的详细信息和推送的历史记录
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_detail_self(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = QueryUploaderSelfDetailForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 每页显示数量（默认100）
    PAGE_SIZE = 100

    owner = request.session.get('id', '')  # 当前用户
    upid = uf.cleaned_data['upid']  # 当前up账号的id
    page = uf.cleaned_data.get('page', 1)  # 页码数

    # 拿到当前用户信息 （同时进行用户权限校验）
    mp_info = MsgPuber.objects.filter(id=upid, user_id=owner)

    # 找不到该用户
    if len(mp_info) == 0:
        return get_res_json(code=200, msg='该用户信息不存在', data={
            'uploader_info': None,
            'page': {
                'total': 0,  # 总数
                'total_page': 1,  # 一共多少页
                'current_page': 1,  # 当前第几页
                'page_size': PAGE_SIZE,  # 每页多少个
            },
            'feeds': []
        })

    mp_info = mp_info[0]
    # 获取up主的相关信息
    uploader_info = get_msgpub_info(mp_info, has_key=True)

    # 有用户，那么去找他推送的消息
    query_result = Feeds.objects.filter(uploader_id=upid).order_by('-id')

    total = len(query_result)
    # 如果查不到数据
    if total == 0:
        return get_res_json(code=200, msg='您未发布过任何消息', data={
            'uploader_info': uploader_info,
            'page': {
                'total': 0,  # 总数
                'total_page': 1,  # 一共多少页
                'current_page': 1,  # 当前第几页
                'page_size': PAGE_SIZE,  # 每页多少个
            },
            'feeds': []
        })

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
    feeds_list = [
        {
            'id': item.id,
            'pub_time': item.pub_time.strftime('%Y-%m-%d %H:%M:%S'),
            'content': item.content,
            'sendtime': get_sendtime_cn(item.sendtime),  # 消息状态（后端手动转换后推送给前端）
            'action_type': get_action_type_cn(item.action_type)
        } for item in query_result
    ]

    # 返回
    return get_res_json(code=200, data={
        'uploader_info': uploader_info,
        'page': page_info,
        'feeds': feeds_list
    })
