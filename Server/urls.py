"""Server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from Server.settings import QQ_SYSTEM_SWITCH

urlpatterns = [
    path('', include('html_template.urls')),
    path('user/', include('user.urls')),
    path('feeds/', include('feeds.urls')),
    # path('', include('page.urls')),
]

if QQ_SYSTEM_SWITCH:
    urlpatterns.insert(0, path('msg/', include('msg.urls')))

# 如果是调试模式
if settings.DEBUG:
    test_urlpatterns = [
        # path('experiment/', include('experiment.urls')),
        path('admin/', admin.site.urls),
    ]
    urlpatterns.extend(test_urlpatterns)
