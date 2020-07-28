#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ..forms import SendFeedForm
from ._utils import is_user_can_pub_feed, feed_send_now


# 发送信息
@my_csrf_decorator()
@post_limit
@login_limit
def feeds_send(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = SendFeedForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    """
    流程：
    1. 拿取数据
    2. 检查该用户是否存在，以及是否是当前登录用户的up主
    2.1 不存在则返回报错信息
    3. 查看当前消息是否需要立即发布（delay == False）
    3.1 如果需要立即发布，首先设置 feed.set_plan() 设置状态，mp_data.set_last_pub() 更新发布时间
    3.1.1 调用立即发布的函数
    
    3.2 不是立即发布，调用 feed.set_send_delay() 设置为延迟推送
    4. 返回对应的提示信息
    
    """
    # todo 后期应当将立即发布这个行为，放入到线程池里去执行（即异步推送消息），提高响应速度

    # 拿到各个数据
    upid = uf.cleaned_data['upid']  # UP主的id
    content = uf.cleaned_data['content']  # 消息体
    delay = uf.cleaned_data['delay']  # 发送情况：立即/延迟
    owner = request.session.get('id', '')  # 当前用户

    # 如果该UP主并不存在，则返回报错提示信息（注意，这里要求up主id和其所属的userid是相符的）
    mp_data = MsgPuber.objects.filter(user_id=owner,
                                      id=upid)
    if len(mp_data) == 0:
        return get_res_json(code=0, msg='该UP主并不存在')

    mp_data = mp_data[0]

    # 判断一下是否允许推送新消息
    is_can_pub = is_user_can_pub_feed(owner)

    if is_can_pub is not True:
        return get_res_json(code=0, msg=is_can_pub)

    # 创建一条新记录
    feed = Feeds.objects.create(user_id=owner,
                                uploader_id=upid,
                                content=content)

    # 是否只是保存
    if delay:
        # 是保存
        feed.set_plan()
        feed.save()
        return get_res_json(code=200, msg='本条消息已保存成功')
    else:
        # 是立即推送
        send_result = feed_send_now(feed, mp_data)
        # 推送成功
        if send_result:
            return get_res_json(code=200, msg=send_result['msg'])
        else:
            return get_res_json(code=0, msg=send_result['msg'])
