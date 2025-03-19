# -*- coding: utf-8 -*-#

from django.db import models
from django.utils import timezone


class BaseQuerySetMixin(models.QuerySet):
    def delete(self):
        for obj in self:
            obj.deleted_at = timezone.now()
            obj.is_deleted = True
            obj.save()

    def bulk_hard_delete(self):
        for obj in self:
            obj.hard_delete()

    def bulk_restore(self):
        for obj in self:
            obj.restore()
