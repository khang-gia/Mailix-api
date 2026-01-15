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
router.register(r'titles', views.TitleViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'customer-attachments', views.CustomerAttachmentViewSet)
router.register(r'work-attachments', views.WorkAttachmentViewSet)
router.register(r'works',views.WorkViewSet)
router.register(r'work_comments',views.WorkCommentViewSet)
router.register(r'customer_comments',views.CustomerCommentViewSet)

urlpatterns = router.urls + [
    path('hrm_statistic/', views.hrm_statistic, name='hrm_statistic'),
]