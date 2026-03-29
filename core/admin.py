from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.register(Department)
admin.site.register(Title)
admin.site.register(Nationality)
admin.site.register(TimekeepingLocation)
admin.site.register(Bank)
admin.site.register(UserBankAccount)
admin.site.register(FamilyRelationship)
admin.site.register(ProfessionalQualification)
admin.site.register(CommunistPartyMember)
admin.site.register(Profile)
admin.site.register(WorkAttachment)
admin.site.register(WorkComment)
admin.site.register(WorkCommentAttachment)
admin.site.register(CustomerAttachment)
admin.site.register(CustomerComment)
admin.site.register(CustomerCommentAttachment)
admin.site.register(UserNotification)
@admin.register(ProfileHR)
class ProfileHRAdmin(admin.ModelAdmin):
  list_display = ('full_name', 'status', 'department', 'direct_manager', 'user', 'email', 'is_deleted')
  raw_id_fields = ('user', 'department')
  list_filter = ('status', 'account_status')

  def get_queryset(self, request):
      # Use global_objects to include soft-deleted records in the admin list
      return self.model.global_objects.all()
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ('name', 'customer_code','status','stage')


@admin.register(ContactAddtionalInfo)
class ContactAddtionalInfoAdmin(admin.ModelAdmin):
    raw_id_fields = ('customer',)
    list_display = ('customer', 'type_of_contact', 'description')

@admin.register(Works)
class WorkAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'status',)
