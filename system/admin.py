from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(SystemGroup)
class SystemGroupAdmin(admin.ModelAdmin):
  raw_id_fields = ('account_type', )
  list_display = ('name','code','account_type')

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'user_amount', 'quota', 'unit_price')
  # search_fields = ('info', 'dob', 'gender', 'email', 'phone', 'company')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
  raw_id_fields = ('parent', 'business_unit')
  list_display = ('name', 'code', 'department_type', 'business_unit')

@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
  list_display = ('name',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
  raw_id_fields=('legal_representative',)
  list_display = ('name','code','tax_code','phone','status','establishment_date','legal_representative')

@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'user_agent', 'last_used_at')
    raw_id_fields = ('user',)