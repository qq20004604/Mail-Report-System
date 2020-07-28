#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 创建一个新的 up 主账号

import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..forms import UploaderCreate
from ..models import *
from ._utils import *


# 查询指定用户的消息
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_create(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = UploaderCreate(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 先获取当前用户的id
    owner = request.session.get('id', '')  # 当前用户
    # 获取创建的用户名
    uploader_name = uf.cleaned_data['uploader_name']

    # 检查当前用户是否有权限创建up主账号
    check_result = is_user_can_create_uploader(user_id=owner,
                                               uploader_name=uploader_name)
    # 返回结果不为True，则为错误提示信息
    if check_result is not True:
        return get_res_json(code=0, msg=check_result)

    # 创建账号，并返回提示信息
    if create_uploader_account(user_id=owner,
                               uploader_name=uploader_name) is True:
        return get_res_json(code=200)
    else:
        # 此时失败了
        return get_res_json(code=0, msg='创建失败，请重试或联系管理员')
