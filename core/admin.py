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
admin.site.register(ProfileHR)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ('name', 'customer_code','status','stage')


@admin.register(ContactAddtionalInfo)
class ContactAddtionalInfoAdmin(admin.ModelAdmin):
    raw_id_fields = ('customer',)
    list_display = ('customer', 'type_of_contact', 'description')

@admin.register(Works)
class WorkAdmin(admin.ModelAdmin):
  list_display = ('name', 'code')
