from .models import *
from rest_framework import serializers

class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'

