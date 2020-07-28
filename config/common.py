#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Server.settings import REMOTE_MODEL

"""
    服务的配置选项
    说明：
    1. 这里是有效的，用于配置和QQ服务对接的一些全局配置变量，方便管理；
"""
# 基础 HOST
# HOST = 'qqrobot'
HOST = '172.20.0.9'
if REMOTE_MODEL is True:
    HOST = '172.18.0.1'
