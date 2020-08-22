## 说明

本文件夹内的相关功能，用于定时扫描数据库表，查找符合条件的用户，并对其发送其订阅的时间。

具体来说：

1. 当时间到达整点时，扫描 feeds.UserRecManage 表，查看字段 rec_time='当前时间' and is_active = true 的用户。
2. 扫描 SubscribeFeeds 表，该用户订阅的所有 UP 主。具体来说，是 is_active=True 的数据；
3. 再去获取 MsgPuber 表 UP 主的信息，查看 auth='01' 的 UP 主。
4. 当某个 UP 主 MsgPuber.auth='01'，SubscribeFeeds.is_active=True，说明该 UP 主符合条件；
5. 再用该 UP 主的 id 去扫描 feeds.Feeds 表，寻找 pub_time 是最近 24 个小时，sendtime='done' 的数据，组装起来；
6. 根据 4 和 5，可以获取到某个用户订阅的所有 UP 主最近 24 小时推送的消息，然后拼装起来，推送给用户。将邮件推送记录写入mail_push.PuberMailPushHistory 表。
7. 再根据 1，重复 2-6，依次推送每个用户的邮件。
8. 记录整体推送耗费时间，写一个总结，推送邮件给管理员（比如我自己）；
