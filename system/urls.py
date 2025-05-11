from rest_framework import routers
from django.urls import path, include
from system import views

router = routers.SimpleRouter()
router.register(r'departments', views.DepartmentViewSet)
urlpatterns = router.urls + [
]