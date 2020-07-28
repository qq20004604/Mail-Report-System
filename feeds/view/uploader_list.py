#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit
from package.response_data import get_res_json
from ..forms import QueryUploaderListForm
from ..models import *
from ._utils import *
from config.variable import UPLOADER_PAGE_SIZE


# 加载用户列表
@my_csrf_decorator()
@post_limit
def uploader_list(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = QueryUploaderListForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 每页显示数量
    PAGE_SIZE = UPLOADER_PAGE_SIZE

    """
    整体逻辑：
    1. 先分页拿用户数据（排序顺序是最近发送消息的时间）；
    2. 根据用户id去查该用户最近发送的一条消息（已发送，并且未被删除的）；
    """

    # 拿到各个数据
    page = uf.cleaned_data['page']  # 页码数
    begin_index = (page - 1) * PAGE_SIZE
    end_index = page * PAGE_SIZE

    # 按最后推送时间排序
    mp_list = MsgPuber.objects.filter(allow_sub=True).order_by('-last_pub_time')
    total = len(mp_list)
    current_page = page

    # 如果没有数据
    if total == 0:
        # 返回
        return get_res_json(code=200, data={
            'page': {
                'total': total,
                'total_page': math.ceil(total / PAGE_SIZE),
                'current_page': current_page,
                'page_size': PAGE_SIZE
            },
            'list': []
        })

    # 加载数据
    up_list = mp_list[begin_index:end_index]

    result = []
    for mp_info in up_list:
        up_id = mp_info.id
        # 获取 UP主 信息
        d = get_msgpub_info(mp_info)
        # 当前用户是否已订阅
        d['had_user_sub'] = had_user_sub(request=request, upid=up_id)
        # 获取最近推送成功的消息，只取最后一个
        feed_list = Feeds.objects.filter(uploader_id=up_id,
                                         sendtime='done').order_by('-pub_time')[:1]
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

    # 返回
    return get_res_json(code=200, data={
        'page': {
            'total': total,
            'total_page': math.ceil(total / PAGE_SIZE),
            'current_page': current_page,
            'page_size': PAGE_SIZE
        },
        'list': result
    })
