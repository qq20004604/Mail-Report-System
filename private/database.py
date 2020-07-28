#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SQL命令，初始化权限
# GRANT ALL ON report_db.* to report_admin@'%' IDENTIFIED BY '123456';
# FLUSH PRIVILEGES;

# 注意，这个数据是我自己的，仅供参考，实际开发需要根据你自己的环境配置。
DBCONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'report_db',  # 数据库名，先前创建的
    'USER': 'report_admin',  # 用户名，可以自己创建用户
    'PASSWORD': '123456',  # 密码
    'HOST': '172.19.0.1',  # mysql服务所在的主机ip（注意，我这个是因为在线上跑的，所以ip是docker network的地址）
    'PORT': '3306',  # mysql服务端口
    'OPTIONS': {
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    }
}
