#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 装饰器：接口请求方式限制
from package.response_data import get_res_json
from package.session_manage import is_logined


# 加了这个装饰器后，如果请求方式不是post，那么自动返回错误信息
def post_limit(func):
    def wrapper(*args, **kw):
        request = args[0]
        if request.method != 'POST':
            return get_res_json(code=0, msg='请使用POST方式请求')
        return func(*args, **kw)

    return wrapper


# 加了这个装饰器后，如果请求方式不是post，那么自动返回错误信息
def get_limit(func):
    def wrapper(*args, **kw):
        request = args[0]
        if request.method != 'GET':
            return get_res_json(code=0, msg='请使用POST方式请求')
        return func(*args, **kw)

    return wrapper


# 登录限制。如果用户没有登录，则自动返回错误信息
def login_limit(func):
    def wrapper(*args, **kw):
        request = args[0]
        if is_logined(request) is False:
            return get_res_json(code=5, msg='请先登录')
        return func(*args, **kw)

    return wrapper
