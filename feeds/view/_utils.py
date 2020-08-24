#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ..models import *
from django.utils import timezone
from django.db.models import Q
from user.models import UserModel
from mail_pusher.models import PuberMailPushHistory
from mail_pusher.utils import send_feeds_mail
from package.simple_log import log
from package.get_time import get_date_time
from config.switch import USER_FEED_SEND_LIMIT
from config.variable import USER_FEED_SEND_LIMIT_COUNT


def get_sendtime_cn(sendtime):
    kv = {
        'delay': '未要求推送',
        'plan': '推送中',
        'done': '推送完毕',
        'fail': '推送失败'
    }
    if sendtime in kv:
        return kv[sendtime]
    else:
        return '未知状态'


# 获取用户权限的中文名
def get_user_permission_cn(user_permission):
    kv = {
        '01': '普通用户（只能接收邮件）',
        '02': '高级用户（可以接收邮件和创建up主账号）',
        '10': '管理员',
        '11': '超级管理员',
    }
    if user_permission in kv:
        return kv[user_permission]
    else:
        return '未知用户'


# 能否创建 up 主账号。其实应该做个权限表的，但是我懒
def can_create_uploader(user_permission):
    kv = {
        '01': False,
        '02': True,
        '10': False,
        '11': False,
    }
    if user_permission in kv:
        return kv[user_permission]
    else:
        return False


# 获取推送方式的中文版
def get_action_type_cn(action_type):
    kv = {
        '01': '网页推送',
        '02': '密钥推送'
    }
    return kv[action_type]


# 获取订阅类型的中文版
def get_sub_type_cn(sub_type):
    kv = {
        '01': '邮件订阅',
        '02': 'QQ订阅'
    }
    if sub_type in kv:
        return kv[sub_type]
    else:
        return '未知订阅模式'


# 返回该用户信息
def get_msgpub_info(mp_info, has_key=False):
    d = {
        'id': mp_info.id,
        'user_id': mp_info.user_id,
        'create_time': mp_info.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'last_pub_time': mp_info.last_pub_time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': mp_info.name,
        'default_allow_rec': mp_info.default_allow_rec,
        'allow_sub': mp_info.allow_sub
    }
    if has_key is True:
        d['secret_key'] = mp_info.secret_key
    return d


# 返回该用户是否已订阅
def had_user_sub(request, upid):
    # 1. 先拿到用户id——没拿到就直接返回False
    # 2. 用户id + up主ID 去查 SubscribeFeeds 表
    # 2.1 没数据，返回False
    # 2.2 有数据，但 is_active 为 True ，返回 True
    # 3. 返回 False
    user_id = request.session.get('id', None)  # 当前用户
    if user_id is None:
        return False
    user_id = int(user_id)
    sf_info = SubscribeFeeds.objects.filter(uploader_id=upid, user_id=user_id)
    if len(sf_info) == 0:
        return False

    sf_info = sf_info[0]
    if sf_info.is_active is True:
        return True
    else:
        return False


# 用户当前是否可以推送新消息
# 可以推送返回 True，否则返回 错误提示信息
def is_user_can_pub_feed(user_id):
    # 流程分析
    # 1. 查User表，拿到权限，然后调用 can_create_uploader 查看是否能推送消息（能创建up主账号的就能推送消息）
    # 2. 理论上应该区分更多用户权限，比如某些用户每日只能推送一个，某些用户可以推送多个之类的。
    # 3. 之所以查一次表，是为了在后期管理员可以禁止某些用户推送邮件
    # 4. 【特殊限制】每个用户，多个up主账号，加起来每日最多只能推送 3 次消息

    user_info = UserModel.objects.filter(id=user_id)[0]
    can_create = can_create_uploader(user_info.user_permission)
    # 不能则返回
    if can_create is False:
        return '你被禁止推送新消息，请联系管理员'

    # 如果限制开关没有打开，则此时返回允许推送新消息
    if USER_FEED_SEND_LIMIT is False:
        return True

    # 拿到时间
    d = timezone.now()
    # 筛选当前用户，今日，推送中或推送成功
    feeds_list = Feeds.objects. \
        filter(user_id=user_id). \
        filter(Q(sendtime='plan') | Q(sendtime='done')). \
        filter(pub_time__year=d.year,
               pub_time__month=d.month,
               pub_time__day=d.day)

    # 查看数量是否超过上限
    if len(feeds_list) >= USER_FEED_SEND_LIMIT_COUNT:
        return '你今日推送邮件已达到上限：%s' % USER_FEED_SEND_LIMIT_COUNT
    else:
        return True


# 立即推送消息
def feed_send_now(feed, mp_data, title=''):
    # 是立即推送
    feed.set_plan()
    # 调用邮件推送的 api
    push_result = push_mail(feed_id=feed.id, title=title)
    # 推送成功
    if push_result['code'] == 200:
        # 设置为已推送
        feed.set_sended()
        feed.save()
        # 更新该up主最近推送时间
        mp_data.set_last_pub()
        mp_data.save()
        return push_result
    else:
        # 失败
        # 设置本条消息为推送失败
        feed.set_send_failed()
        feed.save()
        return push_result


