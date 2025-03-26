from datetime import date, timedelta
import json

from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.core import serializers


from core.tasks import process_import_hr