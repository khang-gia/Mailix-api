from .models import *
from rest_framework import serializers

class ParentDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')

class BusinessUnitSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = ('id', 'name')

class DepartmentListSerializer(serializers.ModelSerializer):
    parent = ParentDepartmentSerializer(read_only=True)
    business_unit = BusinessUnitSimpleSerializer(read_only=True)
    department_type_display = serializers.CharField(source='get_department_type_display', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class DepartmentDetailSerializer(serializers.ModelSerializer):
    parent = ParentDepartmentSerializer(read_only=True)
    business_unit = BusinessUnitSimpleSerializer(read_only=True)
    class Meta:
        model = Department
        fields = '__all__'
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class BusinessUnitListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessUnit
        fields = '__all__'

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = '__all__'
