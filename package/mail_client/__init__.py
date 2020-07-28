#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import grpc
import time
from Server.settings import MY_PRIVATE
from package.mail_client import mail_pb2
from package.mail_client import mail_pb2_grpc

PORT = 0
HOST = '0.0.0.0'
SECRET_KEY = ''

if MY_PRIVATE:
    from private.mail_server_config import PORT, HOST, SECRET_KEY


# 记录请求发送邮件的日志
def log_mail_request(receiver, title, content):
    with open('log/mail_client_send.log', 'a')as f:
        f.write('time:%s||receiver:%s||title:%s||content:%s\n' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            receiver, title, content
        ))


# 记录请求发送邮件的日志
def log_mail_request_err(receiver, title, content, secretkey, err):
    with open('log/mail_client_send_err.log', 'a')as f:
        f.write('time:%s||receiver:%s||title:%s||content:%s||secretkey:%s||err:%s\n' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            receiver, title, content, secretkey, err
        ))


# RPC专用类（客户端）
class GRPCClient(object):
    def __init__(self):
        server = '%s:%s' % (HOST, PORT)
        # 连接 rpc 服务器
        channel = grpc.insecure_channel(server)
        # 调用 rpc 服务，XxxxxStub 这个类名是固定生成的，参照 mail_pb2_grpc.py
        self.stub = mail_pb2_grpc.MailManagerServiceStub(channel)

    def send_mail(self, mail_data):
        receiver = mail_data['receiver']
        title = mail_data['title']
        content = mail_data['content']
        secretkey = mail_data['secretkey']
        # print(content)
        response = None
        try:
            # s 是一个基于 dict 的实例
            s = mail_pb2.SendTextMailRequest(receiver=receiver, title=title, content=content, secretkey=secretkey)
            log_mail_request(receiver=receiver, title=title, content=content)
            response = self.stub.SendMail(s)
            return response
        except BaseException as e:
            log_mail_request_err(receiver=receiver, title=title, content=content, secretkey=secretkey, err=str(e))
            return {
                'code': 0,
                'msg': 'send error',
                'data': e
            }


def send_mail(receiver, title, content):
    client = GRPCClient()
    # test_mail_title = '测试邮件，推送时间%s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mail_data = {
        'receiver': receiver,
        'title': title,
        'content': content,
        'secretkey': SECRET_KEY
    }
    res2 = client.send_mail(mail_data)
    return res2


def send_mail_test(receiver,
                   title='测试邮件标题',
                   content=['邮件正文']):
    client = GRPCClient()
    test_mail_title = '测试邮件，推送时间%s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    title = test_mail_title
    mail_data = {
        'receiver': receiver,
        'title': title,
        'content': content,
        'secretkey': SECRET_KEY
    }
    res2 = client.send_mail(mail_data)
    return res2


# 测试和示例代码
if __name__ == '__main__':
    client = GRPCClient()
    sender = ''
    receiver = ''

    mail_body = '段落2'
    # 邮件主题
    mail_title = '测试邮件，推送时间%s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    contents = ['这是一个测试邮件的段落1', mail_body, '<a href="https://www.baidu.com">退订这个订阅号2</a>']
    mail_data = {
        'receiver': [receiver],
        'title': '测试邮件',
        'content': contents,
        'secretkey': SECRET_KEY
    }
    res2 = client.send_mail(mail_data)
    print(res2)
