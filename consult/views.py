from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
import django_filters
from django_filters.rest_framework import FilterSet
from django.utils import timezone

from .serializers import NotificationSerializer, ArticleDetailSerializer, ArticleSerializer, ArticleTypeSerializer, \
    ArticleNoAuthSerializer
    
from .models import Notification, Article, ArticleType

# from invest.models import UserStockList

from django.db.models import Q

# Create your views here.
class NotificationViewSet(viewsets.ModelViewSet):

    queryset = Notification.objects.order_by('-created_at')
    serializer_class = NotificationSerializer

    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user and self.request.user.is_authenticated:
            return qs
        return qs.none()
    
    
class ArticleFilter(FilterSet):
  related_symbols = django_filters.CharFilter(field_name="related_symbols", lookup_expr='icontains')
  class Meta:
    model = Article
    fields = ['related_symbols', 'article_type', 'created_by']

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filterset_class = ArticleFilter
    ordering_fields = ['published_at']
    ordering = ('-published_at')

    # def get_permissions(self):
    #     if self.action == "retrieve":
    #         self.permission_classes = [IsAuthenticated]
    #     return super().get_permissions()
    
    def get_serializer_class(self):
        if not self.request.user.is_authenticated:
            return ArticleNoAuthSerializer
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return ArticleSerializer
    
    def get_queryset(self):
        is_consult_admin = self.request.user.groups.filter(name='EDITOR').exists()
        if is_consult_admin:
            return super().get_queryset()
        return super().get_queryset().filter(status=3)
    
class ArticleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleType.objects.all()
    serializer_class = ArticleTypeSerializer
    
    ordering_fields = ['value']
    ordering = ('value',)
