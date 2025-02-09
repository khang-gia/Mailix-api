from django.urls import path, include
from rest_framework import routers
from consult import views

router = routers.SimpleRouter()
router.register(r'notifications', views.NotificationViewSet)
router.register(r'articles', views.ArticleViewSet)
router.register(r'article_types', views.ArticleTypeViewSet)

urlpatterns = router.urls + [
  
]