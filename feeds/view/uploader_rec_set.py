#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..forms import SetUserRecForm
from ..models import *
from ._utils import *


# 查询当前用户的订阅者列表
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_rec_set(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = SetUserRecForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 流程梳理：
    # 1. 拿取订阅者 id 和 当前用户 id；
    # 2. 查看当前用户 MsgPuber 表的 auth 是不是 02
    # 2.1 不是 02，返回错误提示信息（没有权限修改）
    # 2.2 是 02，进入 3
    # 3. 查询订阅表 SubscribeFeeds 表，修改 puber_allow_rec 为相反的值
    # 4. 保存，返回信息

    # 拿取数据
    upid = uf.cleaned_data['upid']
    user_id = uf.cleaned_data['user_id']
    owner = request.session.get('id', '')  # 当前用户

    # 先校验该用户有无权限对该up主进行操作
    mp_info = MsgPuber.objects.filter(id=upid, user_id=owner)
    if len(mp_info) == 0:
        return get_res_json(code=0, msg='UP 主不存在或你无权限对该用户进行操作')

    # 获取订阅信息。只能对生效中的进行操作
    # （若想禁止曾经订阅过但现在取消的人，请禁止用户订阅）
    # todo 有一种场景，是你想默认禁止用户订阅，只允许你打开权限的人收取邮件。
    #  这个需要后期添加一个接口，修改订阅后，puber_allow_rec 默认为 False）
    #  目前默认是 True——即允许收取
    sub_info = SubscribeFeeds.objects.filter(uploader_id=upid,
                                             user_id=user_id)

    if len(sub_info) == 0:
        return get_res_json(code=0, msg='该用户并未订阅，无法进行操作')

    sub_info = sub_info[0]
    sub_info.puber_allow_rec = bool(1 - sub_info.puber_allow_rec)
    sub_info.save()

    return get_res_json(code=200, msg='订阅者 id 为：%s 的 接受邮件权限 修改成功' % user_id)
