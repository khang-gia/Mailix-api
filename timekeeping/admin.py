from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(TimeRecord)
admin.site.register(BonusRate)
admin.site.register(PenaltyRate)
