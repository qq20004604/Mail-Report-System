#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config.variable import LOGIN_EXPIRE_TIME
from django.utils import timezone


# 设置登录状态
# 参数2是User model的一条数据
def set_user_session(request, user):
    request.session['id'] = user.id
    request.session['username'] = user.username
    request.session['last_login_timestamp'] = user.last_login.timestamp()


# 清除登录状态
def clear_session(request):
    request.session.flush()


# 登录是否过期
def was_expired(request):
    last_login_timestamp = request.session.get("last_login_timestamp")
    if timezone.now().timestamp() - last_login_timestamp > LOGIN_EXPIRE_TIME:
        return True
    else:
        return False


# 当前是否登录中
def is_logined(request):
    try:
        # 先查看有没有id
        if request.session.get('id') is None:
            # 没有显然是没登录
            return False
        else:
            # 再看登录是否过期
            if was_expired(request) is True:
                # 过期当然也是未登录咯
                clear_session(request)
                return False
            else:
                return True
    except BaseException as e:
        print(e)
        return False


# 测试和示例代码
if __name__ == '__main__':
    pass
