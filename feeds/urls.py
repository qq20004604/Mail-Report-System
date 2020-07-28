from django.urls import path

from . import views

urlpatterns = [
    # 创建一个新的 up 主账号
    path('uploader/create/', views.uploader_create, name='uploader_create'),
    # 删除或禁用 up 主账号：undo
    # 查看当前用户名下的 up 主账号
    path('user/detail/', views.user_detail, name='user_detail'),
    # 查看我的 up 主账号的详情
    path('uploader/detail/self/', views.uploader_detail_self, name='uploader_detail_self'),
    # 重置 UP 主密钥
    path('uploader/key/refresh/', views.uploader_key_refresh, name='uploader_key_refresh'),
    # 修改 UP 主昵称
    path('uploader/name/edit/', views.uploader_name_edit, name='uploader_name_edit'),
    # 获取当前用户的up主列表（相当于 uploader_my_detail 比较详细信息来说，是简化版）
    path('uploader/list/self_simple/', views.my_uploader_list_simple, name='my_uploader_list_simple'),
    # 新增信息
    path('send/', views.feeds_send, name='feeds_send'),
    # 新增信息（使用密钥）
    path('send/bykey/', views.feeds_send_by_key, name='feeds_send_by_key'),
    # 查看所有用户，以及他们最近的一条消息
    path('uploader/list/', views.uploader_list, name='uploader_list'),
    # 订阅某条消息
    path('subscribe/', views.user_subscribe, name='user_subscribe'),
    # 取消订阅某条消息
    path('unsubscribe/', views.user_unsubscribe, name='user_unsubscribe'),
    # 查看订阅当前UP主的人
    path('uploader/suberlist/', views.uploader_suberlist, name='uploader_suberlist'),
    # 其他人查看某UP主信息（只能查询最近一条已推送的信息）
    path('uploader/detail/others/', views.uploader_detail_by_others, name='uploader_detail_by_others'),
    # 允许/禁止 指定用户接受当前 UP 主的邮件推送
    path('uploader/rec/set/', views.uploader_rec_set, name='self_suber_rec'),
    # 查看某用户订阅了哪些up主
    path('user/subscribe_list/', views.user_subscribe_list, name='user_subscribe_list'),
]
