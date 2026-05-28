from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q
from celery import current_app

from upload.serializers import UploadSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.
from .models import *

class UploadFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = Upload
        fields = ('upload_type',)

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['file_name__icontains', 'created_by__first_name__icontains', 'created_by__last_name__icontains', 'created_by__username__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)

class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    filterset_class = UploadFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['pk']
    ordering = ['-pk']

    def get_queryset(self):
        qs = self.queryset
        if not self.request.user.profile or not self.request.user.profile.role:
            qs = qs.none()
        elif self.request.user.profile.role != 'A':
            qs = qs.filter(created_by=self.request.user)
            

        return qs.select_related('created_by')

    def create(self, request, *args, **kwargs):
        # override created_by        
        request.data['created_by'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def revoke_import_in_progress(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == 3:
            task_id = obj.task_id
            if task_id:
                current_app.control.revoke(task_id, terminate=True)
            obj.status = 9
            obj.save()
        return Response({'success': 'Import revoked'}, status=status.HTTP_200_OK)
