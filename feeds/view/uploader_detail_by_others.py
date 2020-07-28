#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..forms import UploaderDetailByOthersForm
from ..models import *
from ._utils import *


# 其他人查看某UP主信息（只能查询最近一条已推送的信息）
@my_csrf_decorator()
@post_limit
def uploader_detail_by_others(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = UploaderDetailByOthersForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    upid = uf.cleaned_data['upid']  # 消息体

    mp_info = MsgPuber.objects.filter(id=upid)

    # 找不到该用户
    if len(mp_info) == 0:
        return get_res_json(code=0, msg='该 UP主 不存在', data={
            'uploader_info': None,
            'feed': None
        })

    mp_info = mp_info[0]
    uploader_info = get_msgpub_info(mp_info)

    feeds_list = Feeds.objects.order_by('-pub_time').filter(uploader_id=upid,
                                                            sendtime='done')

    # 如果查不到数据
    if len(feeds_list) == 0:
        return get_res_json(code=200, data={
            'uploader_info': uploader_info,
            'feed': None
        })

    last_feed = feeds_list[0]

    feed = {
        'id': last_feed.id,
        'pub_time': last_feed.pub_time.strftime("%Y-%m-%d %H:%M:%S"),
        'content': last_feed.content,
        'sendtime': get_sendtime_cn(last_feed.sendtime)
    }

    # 返回
    return get_res_json(code=200, data={
        'uploader_info': uploader_info,
        'feed': feed
    })
