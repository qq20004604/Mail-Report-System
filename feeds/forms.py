#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from package.form import Form, forms
from .models import FEED_MAX_LENGTH

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_sendtime(value):
    if value == 'now' or value == 'delay':
        return
    else:
        raise ValidationError(
            _('发送时间字段数据非法'),
            params={'value': value},
        )


def validate_uploader_name(value):
    if len(value.strip()) < 2 or (value[0] == ' ' or value[:-1] == ' '):
        raise ValidationError(
            _('【UP主名字】长度需需要在2~20位之间，且首尾不能为空格'),
            params={'value': value},
        )


# 创建新的up主
class UploaderCreate(Form):
    uploader_name = forms.CharField(label='uploader_name',
                                    required=True,
                                    min_length=2,
                                    max_length=20,
                                    validators=[
                                        validate_uploader_name
                                    ],
                                    error_messages={
                                        'required': '【UP主名字】长度需需要在2~20位之间',
                                        'max_length': '【UP主名字】长度需需要在2~20位之间',
                                        'min_length': '【UP主名字】长度需需要在2~20位之间',
                                    }
                                    )


# 请求某个up账号的详情以及他推送的信息
class QueryUploaderSelfDetailForm(Form):
    page = forms.IntegerField(label='page',
                              required=True,
                              min_value=1,
                              max_value=10000,
                              error_messages={
                                  'required': '请填写【页码】',
                                  'min_value': '【页码】应当大于等于1',
                                  'max_value': '【页码】应当小于等于10000'
                              }
                              )
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )


# 重置 UP 主密钥
class UploaderKeyRefreshForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )


# 修改 UP 主昵称
class UploaderNameEditForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )
    name = forms.CharField(label='name',
                           required=True,
                           min_length=2,
                           max_length=20,
                           validators=[
                               validate_uploader_name
                           ],
                           error_messages={
                               'required': '缺少【UP 主的新昵称】',
                               'max_length': '【UP 主的新昵称】长度需不能大于20位',
                               'min_length': '【UP 主的新昵称】长度最小为2位',
                           }
                           )


# 推送一条消息
class SendFeedForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )
    content = forms.CharField(label='msg',
                              min_length=1,
                              max_length=FEED_MAX_LENGTH,
                              required=True,
                              error_messages={
                                  'required': '你没有填写【消息内容】',
                                  'max_length': '【消息内容】长度需要在1~%s位之间' % FEED_MAX_LENGTH,
                                  'min_length': '【消息内容】长度需要在1~%s位之间' % FEED_MAX_LENGTH
                              }
                              )
    delay = forms.NullBooleanField(label='delay',
                                   required=True,
                                   error_messages={
                                       'required': '你没有填写【是否立即推送】',
                                   }
                                   )


# 请求所有推送过信息的用户
class QueryUploaderListForm(Form):
    page = forms.IntegerField(label='page',
                              required=True,
                              min_value=1,
                              max_value=10000,
                              error_messages={
                                  'required': '请填写【页码】',
                                  'min_value': '【页码】应当大于等于1',
                                  'max_value': '【页码】应当小于等于10000'
                              }
                              )


# 订阅某条消息主
class SubscribeForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )


# 获取某个 up 主的订阅者
class UploaderSuberlistForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )
    page = forms.IntegerField(label='page',
                              required=True,
                              min_value=1,
                              max_value=10000,
                              error_messages={
                                  'required': '请填写【页码】',
                                  'min_value': '【页码】应当大于等于1',
                                  'max_value': '【页码】应当小于等于10000'
                              }
                              )


# 其他人查看某UP主信息
class UploaderDetailByOthersForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '请填写【UP主id】'
                              }
                              )


# 某个 UP 主在 auth 为 02 的时候，修改订阅者是否能接受到自己的邮件
class SetUserRecForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '请填写【UP主id】'
                              }
                              )
    user_id = forms.IntegerField(label='user_id',
                                 required=True,
                                 min_value=1,
                                 error_messages={
                                     'required': '缺少【订阅者的 id】',
                                     'min_value': '【订阅者的 id】非法'
                                 }
                                 )


# ——————————以上为更新完成————————


# 新增消息流（密钥）
class FeedSendByKeyForm(Form):
    upid = forms.IntegerField(label='upid',
                              required=True,
                              error_messages={
                                  'required': '缺少【UP 主的 id】'
                              }
                              )
    content = forms.CharField(label='msg',
                              min_length=1,
                              max_length=FEED_MAX_LENGTH,
                              required=True,
                              error_messages={
                                  'required': '你没有填写【消息内容】',
                                  'max_length': '【消息内容】长度需要在1~%s位之间' % FEED_MAX_LENGTH,
                                  'min_length': '【消息内容】长度需要在1~%s位之间' % FEED_MAX_LENGTH
                              }
                              )
    # 可选
    title = forms.CharField(label='title',
                            max_length=20,
                            required=False,
                            error_messages={
                                'max_length': '【消息标题】长度应当小于 %s 位' % FEED_MAX_LENGTH,
                            }
                            )
    delay = forms.NullBooleanField(label='delay',
                                   required=True,
                                   error_messages={
                                       'required': '你没有填写【是否立即推送】',
                                   }
                                   )
    secret_key = forms.CharField(label='secret_key',
                                 required=True,
                                 max_length=20,
                                 min_length=20,
                                 error_messages={
                                     'required': '【密钥】错误',
                                     'min_length': '【密钥】错误',
                                     'max_length': '【密钥】错误',
                                 }
                                 )


# 查询历史消息
class QueryHistoryFeedsForm(Form):
    page = forms.IntegerField(label='page',
                              required=True,
                              min_value=1,
                              max_value=10000,
                              error_messages={
                                  'required': '请填写【页码】',
                                  'min_value': '【页码】应当大于等于1',
                                  'max_value': '【页码】应当小于等于10000'
                              }
                              )


def validate_rec_time(value):
    value_list = [
        '0000', '0100', '0200',
        '0300', '0400', '0500',
        '0600', '0700', '0800',
        '0900', '1000', '1100',
        '1200', '1300', '1400',
        '1500', '1600', '1700',
        '1800', '1900', '2000',
        '2100', '2200', '2300'
    ]
    if value in value_list:
        return
    else:
        raise ValidationError(
            _('接收推送时间 字段非法'),
            params={'value': value},
        )


# 修改当前用户的订阅信息
class UserSubscribeUpdateForm(Form):
    rec_time = forms.CharField(label='rec_time',
                               required=False,
                               validators=[
                                   validate_rec_time
                               ],
                               error_messages={
                                   'required': '接收推送时间 字段非法',
                               }
                               )
    is_active = forms.NullBooleanField(label='is_active',
                                       required=False
                                       )
