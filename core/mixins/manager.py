# -*- coding: utf-8 -*-#
from django.db import models
from .queryset import BaseQuerySetMixin


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        queryset = BaseQuerySetMixin(self.model, using=self._db)
        return queryset
