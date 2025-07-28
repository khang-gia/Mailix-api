from rest_framework import routers
from django.urls import path, include
from system import views

router = routers.SimpleRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'business-units', views.BusinessUnittViewSet)
router.register(r'schedule-events', views.ScheduleEventViewSet)
router.register(r'resources', views.SystemResourceViewSet)
router.register(r'groups', views.SystemGroupViewSet)
urlpatterns = router.urls + [
]