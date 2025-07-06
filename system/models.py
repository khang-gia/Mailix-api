from django.db import models
# from core.models import BaseCreateDeleteModel, BaseCreateUpdateModel
from django.contrib.auth.models import User, Group

from core.mixins.base_model import BaseModel, BaseCreateDeleteModel, BaseCreateUpdateModel
from simple_history.models import HistoricalRecords
import secrets
from django.conf import settings
from django.utils import timezone

class PackageConfig(BaseCreateUpdateModel):
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
class Company(BaseCreateUpdateModel):
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
    description = models.TextField("Description", null=True, blank=True)
    website = models.URLField("Website", null=True, blank=True, db_index=True)
    email = models.EmailField("Email", null=True, blank=True, db_index=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return "Company {}".format(self.name)

class BusinessUnit(BaseCreateUpdateModel):
    name = models.CharField('Name',max_length=100)
    description = models.TextField('Description',null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self)-> str:
        return "BusinessUnit{}".format(self.name)
 
DEPARTMENT_TYPES = (
    (1, 'Company branch'),
    (2, 'Department')
)
class Department(BaseCreateUpdateModel):
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    name = models.CharField("Name", max_length=50, db_index=True)
    location = models.CharField("Location", max_length=200, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="childen", db_index=True)
    business_unit = models.ForeignKey("BusinessUnit", on_delete=models.SET_NULL, null=True, blank=True, related_name="departments", db_index=True)
    department_type = models.IntegerField("Department Type", choices=DEPARTMENT_TYPES, default=1)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name="departments",db_index=True)
    history = HistoricalRecords()

    def _str_(self) -> str:
        return "Department <{}> {}".format(self.pk, self.name)


class AccountType(BaseModel):
    name = models.CharField("Name", max_length=50, db_index=True)
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    quota = models.CharField("Quota", null=True, max_length=200 ,blank=True, db_index=True)
    unit_price = models.DecimalField("Unit Price", max_digits=10, decimal_places=2, db_index=True)
    user_amount = models.PositiveIntegerField("User Amount")
    history = HistoricalRecords()

    def __str__(self) -> str:
        return "AccountType <{}>".format(self.name)


class SystemGroup(BaseCreateUpdateModel):
    name = models.CharField("Name", max_length=50, db_index=True)
    code = models.CharField("Code", max_length=20, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    account_type = models.ForeignKey("AccountType", on_delete=models.SET_NULL, null=True, blank=True, related_name="system_groups", db_index=True)

    history = HistoricalRecords()
    def __str__(self) -> str:
        return "SystemGroup <{}>".format(self.name)

class TrustedDevice(BaseCreateUpdateModel):
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