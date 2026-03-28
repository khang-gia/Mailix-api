from django.db import models
# from core.models import BaseCreateDeleteModel, BaseCreateUpdateDeleteModel
from django.contrib.auth.models import User, Group

from core.mixins.base_model import BaseModel, BaseCreateDeleteModel, BaseCreateUpdateDeleteModel
from simple_history.models import HistoricalRecords
import secrets
from django.conf import settings
from django.utils import timezone

class PackageConfig(BaseCreateUpdateDeleteModel):
  name = models.CharField("Name", max_length=100, db_index=True)
  code = models.CharField("Code", max_length=50, unique=True, db_index=True)
  description = models.TextField("Description", null=True, blank=True, db_index=True)
  price = models.DecimalField("Price", max_digits=10, decimal_places=2, default=0.00, db_index=True)
  is_active = models.BooleanField("Is Active", default=True)
  maximum_user = models.IntegerField("Maximum User", default=0)
  maximum_email = models.IntegerField("Maximum Email", default=0)
  maximum_customer = models.IntegerField("Maximum Customer", default=0)
  maximum_contact = models.IntegerField("Maximum Contact", default=0)

  def __str__(self) -> str:
    return "PackageConfig <{}> {}".format(self.pk, self.name)


COMPANY_STATUSES = (
  (0, "Working"),
  (1, "Suspend"),
  (9, "Others"),
)
INDUSTRY_CHOICES = (
  (1, 'Retail'),
  (2, 'Wholesale'),
  (3, 'Manufacturing'),
  (4, 'Service'),
  (5, 'Technology'),
  (6, 'Healthcare'),
  (7, 'Education'),
  (8, 'Finance'),
  (9, 'Real Estate'),
  (10, 'Transportation'),
  (11, 'Construction'),
  (12, 'Hospitality'),
  (13, 'Entertainment'),
  (14, 'Agriculture'),
  (15, 'Other'),
)
class Company(BaseCreateUpdateDeleteModel):
    name = models.CharField('Name',max_length=100, db_index=True)
    code = models.CharField('Code (AKA)', max_length=100, null=True, blank=True, db_index=True)
    tax_code = models.CharField('Tax Code', max_length=100, db_index=True)
    phone = models.CharField("Phone", max_length=20, null=True, blank=True)
    fax = models.CharField("Fax", max_length=100, null=True, blank=True)
    status = models.IntegerField("Status", default=0, choices=COMPANY_STATUSES)
    address = models.CharField("Address", max_length=200, null=True, blank=True, db_index=True)
    headquarter = models.CharField("Headquarter", max_length=200, null=True, blank=True, db_index=True)
    establishment_date = models.DateField("Establishment Date")
    legal_representative = models.ForeignKey("auth.User",on_delete=models.SET_NULL, null=True, blank=True, related_name='companies', db_index=True)
    package_config = models.ForeignKey("PackageConfig", on_delete=models.SET_NULL, null=True, blank=True, related_name="companies", db_index=True)
    is_maximum_user = models.BooleanField("Is Maximum User", default=False, db_index=True)
    is_maximum_email = models.BooleanField("Is Maximum Email", default=False, db_index=True)
    is_maximum_customer = models.BooleanField("Is Maximum Customer", default=False, db_index=True)
    is_maximum_contact = models.BooleanField("Is Maximum Contact", default=False, db_index=True)
    logo = models.ImageField("Logo", upload_to='company_logos/', null=True, blank=True)
    favicon = models.ImageField("Favicon", upload_to='company_favicons/', null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    website = models.URLField("Website", null=True, blank=True, db_index=True)
    email = models.EmailField("Email", null=True, blank=True, db_index=True)
    industry = models.IntegerField("Industry", choices=INDUSTRY_CHOICES, null=True, blank=True, db_index=True)
    # config_volume = models.ForeignKey('ConfigVolume', on_delete=models.SET_NULL, null=True, blank=True, related_name='companies', db_index=True)

    history = HistoricalRecords()

    def __str__(self) -> str:
        return "Company {}".format(self.name)

class BusinessUnit(BaseCreateUpdateDeleteModel):
    name = models.CharField('Name',max_length=100)
    description = models.TextField('Description',null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self)-> str:
        return "BusinessUnit{}".format(self.name)
 
DEPARTMENT_TYPES = (
    (1, 'Company branch'),
    (2, 'Department')
)
class Department(BaseCreateUpdateDeleteModel):
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    name = models.CharField("Name", max_length=50, db_index=True)
    location = models.CharField("Location", max_length=200, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="childen", db_index=True)
    business_unit = models.ForeignKey("BusinessUnit", on_delete=models.SET_NULL, null=True, blank=True, related_name="departments", db_index=True)
    department_type = models.IntegerField("Department Type", choices=DEPARTMENT_TYPES, default=1)
    # company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name="departments",db_index=True)
    group = models.ForeignKey('SystemGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='departments', db_index=True)
    config_volume = models.ForeignKey('ConfigVolume', on_delete=models.SET_NULL, null=True, blank=True, related_name='departments', db_index=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return "Department {}".format(self.name)

UNIT_CHOICES = (
    ('GB', 'GB'),
    ('MB', 'MB'),
    ('KB', 'KB'),
    ('FILE', 'FILE'),
)

class ConfigVolume(BaseModel):
    """This model is used to set the type of account (small scope, only effect under company level as department), for config and other purposes"""
    name = models.CharField("Name", max_length=50, db_index=True)
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    quota = models.CharField("Quota", null=True, max_length=200 ,blank=True, db_index=True)
    unit = models.CharField("Unit", max_length=20, null=True, blank=True, db_index=True, choices=UNIT_CHOICES)
    unit_price = models.DecimalField("Unit Price", max_digits=10, decimal_places=2, db_index=True)
    user_amount = models.PositiveIntegerField("User Amount")
    history = HistoricalRecords()

    def __str__(self) -> str:
        return "ConfigVolume <{}>".format(self.name)

class SystemResource(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    apps = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)

    def __str__(self) -> str:
        return "SystemResource <{}>".format(self.name)

class SystemGroup(BaseCreateUpdateDeleteModel):
    """This model is used to store system groups (for decentralization only)"""
    name = models.CharField("Name", max_length=50, db_index=True)
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    resources = models.ManyToManyField(SystemResource, related_name='groups', db_index=True)
    # account_type = models.ForeignKey("AccountType", on_delete=models.SET_NULL, null=True, blank=True, related_name="system_groups", db_index=True)

    history = HistoricalRecords()
    def __str__(self) -> str:
        return "SystemGroup <{}>".format(self.name)

class TrustedDevice(BaseCreateUpdateDeleteModel):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='trusted_devices'
    )
    # We will store a hashed version of the token.
    token = models.CharField(max_length=255, unique=True)
    
    # Optional: Store these for user's reference and extra security checks
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, null=True, blank=True)
    
    last_used_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s device"

REMINDER_UNIT_CHOICES = [
    ('minutes', 'Minutes before'),
    ('hours', 'Hours before'),
    ('days', 'Days before'),
    ('weeks', 'Weeks before'),
]
FREQ_CHOICES = [
    ('none', 'Does not repeat'),
    ('daily', 'Every day'),
    ('weekly', 'Every week'),
    ('monthly', 'Every month'),
]

WEEKDAY_CHOICES = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
]
PRIORITY_CHOICES = (
  (1, 'Low'),
  (2, 'Medium'),
  (3, 'High'),
  (4, 'Urgent'),
  (5, 'Critical'),
  (6, 'None'),
)
class ScheduleEvent(BaseCreateUpdateDeleteModel):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='schedule_events',db_index=True
    )
    participants = models.ManyToManyField('auth.User', related_name='p_schedule_events', null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    priority = models.IntegerField("Priority", choices=PRIORITY_CHOICES, default=2, null=True, blank=True, db_index=True)
    notification_type = models.IntegerField(
        choices=(
            (1, 'Email'),
            (2, 'SMS'),
            (3, 'Push Notification'),
        ),
        default=3,
        db_index=True,
        help_text="Type of notification to send"
    )
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)

    is_all_day = models.BooleanField(default=False, db_index=True)

    location = models.CharField(max_length=255, blank=True)

    # Optional: Event color, like Google Calendar (could be used for categories)
    color = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    work = models.ForeignKey('core.Works', on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule_events', db_index=True)
    # Reminder/notification
    has_reminder = models.BooleanField(default=False, db_index=True)
    reminder_time_value = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="How long before the event to send a reminder"
    )

    reminder_time_unit = models.CharField(
        max_length=10,
        choices=REMINDER_UNIT_CHOICES,
        default='minutes',
        help_text="Unit for reminder time"
    )

    reminder_email = models.EmailField(
        blank=True,
        help_text="Optional email address to send reminder to"
    )
    is_send_participants = models.BooleanField(
        default=False,
        help_text="Send reminder to all participants"
    )
    # Future: recurrence support. repeat config
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(
        max_length=255, blank=True,
        help_text="Optional iCal RRULE for recurring events"
    )
    

    frequency = models.CharField(
        max_length=10,
        choices=FREQ_CHOICES,
        default='none',
        db_index=True,
        help_text="How often this event repeats"
    )

    repeat_on_weekdays = models.JSONField(
        blank=True, null=True,
        help_text="List of weekdays if frequency is weekly. Example: ['mon', 'wed']"
    )

    repeat_until = models.DateField(
        null=True, blank=True,
        help_text="Stop repeating after this date"
    )

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} - {self.user}"

    def is_past(self):
        from django.utils import timezone
        return self.end_datetime < timezone.now()

