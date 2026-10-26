from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(ConfigVolume)
class ConfigVolume(admin.ModelAdmin):
  list_display = ('name', 'code', 'user_amount', 'quota', 'unit_price')
  # search_fields = ('info', 'dob', 'gender', 'email', 'phone', 'company')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
  raw_id_fields = ('parent', 'business_unit')
  list_display = ('name', 'code', 'department_type', 'business_unit')

@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
  list_display = ('name',)
@admin.register(PackageConfig)
class PackageConfigAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'price', 'maximum_user','maximum_email', 'maximum_customer','maximum_contact')
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
  raw_id_fields=('legal_representative',)
  list_display = ('name','code','tax_code','phone','status','establishment_date','legal_representative')

@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'user_agent', 'last_used_at')
    raw_id_fields = ('user',)

@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
  list_display = ('title', 'user', 'start_datetime', 'end_datetime', 'is_all_day')
  raw_id_fields = ('user',)

# @admin.register(SystemGroup)
# class SystemGroupAdmin(admin.ModelAdmin):
#   list_display = ('name','code')
  # raw_id_fields = ('resources',)
admin.site.register(SystemGroup)
@admin.register(SystemResource)
class SystemResourceAdmin(admin.ModelAdmin):
  list_display = ('name','code','apps')

# RBAC Permission Admin
@admin.register(GroupResource)
class GroupResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'name', 'description']
    search_fields = ['name', 'group']
    list_filter = ['group']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'apps', 'name', 'name_view', 'url', 'action', 'sort_number']
    list_filter = ['group_resource', 'apps', 'action']
    search_fields = ['name', 'apps', 'url']
    ordering = ['sort_number']
    raw_id_fields = ['group_resource']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'resource', 'status']
    list_filter = ['status', 'group']
    search_fields = ['group__name', 'resource__name']
    raw_id_fields = ['resource', 'group']
    list_editable = ['status']


