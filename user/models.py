from django.db import models
from django.utils import timezone
from datetime import datetime
import hashlib

# 盐
SALT = 'qweabc'


# 用户数据模型
class UserModel(models.Model):
    username = models.CharField(
        max_length=20,
        unique=True,
        help_text='用户昵称（2~20位）'
    )
    password = models.CharField(
        max_length=40,
        help_text='密码（8~40位），最终以hash的形式存储，固定40位，查找form表单，hashlib.sha1()'
    )
    register_date = models.DateTimeField(
        default=timezone.now,
        help_text='用户注册时间'
    )
    last_login = models.DateTimeField(
        default=timezone.now,
        help_text='最近一次登录时间'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='该账号是否生效'
    )
    # user_type = models.CharField(
    #     max_length=2,
    #     help_text='用户类型。1.私聊；2.群组；'
    # )
    email = models.CharField(
        default='',
        max_length=100,
        help_text='注册邮箱'
    )
    user_permission = models.CharField(
        default='01',
        max_length=2,
        help_text='用户类型：'
                  '01.普通（只能接受邮件）；'
                  '02.高级用户（可以接受和创建up主账号）；'
                  '10.管理员（未设计）；'
                  '11.超级管理员（未设计）；'
    )

    # 显示的默认信息
    def __str__(self):
        return self.username

    # 生成hash密码
    def set_pw(self, pw):
        sha1 = hashlib.sha1()
        # 用户名、密码、盐 拼到一起生成hash
        sha1.update(('%s%s%s' % (self.username, pw, SALT)).encode('utf-8'))
        self.password = sha1.hexdigest()

    # 密码是否正确
    def is_pw_correct(self, pw):
        sha1 = hashlib.sha1()
        # 用户名、密码、盐 拼到一起生成hash
        sha1.update(('%s%s%s' % (self.username, pw, SALT)).encode('utf-8'))
        return self.password == sha1.hexdigest()

    # 修改最后登录时间
    def set_last_login(self):
        self.last_login = timezone.now()
