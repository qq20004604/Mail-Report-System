from django.contrib import admin

# Register your models here.

from .models import MsgPuber, Feeds, SubscribeHistory, SubscribeFeeds

admin.site.register(MsgPuber)
admin.site.register(Feeds)
admin.site.register(SubscribeFeeds)
admin.site.register(SubscribeHistory)
