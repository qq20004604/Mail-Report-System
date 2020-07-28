#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ..forms import UploaderNameEditForm


# 更新 UP 主信息
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_name_edit(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = UploaderNameEditForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    owner = request.session.get('id', '')  # 当前用户
    # 拿到姓名，注意，这个姓名可能是空
    upid = uf.cleaned_data['upid']
    name = uf.cleaned_data['name']

    # 先查看有没有数据
    mp_data = MsgPuber.objects.filter(id=upid,
                                      user_id=owner)

    # 不存在，报错并返回
    if len(mp_data) == 0:
        return get_res_json(code=0, msg='该UP主并不存在')

    # 名字重复
    if len(MsgPuber.objects.filter(name=name)) > 0:
        return get_res_json(code=0, msg='已有同名账号，请使用其他名字')

    mp_data = mp_data[0]

    # 修改名字
    mp_data.set_name(name=name)

    # 保存
    mp_data.save()

    return get_res_json(code=200, msg='用户信息更新成功')
