from django_filters.rest_framework import FilterSet
import django_filters
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger('app')

class RangeFilter(FilterSet):
    range = django_filters.CharFilter(method='range_filter')

    def range_filter(self, queryset, name, value):
        today = timezone.localdate(timezone.now())
        
        _val = value.replace('m', '').replace('d', '')
        try:
            _val = int(_val)
        except:
            _val = 1
        if 'm' in value:
            qs = queryset.filter(date__gte=today - relativedelta(months=_val))
        elif 'd' in value:
            qs = queryset.filter(date__gte=today - relativedelta(days=_val))
        return qs