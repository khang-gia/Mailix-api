from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
  list_display = ('file_name', 'created_at', 'status','total','success', 'failure')