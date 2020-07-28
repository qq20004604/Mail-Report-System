from django.db import models
from django.utils import timezone
from datetime import datetime
import hashlib
import random

# 单条消息最大长度
FEED_MAX_LENGTH = 2048

"""
    1. 一个用户可以有多个up主账号，对应不同业务；
    2. 只有高级用户才能创建up主账号，普通用户只能订阅；
    3. 目前需要手动在数据库修改某个用户的权限为高级用户（通过管理员权限修改的功能尚未添加）；
    4. 单条消息暂定最大长度为 2048
"""


# 消息发布者
# 基础数据继承于user
# 一个user可以有多个子 MsgPuber
class MsgPuber(models.Model):
    # class Meta:
    #     indexes = [models.Index(fields=['puber_id']),]

    # 发布者id，这个应该用外键才对，是 user.UserModel 这个表里的 id
    user_id = models.IntegerField(
        db_index=True,
        default=-1,
        help_text='该账号归属用户的id。这个指的是User表的id属性'
    )
    create_time = models.DateTimeField(
        default=timezone.now,
        help_text='账号创建时间'
    )
    last_pub_time = models.DateTimeField(
        default=timezone.now,
        help_text='最近一次推送消息的时间'
    )
    name = models.CharField(
        max_length=20,
        default='',
        help_text='UP主名字，最大长度20。不填不能推送消息'
    )
    secret_key = models.CharField(
        max_length=20,
        default='',
        help_text='秘钥，默认为空，有秘钥的情况下才能通过调用接口提交数据'
    )
    allow_sub = models.BooleanField(
        default=True,
        help_text='是否允许新用户订阅。（不允许的将无法被看到，取消订阅的人，也不允许再次订阅）'
                  '目前模式是 订阅者 订阅后，将收到推送邮件'
                  'todo 未来将新增允许 UP 主直接推送邮件给某些指定邮箱'
    )
    default_allow_rec = models.BooleanField(
        default=True,
        help_text='新用户订阅后，默认能否收取邮件'
                  'True为允许，即会修改 SubscribeFeeds.puber_allow_rec 默认值为 True'
    )

    # 修改最后推送消息时间
    def set_last_pub(self):
        self.last_pub_time = timezone.now()

    # 修改消息号名字
    def set_name(self, name):
        self.name = name

    # 生成秘钥
    def make_secret_key(self):
        sha1 = hashlib.sha1()
        # 用户id，随机数字，拼到一起生成hash
        sha1.update(('%s%s' % (self.user_id, str(random.random() * 1000))).encode('utf-8'))
        self.secret_key = sha1.hexdigest()[:20]


# 消息表
class Feeds(models.Model):
    user_id = models.IntegerField(
        db_index=True,
        default=-1,
        help_text='该账号归属用户的id。这个指的是User表的id属性'
    )
    uploader_id = models.IntegerField(
        db_index=True,
        default=-1,
        help_text='该消息发布者的用户id。这个指的是 MsgPuber 表的id属性'
    )
    pub_time = models.DateTimeField(
        default=timezone.now,
        help_text='消息推送的时间'
    )
    content = models.CharField(
        max_length=FEED_MAX_LENGTH,
        help_text='消息内容'
    )
    # 如果是用户订阅型（即根据用户订阅时间，去寻找订阅的 UP 主然后邮件推送）
    # 那么 plan、pushing、done，都被认为需要推送
    # 而 up 主发起立即推送，则需要根据推送情况修改状态
    sendtime = models.CharField(
        default='delay',
        max_length=15,
        help_text='该消息的推送状态：'
                  'delay 未要求推送（相当于只是保存了一下数据）'
                  'plan 在推送队列里（比如定时推送，或者正在推送中）'
                  'done 推送完毕'
                  'fail 推送失败'
    )
    action_type = models.CharField(
        default='01',
        max_length=2,
        help_text='01表示网页推送，02表示通过密钥推送'
    )

    # 设置为立即发送状态
    def set_plan(self):
        self.sendtime = 'plan'

    # 设置为已发送
    def set_sended(self):
        self.sendtime = 'done'

    # 设置为发送失败
    def set_send_failed(self):
        self.sendtime = 'fail'

    # 设置为延迟发布
    def set_send_delay(self):
        self.sendtime = 'delay'


# 订阅表
# 1、需要考虑2个情况，分别是邮件订阅和QQ订阅；
# 2、先只做邮件订阅（已登录订阅，之所以已登录订阅，是因为要防止垃圾信息骚扰）；
class SubscribeFeeds(models.Model):
    uploader_id = models.IntegerField(
        help_text='UP主的id（指MsgPuber表的id）'
    )
    user_id = models.IntegerField(
        default=-1,
        help_text='消息订阅者的id（指User表的id）'
    )
    sub_type = models.CharField(
        max_length=2,
        default='01',
        help_text='订阅类型：01，邮件订阅；02、QQ订阅（目前只支持邮件订阅）'
    )
    # qq = models.IntegerField(
    #     default=-1,
    #     help_text='消息订阅者的qq。只有qq订阅时才有效'
    # )
    sub_time = models.DateTimeField(
        default=timezone.now,
        help_text='订阅时间'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='该订阅是否生效中。'
    )
    puber_allow_rec = models.BooleanField(
        default=True,
        help_text='MsgPuber 是否允许该用户接受信息推送。up主可以禁止某个人能收到订阅邮件'
    )

    # 更新最近一次订阅时间
    def update_action_time(self):
        self.sub_time = timezone.now()


# 订阅/取消订阅历史表
class SubscribeHistory(models.Model):
    uploader_id = models.IntegerField(
        help_text='消息推送者的id（指MsgPuber表的id）'
    )
    user_id = models.IntegerField(
        default=-1,
        help_text='消息订阅者的id（指User表的id）'
    )
    # qq = models.IntegerField(
    #     default=-1,
    #     help_text='消息订阅者的qq。只有qq订阅时才有效'
    # )
    sub_type = models.CharField(
        max_length=2,
        default='01',
        help_text='订阅类型：01，邮件订阅；02、QQ订阅（目前只支持邮件订阅）'
    )
    action = models.CharField(
        max_length=2,
        default='01',
        help_text='订阅类型：01，订阅；02，取消订阅'
    )
    action_time = models.DateTimeField(
        default=timezone.now,
        help_text='订阅时间'
    )