# class ScheduleEventNotifications(models.Model):
#     schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, related_name='emails', db_index=True)
#     recipient_email = models.EmailField()

#     def __str__(self):
#         return f"Notification for {self.schedule_event} to {self.recipient_email}"    
# Decentralization
# class GroupResource(models.Model):
# 	group = models.CharField(max_length=255, null=True, blank=True, verbose_name='group')
# 	name = models.CharField(max_length=255, null=True, blank=True, verbose_name='name')

# 	def __str__(self):
# 		return '{}'.format(self.name)

# 	class Meta:
# 		ordering = ['id']

# class Resource(models.Model):
# 	apps = models.CharField(max_length=255, null=True, blank=True, verbose_name='api_name')
# 	name = models.CharField(max_length=255, null=True, blank=True, verbose_name='name')
# 	name_view = models.CharField(max_length=255, null=True, blank=True, verbose_name='name_view')
# 	url = models.CharField(max_length=255, null=True, blank=True, verbose_name='url')
# 	action = models.CharField(max_length=255, null=True, blank=True, verbose_name='action')
# 	sort_number = models.IntegerField(default=0)
# 	group_resource =  models.ForeignKey(GroupResource, null=True, blank=True, related_name='group_resource', on_delete=models.CASCADE)

# 	def __str__(self):
# 		return '{}<{}> - {}'.format(self.name, self.pk, self.name_view)

# 	class Meta:
# 		ordering = ['sort_number']

# class Permission(models.Model):
# 	resource = models.ForeignKey(Resource, null=True, blank=True, related_name='permission', on_delete=models.CASCADE)
# 	group =  models.ForeignKey(SystemGroup, null=True, blank=True, related_name='permission', on_delete=models.CASCADE)
# 	status = models.BooleanField(default=False, verbose_name="Is Permission?")

# 	class Meta:
# 		unique_together = ('resource', 'group')