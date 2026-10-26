from rest_framework import routers
from django.urls import path, include
from system import views

router = routers.SimpleRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'business-units', views.BusinessUnittViewSet)
router.register(r'schedule-events', views.ScheduleEventViewSet)
router.register(r'resources', views.SystemResourceViewSet)
router.register(r'groups', views.SystemGroupViewSet)
router.register(r'company', views.CompanyViewSet)
# RBAC Permission Routes
router.register(r'group_resources', views.GroupResourceViewSet)
router.register(r'api_resources', views.ResourceViewSet)
router.register(r'permissions', views.PermissionViewSet)
urlpatterns = router.urls + [
    path('config/', views.system_config, name='system_config'),
    path('admin-config/', views.system_admin_config, name='system_admin_config'),
]