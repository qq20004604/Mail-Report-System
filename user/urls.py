from django.urls import path

from . import views

urlpatterns = [
    path('send_email_regcode/', views.send_email_regcode, name='send_email_regcode'),
    path('register/', views.register, name='user_register'),
    path('login/', views.login, name='user_login'),
    path('logout/', views.logout, name='user_logout'),
    path('had_logined/', views.had_logined, name='user_had_logined'),
]