# 推送邮件给订阅者
# 推送失败则返回 False
def push_mail(feed_id, title=''):
    # 流程
    # 1. 根据 feed_id 查 Feeds 表拿到 user_id，uploader_id，pub_time，content。
    # 2. 用 uploader_id 查 MsgPuber 表拿到 name
    # 3. 用 uploader_id 查 SubscribeFeeds 表，条件为 is_active=True，sub_type='01'，
    #       拿到所有订阅该 up 主 的 user_id
    # 4. 根据 user_id 查 User 表，拿到该用户的邮箱（没有邮箱则被忽略）
    # 5. 用邮箱组成一个 list，作为邮件接受者
    # 6. 用 name，pub_time，content 等拼装邮件的 content
    # 7. 推送邮件，拿到推送结果（假如有一个邮件地址是错的，那么所有的都不会被推送）
    #       （不过理论上不可能，因为用户是需要收取邮件验证码后才能注册成功的）。
    # 8. 并写下日志，返回推送结果

    # 1
    feed = Feeds.objects.filter(id=feed_id)[0]
    mail_info = {
        'user_id': feed.user_id,
        'uploader_id': feed.uploader_id,
        'pub_time': feed.pub_time.strftime('%Y-%m-%d %H:%M:%S'),
        'content': feed.content,
        'name': None
    }
    # 2
    puber_info = MsgPuber.objects.filter(id=mail_info['uploader_id'])[0]
    mail_info['name'] = puber_info.name

    # 3 找到订阅者列表，（订阅者订阅中 + 当前模式是邮件订阅）
    suber_list = SubscribeFeeds.objects.filter(uploader_id=mail_info['uploader_id'],
                                               is_active=True,
                                               puber_allow_rec=True,
                                               sub_type='01')
    # 如果没有人订阅，直接返回 0 表示推送成功，但是推送了 0 个订阅者
    if len(suber_list) == 0:
        return {
            'code': 200,
            'msg': '你成功推送了消息给 0 位邮件订阅者'
        }

    suber_id_list = [
        item.user_id for item in suber_list
    ]

    # 5 搞一个接受这次推送的邮件列表
    suber_mail_list = []
    for user_id in suber_id_list:
        user_info = UserModel.objects.filter(id=user_id)[0]
        if user_info.email:
            suber_mail_list.append(user_info.email)

    # 6 拼装邮件内容
    content = [
        # up主这里应该给个链接
        '<a href="http://report.lovelovewall.com/?upid=%s">UP主：%s</a>' % (
            mail_info['uploader_id'],
            mail_info['name']
        ),
        '<b>消息推送时间：</b>',
        mail_info['pub_time'],
        '<b>消息推送类型：</b>',
        '立即推送',
        '<b>内容：</b>',
        mail_info['content']
    ]

    send_result = send_feeds_mail(receiver_list=suber_mail_list,
                                  title='%s。UP主：%s' % (title, mail_info['name']),
                                  content=content)

    is_success = False
    if send_result.code == 200:
        is_success = True
    else:
        # 如果推送失败，则写一个失败日志
        with open('log/push_mail_fail.log', 'a')as f:
            f.write('time:%s||receiver:%s||feed_id:%s||fail_reason:%s\n' % (
                mail_info['pub_time'],
                str(suber_mail_list),
                feed_id,
                send_result.msg
            ))

    # 根据返回信息写入邮件推送记录
    for mail in suber_mail_list:
        PuberMailPushHistory.objects.create(rec_email=mail,
                                            uploader_id=mail_info['uploader_id'],
                                            feed_id=feed_id,
                                            pub_time=mail_info['pub_time'],
                                            success=is_success).save()

    if is_success is False:
        return {
            'code': 0,
            'msg': send_result.msg
        }
    else:
        return {
            'code': 200,
            'msg': '你成功推送了消息给 %s 位邮件订阅者' % len(suber_mail_list)
        }


# 检查当前用户是否能创建up主账号
def is_user_can_create_uploader(user_id, uploader_name):
    user_info = UserModel.objects.filter(id=user_id)
    # 其实应该不可能等于0
    if len(user_info) == 0:
        return '未知错误'
    user_info = user_info[0]
    if user_info.user_permission != '02':
        return '当前用户无权限创建up主账号，请联系管理员'
    if len(MsgPuber.objects.filter(name=uploader_name)) > 0:
        return '已有同名账号，请使用其他名字'
    return True


# 创建 up 主账号
def create_uploader_account(user_id, uploader_name):
    try:
        mb = MsgPuber.objects.create(user_id=user_id,
                                     name=uploader_name)
        mb.make_secret_key()
        mb.save()
    except BaseException as e:
        log('%s：创建用户账号失败，user_id=%s，uploader_name=%s，报错信息：%s' % (
            get_date_time(),
            user_id,
            uploader_name,
            str(e))
            )
        return False
    return True
