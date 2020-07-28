#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from ..models import *
from ..forms import UploaderKeyRefreshForm


# 更新 UP 主信息
@my_csrf_decorator()
@post_limit
@login_limit
def uploader_key_refresh(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = UploaderKeyRefreshForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    owner = request.session.get('id', '')  # 当前用户

    # 拿到 up主的id
    upid = uf.cleaned_data['upid']

    # 校验用户，检查该用户是否存在
    mp_data = MsgPuber.objects.filter(id=upid,
                                      user_id=owner)

    # 不存在，报错并返回
    if len(mp_data) == 0:
        return get_res_json(code=0, msg='该UP主并不存在')

    mp_data = mp_data[0]
    # 重新生成密钥
    mp_data.make_secret_key()
    # 保存
    mp_data.save()

    return get_res_json(code=200, msg='密钥更新成功')
