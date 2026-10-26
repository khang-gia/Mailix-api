from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from .models import Department, ScheduleEvent, BusinessUnit, Company
from .serializers import *
from rest_framework.permissions import IsAuthenticated
import django_filters
from core.serializers import ScheduleEventSerializer, ScheduleEventListSerializer, ScheduleEventDetailSerializer
from rest_framework.decorators import action, api_view, permission_classes
from constance import config
from django.conf import settings

class DepartmentFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = Department
        fields = ['name', 'code','department_type']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains', 'code__icontains', 'location__icontains']
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class DepartmentViewSet(viewsets.ModelViewSet):
  queryset = Department.objects.all()
  serializer_class = DepartmentSerializer
  filterset_class = DepartmentFilter
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return DepartmentListSerializer
    elif self.action =='retrieve':
      return DepartmentDetailSerializer
    return DepartmentSerializer

  @action(detail=False, methods=['post'])
  def delete_departments(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    department_ids = request.data['departments']
    if not department_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for department_id in department_ids:
      try:
        department = Department.objects.get(pk=department_id)
        department.delete()
      except Department.DoesNotExist:
        pass
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)



class ScheduleEventFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    start_datetime__gte = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte')
    start_datetime__lte = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte')
    end_datetime__gte = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='gte')
    end_datetime__lte = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='lte')
    class Meta:
        model = ScheduleEvent
        fields = ['title', 'start_datetime__gte', 'start_datetime__lte', 'end_datetime__gte', 'end_datetime__lte']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['title__icontains',]
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class ScheduleEventViewSet(viewsets.ModelViewSet):
  queryset = ScheduleEvent.objects.all()
  serializer_class = ScheduleEventSerializer
  filterset_class = ScheduleEventFilter
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return ScheduleEventListSerializer
    elif self.action == 'retrieve':
      return ScheduleEventDetailSerializer
    return ScheduleEventSerializer

  def get_queryset(self):
    user = self.request.user
    if user.is_anonymous:
        return self.queryset.none()
    
    # Check if user is admin (Superuser or Admin/System Admin role)
    is_admin = user.is_superuser
    if not is_admin and hasattr(user, 'profile'):
        is_admin = user.profile.role in ['A', 'SA', 'RA']
        
    if is_admin:
        return self.queryset
    
    # Non-admins only see events they created or are participating in
    return self.queryset.filter(Q(user=user) | Q(participants=user)).distinct()


class BusinessUnitFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = BusinessUnit
        fields = ['name', 'description']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains']
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class BusinessUnittViewSet(viewsets.ModelViewSet):
  queryset = BusinessUnit.objects.all()
  serializer_class = BusinessUnitSerializer
  filterset_class = BusinessUnitFilter
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return BusinessUnitListSerializer
    return BusinessUnitSerializer

class SystemResourceFilter(FilterSet):
  search = django_filters.CharFilter(method='elastic_search')

  class Meta:
    model = SystemResource
    fields = ['name', 'description']

  def elastic_search(self, queryset, name, value):
    if not value:
      return queryset
      fields = ['name__icontains']
      _q = Q()
      for field in fields:
        _q = _q | Q(**{field: value})

      return queryset.filter(_q)

class SystemResourceViewSet(viewsets.ModelViewSet):
  queryset = SystemResource.objects.all()
  serializer_class = SystemResourceSerializer
  filterset_class = SystemResourceFilter


class SystemGroupFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = SystemGroup
        fields = ['name', 'code', 'fixed_group']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains',]
        _q = Q()
        for field in fields:
          _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class SystemGroupViewSet(viewsets.ModelViewSet):
  queryset = SystemGroup.objects.all()
  serializer_class = SystemGroupSerializer
  filterset_class = SystemGroupFilter
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return SystemGroupListSerializer
    elif self.action =='retrieve':
      return SystemGroupDetailSerializer
    return SystemGroupSerializer

  @action(detail=False, methods=['post'])
  def delete_groups(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    group_ids = request.data['groups']
    if not group_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for group_id in group_ids:
      try:
        group = SystemGroup.objects.get(pk=group_id)
        group.delete()
      except SystemGroup.DoesNotExist:
        pass
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)



class CompanyFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = Company
        fields = ['name', 'code']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains']
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class CompanyViewSet(viewsets.ModelViewSet):
  queryset = Company.objects.all()
  serializer_class = CompanySerializer
  filterset_class = CompanyFilter
  ordering_fields = ['id']
  ordering = ('-id',)

  @action(detail=True, methods=['patch'], url_path='update-modules')
  def update_modules(self, request, pk=None):
      """
      Update enabled modules for a company.
      This endpoint is designed for external pricing/subscription systems.
      
      Body: {
        "enabled_modules": ["crm", "hrm", "inventory"]
      }
      """
      company = self.get_object()
      
      # Only superusers or system admins can update modules
      if not (request.user.is_superuser or 
              (hasattr(request.user, 'profile') and request.user.profile.is_system_admin)):
          return Response(
              {'detail': 'Only administrators can update company modules'},
              status=status.HTTP_403_FORBIDDEN
          )
      
      modules = request.data.get('enabled_modules', [])
      
      # Validate modules is a list
      if not isinstance(modules, list):
          return Response(
              {'detail': 'enabled_modules must be a list'},
              status=status.HTTP_400_BAD_REQUEST
          )
      
      # Update company modules
      company.enabled_modules = modules
      company.save()
      
      serializer = self.get_serializer(company)
      return Response({
          'detail': 'Modules updated successfully',
          'company': serializer.data
      })


# RBAC Permission ViewSets
class GroupResourceFilter(FilterSet):
    search = django_filters.CharFilter (method='elastic_search')
    
    class Meta:
        model = GroupResource
        fields = ['group', 'name']
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(group__icontains=value)
        )

class GroupResourceViewSet(viewsets.ModelViewSet):
    queryset = GroupResource.objects.all()
    serializer_class = GroupResourceSerializer
    filterset_class = GroupResourceFilter
    ordering = ['id']

class ResourceFilter(FilterSet):
    apps = django_filters.CharFilter(field_name="apps")
    group_resource = django_filters.CharFilter(field_name="group_resource__group")
    search = django_filters.CharFilter(method='elastic_search')
    
    class Meta:
        model = Resource
        fields = ['apps', 'group_resource']
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(apps__icontains=value) |
            Q(url__icontains=value)
        )

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilter
    ordering = ['sort_number']

class PermissionFilter(FilterSet):
    class Meta:
        model = Permission
        fields = ['group', 'status', 'resource']

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filterset_class = PermissionFilter
    ordering = ['id']
    
    @action(detail=False, methods=['POST'])
    def update_multiple(self, request):
        """Bulk update permissions for multiple groups"""
        try:
            for group_data in request.data:
                for resource_perm in group_data.get('resource_list', []):
                    Permission.objects.update_or_create(
                        group_id=resource_perm['group'],
                        resource_id=resource_perm['resource'],
                        defaults={'status': resource_perm.get('status', False)}
                    )
            
            return Response({"detail": "Permissions updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='my-permissions')
    def my_permissions(self, request):
        """
        Returns all granted permissions for the current user's groups.
        Used by the frontend to build the RBAC permissions store on login.

        Response format (minimal, optimised for frontend):
        [
          { "url": "/api/v1/core/employees/", "action": "list", "category": "hrm" },
          ...
        ]
        """
        from system.permissions import AclPermission
        acl = AclPermission()
        group_ids = acl._get_user_groups(request.user)

        if not group_ids:
            return Response([])

        permissions = (
            Permission.objects
            .filter(status=True, group_id__in=group_ids)
            .select_related('resource', 'resource__group_resource')
            .distinct()
        )

        data = []
        for p in permissions:
            if not p.resource:
                continue
            data.append({
                'url':      p.resource.url,
                'action':   p.resource.action,
                'category': (
                    p.resource.group_resource.group
                    if p.resource.group_resource else None
                ),
            })

        return Response(data)


  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_config(request):
    return Response({
        'MAIL_SERVER_URL': config.MAIL_SERVER_URL,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def system_admin_config(request):
    user = request.user
    is_admin = user.is_superuser
    if not is_admin and hasattr(user, 'profile'):
        is_admin = user.profile.role in ['A', 'SA', 'RA']
    
    if not is_admin:
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'GET':
        data = []
        for key, options in settings.CONSTANCE_CONFIG.items():
            default = options[0]
            help_text = options[1] if len(options) > 1 else ''
            value = getattr(config, key)
            data.append({
                'key': key,
                'value': value,
                'default': default,
                'help_text': help_text,
            })
        return Response(data)
    
    elif request.method == 'POST':
        for item in request.data:
            key = item.get('key')
            value = item.get('value')
            if key in settings.CONSTANCE_CONFIG:
                setattr(config, key, value)
        return Response({'status': 'ok'})