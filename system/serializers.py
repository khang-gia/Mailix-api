from .models import *
from rest_framework import serializers

class SystemResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemResource
        fields = '__all__'

    

class SystemGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemGroup
        fields = '__all__'

    def create(self, validated_data):
      resources = validated_data.pop('resources', [])
      group = SystemGroup.objects.create(**validated_data)
      group.resources.set(resources)
      return group

    def update(self, instance, validated_data):
      resources = validated_data.pop('resources', None)
      for attr, value in validated_data.items():
        setattr(instance, attr, value)
      
      if resources is not None:
        instance.resources.set(resources)

      instance.save()
      return instance

class SystemGroupListSerializer(serializers.ModelSerializer):
    # resources = SystemResourceSerializer(read_only=True, many=True)
    class Meta:
        model = SystemGroup
        fields = '__all__'

class SystemGroupDetailSerializer(serializers.ModelSerializer):
    resources = SystemResourceSerializer(read_only=True, many=True)

    class Meta:
        model = SystemGroup
        fields = '__all__' 

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
    group = SystemGroupDetailSerializer(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class DepartmentDetailSerializer(serializers.ModelSerializer):
    parent = ParentDepartmentSerializer(read_only=True)
    business_unit = BusinessUnitSimpleSerializer(read_only=True)
    group = SystemGroupDetailSerializer(read_only=True)
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
