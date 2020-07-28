#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .models import UserModel


# 该邮箱地址是否已注册
def is_can_reg(username, email):
    if len(UserModel.objects.filter(username=username)) > 0:
        return '用户名已注册'

    if len(UserModel.objects.filter(email=email)) > 0:
        return '邮箱已注册'

    return None
