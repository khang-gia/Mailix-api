from django.contrib import admin
from download.models import Download

class DownloadAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'export_type', 'status', 'query')
admin.site.register(Download, DownloadAdmin)
