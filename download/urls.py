from rest_framework import routers
from django.urls import path, include
from upload import views

router = routers.SimpleRouter()
router.register(r'downloads', views.DownloadViewSet)

urlpatterns = router.urls + [
]