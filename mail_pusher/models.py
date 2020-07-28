from django.db import models
from django.utils import timezone
from datetime import datetime
import hashlib
import random


def make_verify_code():
    return str(random.randint(1, 999999)).zfill(6)


# 验证码过期时间（10 分钟）
REG_EXPIRE_TIME = 60 * 10


def get_now_time():
    return timezone.now().timestamp()


# Create your models here.
# 用户注册邮箱验证
class RegVerifyMailModel(models.Model):
    email = models.EmailField(
        max_length=100,
        help_text='注册邮箱'
    )
    push_time = models.IntegerField(
        default=get_now_time,
        help_text='用户注册时间'
    )
    verify_code = models.CharField(
        max_length=6,
        default=make_verify_code,
        help_text='验证码'
    )
    invalid = models.BooleanField(
        default=False,
        help_text='是否失效。该注册验证码使用后，失效'
    )
    ip = models.CharField(
        max_length=20,
        default='',
        help_text='ip 地址'
    )

    def __str__(self):
        return '%s|%s' % (self.email, self.verify_code)

    # 验证码是否过期
    def was_expired(self):
        if timezone.now().timestamp() - self.push_time > REG_EXPIRE_TIME:
            return True
        else:
            return False


# 订阅邮件推送历史记录。
class PuberMailPushHistory(models.Model):
    rec_email = models.EmailField(
        max_length=100,
        help_text='注册邮箱'
    )
    uploader_id = models.IntegerField(
        help_text='消息推送者的id（指MsgPuber表的id）'
    )
    feed_id = models.IntegerField(
        help_text='消息id（指Feeds表的id）'
    )
    pub_time = models.DateTimeField(
        default=timezone.now,
        help_text='邮件推送的时间'
    )
    success = models.BooleanField(
        default=True,
        help_text='是否推送成功'
    )
