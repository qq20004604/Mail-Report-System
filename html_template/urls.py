from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='base_page'),
    path('lessfeeds.html', views.index, name='base_page'),
    path('autoreply.html', views.autoreply, name='autoreply'),
]
