from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from .models import Department, ScheduleEvent
from .serializers import *
from rest_framework.permissions import IsAuthenticated
import django_filters
from core.serializers import ScheduleEventSerializer, ScheduleEventListSerializer, ScheduleEventDetailSerializer
class DepartmentFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = Department
        fields = ['name', 'code']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains', 'code__icontains']
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
    return DepartmentSerializer

class ScheduleEventFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = ScheduleEvent
        fields = ['title',]

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
