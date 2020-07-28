#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ..forms import SubscribeForm


# 订阅 UP 主
@my_csrf_decorator()
@post_limit
@login_limit
def user_subscribe(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = SubscribeForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    """
    流程：
    1. 拿到被订阅者id和订阅类型；
    2. 检测是QQ订阅还是邮件订阅；
    2.1 如果是QQ订阅，则检查QQ字段是否存在，没有则报错；
    3. 插入订阅信息到 Subscribe 表
    4 检查 UserRecManage 表，如果没有该用户信息，则新建一条该用户信息
    5. 插入一条记录到 SubscribeHistory 表
    """

    # 拿到各个数据
    upid = uf.cleaned_data['upid']  # 被订阅者
    user_id = request.session.get('id', '')  # 当前用户

    # 先查该 up 主是否允许被订阅
    mp_info = MsgPuber.objects.filter(id=upid)
    if len(mp_info) == 0:
        return get_res_json(code=0, msg='该 up 主不存在。该UP主id为：%s' % upid)
    if mp_info[0].allow_sub is False:
        return get_res_json(code=0, msg='该 up 主不允许被订阅。该UP主id为：%s' % upid)

    # 先找该用户之前有没有订阅过这个消息号
    sf_result = SubscribeFeeds.objects.filter(uploader_id=upid,
                                              user_id=user_id)

    # 如果查到，则说明他订阅过
    if len(sf_result) > 0:
        sf_result = sf_result[0]
        # 如果是True，说明当前正处于订阅中
        if sf_result.is_active is True:
            return get_res_json(code=0, msg='你已经订阅了，无需重复订阅。该UP主id为：%s' % upid)
        else:
            sf_result.is_active = True
            # 每次订阅时，都修改当前订阅状态为up主默认的是否允许收取该邮件
            sf_result.puber_allow_rec = mp_info[0].default_allow_rec
            sf_result.update_action_time()
            sf_result.save()

            # 插入一条历史订阅记录
            SubscribeHistory.objects.create(uploader_id=upid,
                                            user_id=user_id).save()

            return get_res_json(code=200, msg='你已成功重新订阅，该UP主的id为：%s' % upid)
    else:
        # 如果没有订阅过，则插入一条新的记录
        SubscribeFeeds.objects.create(uploader_id=upid,
                                      user_id=user_id,
                                      puber_allow_rec=mp_info[0].default_allow_rec).save()
        # 插入一条历史记录
        SubscribeHistory.objects.create(uploader_id=upid,
                                        user_id=user_id).save()
        return get_res_json(code=200, msg='你已成功订阅，该UP主id为：%s' % upid)
