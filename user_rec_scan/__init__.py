#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import threading
from datetime import datetime
from feeds.models import *
from mail_pusher.models import *
from user.models import *
from mail_pusher.utils import send_feeds_mail, send_started_mail
from package.simple_log import log

MAX_CACHE_LENGTH = 24


# 自动邮件推送
class AutoMailPush(object):
    def __init__(self):
        # 创建新线程
        self.t = threading.Thread(target=self.loop, name='LoopThread')
        # 上一次触发事件的时间（小时）
        self.last_event_hour = -1
        self.statistics = {
            'time_cost': None,  # 时间耗费
            'begin_time': None,  # 开始执行的时间
            'end_time': None,  # 结束的时间
            'total_user': 0,  # 总共推送了多少个用户
            'total_feeds': 0,  # 总共推送了多少条消息（假如 A 收到邮件里有 2 条，B 收到邮件里有 3 条，那么这个就是 5）
            'fail_user': 0,  # 推送失败的用户数量
            'fail_msg': []  # 失败的原因，每个原因是一个元素
        }
        # 1、当前小时有推送，立即推送
        # 2、当前时间没有推送时，则存储起来；
        # 3、连续 MAX_CACHE_LENGTH 个小时没有推送信息，则推送一次（之前12个小时所有的信息）；
        # 这个就是那个存储的cache
        self.send_cache = []

    # 启动循环
    # 参数表示是否触发当前小时的事件，默认是否
    # 其实更好的方案是这里为 True，然后推送邮件的时候，检查一下该条信息是否推送过，如果没推送过，则去推送。
    def start(self, is_trigger_current_hour_event=False):
        print('AutoMailPush 开始运行')
        log('AutoMailPush 开始运行')
        # 先修改时间，再启动线程
        if is_trigger_current_hour_event is False:
            # 修改最近触发事件的时间为当前的小时数
            self.last_event_hour = datetime.now().hour

        self.t.start()
        # 推送服务启动成功邮件
        send_started_mail()

    # 线程启动后的函数
    def loop(self):
        while True:
            # 等待 10 秒，然后查看当前时间的小时，是否和上一次触发事件的小时数相符
            hour = datetime.now().hour
            # print('当前时间：%s 点' % hour)
            # 查看 hour 和 self.last_event_hour 是否相同，不相同则触发事件，最后修改 self.last_event_hour
            if hour == self.last_event_hour:
                time.sleep(10)
                continue
            else:
                print('开始查询当前时间收取订阅邮件的用户，并推送邮件')
                # 开始时间
                self.statistics['begin_time'] = datetime.now()

                # 开始执行函数
                self.run(hour)

                # 执行结束时间
                self.statistics['end_time'] = datetime.now()
                # 总计耗时（单位秒）
                self.statistics['time_cost'] = self.statistics['end_time'].timestamp() - self.statistics[
                    'begin_time'].timestamp()

                # 推送小结邮件
                self.send_summary(hour)
                # 重置数据
                self.reset_statistics()

                self.last_event_hour = hour

    # 推送日志邮件给我
    def send_summary(self, hour):
        # 先获取本轮是否有推送过
        is_round_have_sended = True if self.statistics['total_user'] == 0 else False

        # 组成文字
        text = [
            '<b>推送时间段：%s：00</b>' % str(hour).zfill(2)
        ]

        # 有推送则消息更多，无推送则不添加额外消息
        if is_round_have_sended:
            text += [
                '<p>推送用户 %s 人，推送消息 %s 条，推送失败为 %s 条</p>' % (
                    self.statistics['total_user'],
                    self.statistics['total_feeds'],
                    self.statistics['fail_user']
                ),
                '<p>推送开始时间：%s，推送结束时间：%s，总计耗时 %s 秒。</p>' % (
                    self.statistics['begin_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    self.statistics['end_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    self.statistics['time_cost'])
            ]

        # 有失败则追加失败原因到邮件中
        if len(self.statistics['fail_msg']) > 0:
            text.append('<p>失败原因：</p>')
            text += self.statistics['fail_msg']
        elif self.statistics['total_user'] == 0:
            text.append('本轮无推送')
        else:
            text.append('<b>本轮推送全部成功</b>')

        send_text = []
        log('当前时间：%s：00。self.send_cache的长度 %s 条。内容：\n————————————\n%s\n————————————' % (
            str(hour).zfill(2),
            len(self.send_cache),
            self.send_cache
        ))

        # 如果之前有缓存，则添加分割线
        if len(self.send_cache) > 0:
            text.append('<p>——————————————————————————————</p>')

        # 如果本轮未推送邮件
        if self.statistics['total_user'] == 0:
            # 将本轮内容追加到前面
            self.send_cache.insert(0, text)

            # 此时，若缓存尚未达到连续 MAX_CACHE_LENGTH 轮未推送邮件，则存起来，并返回（即本轮不推送总结邮件）
            if len(self.send_cache) < MAX_CACHE_LENGTH:
                return
            else:
                # 如果达到 MAX_CACHE_LENGTH 轮未推送邮件了，则一起推送
                # 拼接内容，一起推送
                for cache in self.send_cache:
                    send_text += cache
                    send_text += ['<br/>']
        else:
            # 如果本轮推送邮件了，先把本轮的内容放在最前面
            send_text += text
            send_text += ['<br/>']
            # 再追加缓存内容
            for cache in self.send_cache:
                send_text += cache
                send_text += ['<br/>']

        # 清空缓存
        log('清空缓存 self.send_cache')
        self.send_cache = []
        # 推送总结邮件
        summary_result = send_feeds_mail(receiver_list=['20004604@qq.com'],
                                         title='邮件推送总结',
                                         content=send_text)

        print(text)
        if summary_result.code != 200:
            with open('log/summary_result.log', 'a')as f: \
                    f.write('——————————————————\ns%s\n==================\n%s\n' % (
                        text,
                        summary_result.msg
                    ))

        # 重置数据

    def reset_statistics(self):
        self.statistics = {
            'time_cost': None,  # 时间耗费
            'begin_time': None,  # 开始执行的时间
            'end_time': None,  # 结束的时间
            'total_user': 0,  # 总共推送了多少个用户
            'total_feeds': 0,  # 总共推送了多少条消息（假如 A 收到邮件里有 2 条，B 收到邮件里有 3 条，那么这个就是 5）
            'fail_user': 0,  # 推送失败的用户数量
            'fail_msg': []  # 失败的原因，每个原因是一个元素
        }

    # 事件函数
    # 目前只考虑邮件订阅
    def run(self, hour):
        rec_time = '%s00' % str(hour).zfill(2)
        print(rec_time)
        # 整体逻辑查看 user_rec_scan.readme.md
        # 1. 拿到所有当前时间收取邮件的用户列表
        user_list = UserRecManage.objects.filter(rec_time=rec_time, is_active=True)
        send_info_list = []
        # 2.1 遍历用户列表
        for user in user_list:
            # 生成给该用户推送信息的所有数据
            # 注意：
            # 如果该用户没有订阅UP主，或该用户订阅的所有UP主都没有在最近24小时内推送消息，那么 send_info['content'] 为空
            send_info = self._get_user_mail_data(user)
            print(send_info)
            # 将该用户的信息添加进去
            send_info_list.append(send_info)

        # 然后用这个数据来推送邮件
        for send_info in send_info_list:
            self._send_mail(send_info)

        # 收工

    # 生成一个订阅用户推送邮件的所有数据
    def _get_user_mail_data(self, user):
        # 先找收件地址
        receiver = UserModel.objects.filter(id=user.user_id)[0].email

        # 此时有消息，那么说明需要推送给当前订阅用户
        send_info = {
            'receiver': receiver,  # 当前订阅用户的邮件地址
            'title': 'Feeds——每日订阅推送',  # 邮件标题，固定为：每日订阅邮件推送
            # content 是内容，组装一下。包括
            # [
            #   {
            #       'pub_name': up主，
            #       'upid': up主的id,
            #       'content': [],     # 是邮件内容（包括 [第一条24小时内发布的消息],[第二条消息...]）
            #   },
            #   {
            #       另一个up主...
            #   }
            # ]
            'content': [],
            'pub_records': []
        }
        # 2.2 查找 SubscribeFeeds 表，寻找该用户订阅的 up主，并且当前正在订阅中
        sf_list = SubscribeFeeds.objects.filter(suber_user=user.user_id, is_active=True, sub_type='01')
        # 然后拼接该up主的相关信息
        # 主要目的是为了根据订阅列表，查找订阅的up主最近24小时推送的内容，并且
        for sf in sf_list:
            # 拿到 upid
            upid = sf.upid
            # 3. 再去获取 MsgPuber 表 UP 主的信息，查看 auth='01' 的 UP 主
            mp_info = MsgPuber.objects.filter(id=upid, auth='01')
            if len(mp_info) == 0:
                # 如有数据则跳过这个 UP 主
                continue
            # 4. 找到符合的 UP 主
            mp_info = mp_info[0]
            # 5. 查该 up 主 Feeds 表里最近 24 个小时，sendtime='done' 的数据，组装起来；
            # 先获取 24 小时之前的时间
            t_lastday = datetime.now().timestamp() - 3600 * 24
            feeds_list = Feeds.objects.filter(upid=upid,
                                              sendtime='done',
                                              pub_time__gte=datetime.fromtimestamp(t_lastday))
            # 如果没有查到数据，则跳过
            if len(feeds_list) == 0:
                continue

            # 此时说明有up主，有 feed，那么组装数据
            content = []
            # 再开始拼装数据
            # 这个的目的是为了拼装每个up主的内容，以及生成推送记录
            for feed in feeds_list:
                content += [
                    # up主这里应该给个链接
                    '<a href="http://feeds.lovelovewall.com/lessfeeds.html?tab=user_list&upid=%s">UP主：%s</a>' % (
                        mp_info.id,
                        mp_info.pub_name if mp_info.pub_name else '无名氏'
                    ),
                    '<b>消息推送时间：</b>',
                    feed.pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                    '<b>内容：</b>',
                    feed.content
                ]
                if feed.href:
                    content += [
                        '<b>外链：</b>',
                        '<a href="%s">%s</a>' % (feed.href, feed.href)
                    ]
                # 新建推送记录
                pub_history = PuberMailPushHistory.objects.create(
                    rec_email=receiver,
                    puber_id=upid,
                    feed_id=feed.id
                )
                # 插入推送记录
                send_info['pub_records'].append(pub_history)

            # 将当前up主的消息，组装到content里（这样，send_info['content'] 可以直接作为 api 的 content 使用）
            send_info['content'] += content
            # 记得添加 2 个换行符
            send_info['content'] += ['<br/>', '<br/>']

        # 此时，我们顺利地得到了给一个订阅用户推送邮件的全部内容，现在返回他
        return send_info

    # 推送邮件
    def _send_mail(self, send_info):
        receiver = send_info['receiver']
        title = send_info['title']
        content = send_info['content']
        pub_records = send_info['pub_records']
        # 首先查看 content 是否有内容，如果没内容的话，说明无需推送
        if len(content) == 0:
            return
        # 计数加一
        self.statistics['total_user'] += 1
        self.statistics['total_feeds'] += len(pub_records)

        # 然后调用 api 推送邮件
        send_result = send_feeds_mail(receiver_list=[receiver],
                                      title=title,
                                      content=content)
        is_success = False
        # 推送成功
        if send_result.code == 200:
            is_success = True
        else:
            self.statistics['fail_msg'].append(send_result.msg)
        # 遍历推送记录，修改并保存
        for record in pub_records:
            record.pub_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            record.success = is_success
            record.save()


if __name__ == '__main__':
    amp = AutoMailPush()
    amp.start()
