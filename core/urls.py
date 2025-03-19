from rest_framework import routers
from django.urls import path, include
from core import views

# from .views import ProductViewSet
router = routers.SimpleRouter()
# router.register(r'products', ProductViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'system_notifications', views.SystemNotificationViewSet)
router.register(r'happening_events', views.HappeningEventViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'hot_events', views.HotEventViewSet)
router.register(r'profile_hrs', views.ProfileHRViewSet)
urlpatterns = router.urls + [
]