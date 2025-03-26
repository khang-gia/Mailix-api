from __future__ import absolute_import
import os
from celery import Celery, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tttmail.settings')

app = Celery('tttmail')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



