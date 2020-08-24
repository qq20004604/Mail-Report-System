#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.utils import timezone
from .models import RegVerifyMailModel, REG_EXPIRE_TIME
from package import mail_client


# 检查该用户当前是否可以推送验证码邮件
def can_send_regcode_email(email, ip):
    # 验证规则：
    # 1. 3 分钟内 1 封；
    # 2. 1 小时内 5 封；
    # 3. 24 小时 10 封；
    # 邮箱地址 和 ip 地址，分别查
    now = timezone.now().timestamp()
    first_check = RegVerifyMailModel.objects.filter(email=email, push_time__gt=now - 60 * 3)
    ip_check = RegVerifyMailModel.objects.filter(ip=ip, push_time__gt=now - 60 * 3)
    if len(first_check) > 0 or len(ip_check) > 0:
        return '3 分钟内只能发送 1 次验证邮件'

    second_check = RegVerifyMailModel.objects.filter(email=email, push_time__gt=now - 60 * 60)
    ip_check = RegVerifyMailModel.objects.filter(ip=ip, push_time__gt=now - 60 * 60)
    if len(second_check) >= 5 or len(ip_check) > 5:
        return '60 分钟内只能发送 5 次验证邮件'

    third_check = RegVerifyMailModel.objects.filter(email=email, push_time__gt=now - 60 * 60 * 24)
    ip_check = RegVerifyMailModel.objects.filter(ip=ip, push_time__gt=now - 60 * 60 * 24)
    if len(third_check) >= 10 or len(ip_check) > 10:
        return '24 小时内只能发送 10 次验证邮件'

    return None


# 检查邮件和验证码是否正确
def is_regcode_correct(email, regcode):
    now = timezone.now().timestamp()
    result = RegVerifyMailModel.objects.order_by('-id').filter(email=email, verify_code=regcode)
    if len(result) == 0:
        return '验证码错误'
    # 拿到最新一个
    result = result[0]
    # 检查时间是否过期
    if now - result.push_time > REG_EXPIRE_TIME:
        return '验证码已过期'
    return None


# 推送验证码邮件
def send_regcode_email(email, regcode):
    # send_result = mail_client.send_mail_test()
    send_result = mail_client.send_mail(receiver=[email],
                                        title='注册验证',
                                        content=[
                                            '<h4>',
                                            '你的邮箱注册验证码为：',
                                            '</h4>'
                                            '<h2>%s</h2>' % regcode
                                        ])
    print(send_result)
    return send_result


# 推送订阅邮件（都调用这个api推送）
def send_feeds_mail(receiver_list, title, content):
    send_result = mail_client.send_mail(receiver=receiver_list,
                                        title=title,
                                        content=content)
    print(send_result)
    return send_result


# 推送启动邮件邮件（都调用这个api推送）
def send_started_mail():
    send_result = mail_client.send_mail(receiver='20004604@qq.com',
                                        title='Mail Report System系统已启动',
                                        content=['Mail Report System系统已启动'])
    print(send_result)
    return send_result
