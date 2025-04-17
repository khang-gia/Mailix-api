from django.shortcuts import render

# Create your views here.
from .serializers import TimeRecordListSerializer, TimeRecordDetailSerializer, TimeRecordSerializer
from .model import TimeRecord
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class TimeRecordFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = TimeRecord
        fields = ('user',)

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['user__full_name__icontains', 'user__employee_code__icontains', 'user__timekeeping_id__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)
 
class TimeRecordViewSet(viewsets.ModelViewSet):
    queryset = TimeRecord.objects.all()
    serializer_class = TimeRecordSerializer
    filterset_class = TimeRecordFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['pk']
    ordering = ['-pk']

    def get_serializer_class(self):
        if self.action == 'list':
            return TimeRecordListSerializer
        elif self.action == 'retrieve':
            return TimeRecordDetailSerializer
        return TimeRecordSerializer
