from django.db import models

from django.contrib.auth.models import User, Group

from core.mixins.base_model import BaseModel, BaseCreateDeleteModel, BaseCreateUpdateModel
from simple_history.models import HistoricalRecords
# from django.contrib.gis.db import models as gis_models


class TimeRecord(models.Model):
    user = models.ForeignKey('core.ProfileHR', on_delete=models.CASCADE, related_name='time_records')
    date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    SOURCE_CHOICES = [
        ('XLSX Import', 'XLSX Import'),
        ('API - GPS', 'API - GPS'),
        ('API - Wi-Fi', 'API - Wi-Fi'),
        ('Manual', 'Manual'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='XLSX Import')
    device_info = models.TextField(null=True, blank=True)
    # geolocation = gis_models.PointField(null=True, blank=True)  # Requires GeoDjango setup
    wifi_ssid = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Overtime', 'Overtime'),
        ('Leave', 'Leave'),
        ('Half Day', 'Half Day'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    late_minutes = models.PositiveIntegerField(default=0)
    late_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    soon_minutes = models.PositiveIntegerField(default=0)
    soon_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forget_checking = models.BooleanField(default=False)
    # forget_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unauthorized_absence = models.BooleanField(default=False)
    permitted_absent = models.BooleanField(default=False)

    overtime_night = models.PositiveIntegerField('Overtime Night',default=0)
    overtime_day = models.PositiveIntegerField('Overtime Day',default=0)
    overtime_holiday_night = models.PositiveIntegerField('Overtime Holiday Night',default=0)
    overtime_holiday_day = models.PositiveIntegerField('Overtime Holiday Day',default=0)
    overtime_offday_night = models.PositiveIntegerField('Overtime Offday Night',default=0)
    overtime_offday_day = models.PositiveIntegerField('Overtime Offday Day',default=0)

    def __str__(self):
        return f"{self.user.full_name} - {self.date} - {self.source}"

# class ImportLog(models.Model):
#     file_name = models.CharField(max_length=255)
#     upload_date = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
#     STATUS_CHOICES = [
#         ('Success', 'Success'),
#         ('Partial Success', 'Partial Success'),
#         ('Failure', 'Failure'),
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     error_message = models.TextField(null=True, blank=True)
#     processed_records = models.IntegerField(default=0)
#     failed_records = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.file_name} - {self.upload_date} - {self.status}"


class PenaltyRate(models.Model):
    late_minute_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    soon_minute_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forget_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    absent_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    absent_allow_days = models.PositiveIntegerField(default=0)

    month = models.DateField()
    # Add more penalty types as needed

    def __str__(self):
        return "Penalty Rate"

class BonusRate(models.Model):
    offday_night_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offday_day_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    holiday_night_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    holiday_day_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    night = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.DateField()
    
    def __str__(self):
        return "Bonus Rate"