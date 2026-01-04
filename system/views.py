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
from rest_framework.decorators import action

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
        fields = ['name', 'code']

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
  