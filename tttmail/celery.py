from __future__ import absolute_import
import os
from celery import Celery, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tttmail.settings')

app = Celery('tttmail')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@shared_task
def t_process_hard_delete_old_profiles():
    from core.tasks import process_hard_delete_old_profiles
    process_hard_delete_old_profiles()