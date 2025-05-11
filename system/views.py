from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from .models import Department
from .serializers import *
from rest_framework.permissions import IsAuthenticated

class DepartmentViewSet(viewsets.ModelViewSet):
  queryset = Department.objects.all()
  serializer_class = DepartmentSerializer
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return DepartmentListSerializer
    return DepartmentSerializer