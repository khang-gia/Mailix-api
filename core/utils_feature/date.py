from django.utils import timezone
from datetime import timedelta
from core.models import Holiday
from market.models import MarketIndex

def is_holiday(date=None):
    if not date:
        date = timezone.localtime(timezone.now())
    return Holiday.objects.filter(date_from__lte=date, date_to__gte=date).exists()

def is_dayoff(date=None):
    if not date:
        date = timezone.localtime(timezone.now())
    print('date={}'.format(date))
    date_in_week = date.weekday()
    if date_in_week in [5, 6]: return True
    return is_holiday(date)

def second_to_midnight():
    now = timezone.localtime(timezone.now())
    tomorrow = now +  timedelta(days=1)
    tomorrow = tomorrow.replace(hour=0, minute=0, second=0)
    diff = tomorrow - now
    return diff.seconds

def tplus(_date, max_date=None):
    if not _date:
        return None

    qs = MarketIndex.objects.filter(name='VNINDEX', date__gt=_date)
    if max_date:
        qs = qs.filter(date__lte=max_date)
    return qs.count()

def is_today(date):
    _today = timezone.localdate(timezone.now())
    return date == _today

def get_today():
    return timezone.localdate(timezone.now())

def get_yesterday():
    return get_today() - timedelta(days=1)