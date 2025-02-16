from .models import *
from django.contrib import admin

admin.site.register(Notification)
admin.site.register(ArticleType)
class ArticleAdmin(admin.ModelAdmin):
    raw_id_fields = ['article_type', 'created_by']
    exclude = ['related_symbols']
admin.site.register(Article, ArticleAdmin)
admin.site.register(TelegramPushChannel)