from .models import *
from django.contrib import admin

admin.site.register(Notification)
admin.site.register(ArticleType)
admin.site.register(Article)
admin.site.register(TelegramPushChannel)