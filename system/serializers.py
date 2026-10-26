from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User

class SystemResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemResource
        fields = '__all__'

    

class SystemGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemGroup
        fields = '__all__'

    # def create(self, validated_data):
    #   resources = validated_data.pop('resources', [])
    #   group = SystemGroup.objects.create(**validated_data)
    #   group.resources.set(resources)
    #   return group

    # def update(self, instance, validated_data):
    #   resources = validated_data.pop('resources', None)
    #   for attr, value in validated_data.items():
    #     setattr(instance, attr, value)
      
    #   if resources is not None:
    #     instance.resources.set(resources)

    #   instance.save()
    #   return instance

class SystemGroupUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'full_name')

    def get_full_name(self, obj):
        return '%s %s'%(obj.first_name, obj.last_name) if obj.first_name else obj.username if not hasattr(obj, 'profile_hr') else obj.profile_hr.full_name

class SystemGroupListSerializer(serializers.ModelSerializer):
    # resources = SystemResourceSerializer(read_only=True, many=True)
    users = SystemGroupUserSerializer(read_only=True, many=True)
    class Meta:
        model = SystemGroup
        fields = '__all__'

class SystemGroupDetailSerializer(serializers.ModelSerializer):
    resources = SystemResourceSerializer(read_only=True, many=True)
    users = SystemGroupUserSerializer(read_only=True, many=True)

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
    resources = SystemResourceSerializer(read_only=True, many=True)

    class Meta:
        model = Department
        fields = '__all__'

class DepartmentDetailSerializer(serializers.ModelSerializer):
    parent = ParentDepartmentSerializer(read_only=True)
    business_unit = BusinessUnitSimpleSerializer(read_only=True)
    group = SystemGroupDetailSerializer(read_only=True)
    resources = SystemResourceSerializer(read_only=True, many=True)
    class Meta:
        model = Department
        fields = '__all__'
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
      resources = validated_data.pop('resources', [])
      department = Department.objects.create(**validated_data)
      department.resources.set(resources)
      return department

    def update(self, instance, validated_data):
      resources = validated_data.pop('resources', None)
      for attr, value in validated_data.items():
        setattr(instance, attr, value)
      
      if resources is not None:
        instance.resources.set(resources)

      instance.save()
      return instance

class BusinessUnitListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessUnit
        fields = '__all__'

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = '__all__'

class PackageConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = PackageConfig
        fields = '__all__'
    
class CompanySerializer(serializers.ModelSerializer):
    package_config = PackageConfigSerializer(read_only=True)
    class Meta:
        model = Company
        fields = '__all__'

# RBAC Permission Serializers
class GroupResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupResource
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    group_resource_detail = GroupResourceSerializer(source='group_resource', read_only=True)
    
    class Meta:
        model = Resource
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    group_detail = SystemGroupDetailSerializer(source='group', read_only=True)
    resource_detail = ResourceSerializer(source='resource', read_only=True)
    
    class Meta:
        model = Permission
        fields = '__all__'

class SystemGroupWithResourcesSerializer(serializers.ModelSerializer):
    """SystemGroup serializer with filtered resources based on permissions"""
    resources = serializers.SerializerMethodField()
    
    def get_resources(self, obj):
        # Return all resources this group has permission for
        resources = Resource.objects.filter(
            permissions__group=obj,
            permissions__status=True
        ).distinct()
        return ResourceSerializer(resources, many=True).data
    
    class Meta:
        model = SystemGroup
        fields = '__all__'