#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ..forms import FeedSendByKeyForm
from ._utils import is_user_can_pub_feed, feed_send_now


# 发送信息（以密钥的形式）（方便第三方调用接口推送）
@my_csrf_decorator(True)
@post_limit
def feeds_send_by_key(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = FeedSendByKeyForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    """
    流程：
    1. 参考 feeds_send.py 里面的流程。
    """

    # 拿到各个数据
    upid = uf.cleaned_data['upid']  # UP主的id
    secret_key = uf.cleaned_data['secret_key']  # 密钥
    content = uf.cleaned_data['content']  # 消息体
    delay = uf.cleaned_data['delay']  # 发送情况：False 立即/True 延迟
    title = uf.cleaned_data['title']  # 标题（可选）

    # 必须有密钥，才能使用密钥推送
    mp_data = MsgPuber.objects.filter(secret_key=secret_key,
                                      id=upid)

    if len(mp_data) == 0:
        return get_res_json(code=100, msg='密钥错误，或该密钥对应的UP主不存在')

    mp_data = mp_data[0]

    owner = mp_data.user_id

    # 判断一下是否允许推送新消息
    is_can_pub = is_user_can_pub_feed(owner)

    if is_can_pub is not True:
        return get_res_json(code=0, msg=is_can_pub)

    # 创建一条新记录
    feed = Feeds.objects.create(user_id=owner,
                                uploader_id=upid,
                                content=content,
                                action_type='02')

    # 是否只是保存
    if delay:
        # 是保存
        feed.set_plan()
        feed.save()
        return get_res_json(code=200, msg='本条消息已保存成功')
    else:
        # 是立即推送
        send_result = feed_send_now(feed, mp_data, title=title)
        # 推送成功
        if send_result:
            return get_res_json(code=200, msg=send_result['msg'])
        else:
            return get_res_json(code=0, msg=send_result['msg'])
