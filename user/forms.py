#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from package.form import Form, forms


# 发送注册验证码
class SendRegCodeForm(Form):
    username = forms.CharField(label='username',
                               min_length=2,
                               max_length=20,
                               required=True,
                               error_messages={
                                   'required': '你没有填写【用户名】',
                                   'max_length': '【用户名】长度需要在2~20位之间',
                                   'min_length': '【用户名】长度需要在2~20位之间'
                               }
                               )
    email = forms.EmailField(label='email',
                             min_length=6,
                             max_length=80,
                             required=True,
                             error_messages={
                                 'required': '你没有填写【邮箱地址】',
                                 'max_length': '【邮箱地址】长度需要在6~80位之间',
                                 'min_length': '【邮箱地址】长度需要在6~80位之间'
                             })


# 注册
class RegisterForm(Form):
    username = forms.CharField(label='username',
                               min_length=2,
                               max_length=20,
                               required=True,
                               error_messages={
                                   'required': '你没有填写【用户名】',
                                   'max_length': '【用户名】长度需要在2~20位之间',
                                   'min_length': '【用户名】长度需要在2~20位之间'
                               }
                               )
    password = forms.CharField(label='password',
                               min_length=8,
                               max_length=40,
                               required=True,
                               error_messages={
                                   'required': '你没有填写【密码】',
                                   'max_length': '【密码】长度需要在8~40位之间',
                                   'min_length': '【密码】长度需要在8~40位之间'
                               }
                               )
    email = forms.EmailField(label='email',
                             min_length=6,
                             max_length=80,
                             required=True,
                             error_messages={
                                 'required': '你没有填写【邮箱地址】',
                                 'max_length': '【邮箱地址】长度需要在6~80位之间',
                                 'min_length': '【邮箱地址】长度需要在6~80位之间'
                             })
    regcode = forms.CharField(label='regcode',
                              min_length=6,
                              max_length=6,
                              required=True,
                              error_messages={
                                  'required': '你没有填写【验证码】',
                                  'max_length': '【验证码】格式错误',
                                  'min_length': '【验证码】格式错误'
                              })


# 登录
class LoginForm(Form):
    username = forms.CharField(label='username',
                               min_length=2,
                               max_length=20,
                               required=True,
                               error_messages={
                                   'required': '你没有填写【用户名】',
                                   'max_length': '【用户名】长度需要在2~20位之间',
                                   'min_length': '【用户名】长度需要在2~20位之间'
                               }
                               )
    password = forms.CharField(label='password',
                               min_length=8,
                               max_length=40,
                               required=True,
                               error_messages={
                                   'required': '你没有填写【密码】',
                                   'max_length': '【密码】长度需要在8~40位之间',
                                   'min_length': '【密码】长度需要在8~40位之间'
                               }
                               )
